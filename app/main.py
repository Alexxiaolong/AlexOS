import logging

from fastapi import FastAPI, HTTPException, Query, Request
from sqlalchemy import select

from .ai import extract_items
from .briefing import build_briefing
from .config import settings
from .db import Base, SessionLocal, engine
from .meta import normalize_phone, send_text_to_owner
from .models import Item, Message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alexos")

app = FastAPI(title="AlexOS WhatsApp", version="0.1.0")
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "outbound_policy": "owner_only"}


@app.get("/webhook")
def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge
    raise HTTPException(status_code=403, detail="Verifica webhook non valida")


@app.post("/webhook")
async def receive_webhook(request: Request) -> dict:
    payload = await request.json()

    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                contacts = value.get("contacts", [])
                profile_name = None
                if contacts:
                    profile_name = contacts[0].get("profile", {}).get("name")

                for incoming in value.get("messages", []):
                    if incoming.get("type") != "text":
                        continue

                    wa_id = incoming.get("id")
                    sender = normalize_phone(incoming.get("from", ""))
                    text = incoming.get("text", {}).get("body", "").strip()
                    if not wa_id or not sender or not text:
                        continue

                    with SessionLocal() as db:
                        exists = db.scalar(
                            select(Message).where(Message.whatsapp_message_id == wa_id)
                        )
                        if exists:
                            continue

                        is_owner = sender == normalize_phone(settings.owner_phone_number)
                        message = Message(
                            whatsapp_message_id=wa_id,
                            sender_phone=sender,
                            sender_name=profile_name,
                            text=text,
                            is_owner=is_owner,
                        )
                        db.add(message)
                        db.flush()

                        try:
                            extracted = extract_items(text, profile_name, is_owner)
                        except Exception:
                            logger.exception("Classificazione OpenAI fallita")
                            extracted = []

                        for data in extracted:
                            db.add(
                                Item(
                                    source_message_id=message.id,
                                    folder=data.get("folder") or "Da classificare",
                                    item_type=data.get("item_type") or "nota",
                                    title=data.get("title") or text[:280],
                                    details=data.get("details"),
                                    priority=data.get("priority") or "media",
                                    due_at=data.get("due_at"),
                                    waiting_for=data.get("waiting_for"),
                                    calendar_candidate=bool(data.get("calendar_candidate")),
                                )
                            )
                        db.commit()

                        # Il sistema risponde esclusivamente al proprietario.
                        # Nessun ramo del codice invia messaggi a contatti terzi.
                        if is_owner:
                            lowered = text.lower().strip()
                            if any(cmd in lowered for cmd in [
                                "aggiornami",
                                "fammi il resoconto",
                                "cosa ho in sospeso",
                                "cose aperte",
                                "briefing",
                            ]):
                                reply = build_briefing(db)
                            elif extracted:
                                labels = ", ".join(
                                    f"{x.get('item_type', 'nota')} in {x.get('folder', 'Da classificare')}"
                                    for x in extracted[:3]
                                )
                                reply = f"Registrato: {labels}."
                            else:
                                reply = "Ricevuto e archiviato."

                            await send_text_to_owner(reply)

    except Exception:
        logger.exception("Errore durante la gestione del webhook")
        # Meta deve ricevere comunque 200 per evitare retry incontrollati.
        return {"status": "accepted_with_error"}

    return {"status": "accepted"}
