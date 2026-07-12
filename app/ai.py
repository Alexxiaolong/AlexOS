import json
from datetime import datetime
from zoneinfo import ZoneInfo

from openai import OpenAI

from .config import settings


client = OpenAI(api_key=settings.openai_api_key)

SYSTEM = """
Sei il motore di organizzazione di AlexOS, assistente personale di un imprenditore
della ristorazione. Devi trasformare un messaggio in zero o più elementi operativi.

Cartelle suggerite:
Kensho, Revolution Ramen, Sushi Koi, Donburi House, La Bottega di Gio,
Personale e dipendenti, Fornitori, Banche e commercialista, Progetti,
Famiglia, Salute e palestra, Auto, Casa, Viaggi, Acquisti, Personale,
Da classificare.

Tipi consentiti:
task, promemoria, appuntamento, idea, decisione, follow_up, nota, attesa.

Regole:
- Non inventare scadenze.
- Se qualcuno deve fare qualcosa per Alex, usa tipo 'attesa' e valorizza waiting_for.
- Una proposta con giorno/ora è calendar_candidate=true, ma non è confermata.
- Se è solo conversazione senza azione o informazione utile, restituisci items vuoto.
- Priorità: bassa, media, alta, urgente.
- Restituisci esclusivamente JSON valido.
"""


def extract_items(text: str, sender_name: str | None, is_owner: bool) -> list[dict]:
    now = datetime.now(ZoneInfo("Europe/Rome")).isoformat()
    prompt = {
        "current_datetime_europe_rome": now,
        "sender_name": sender_name,
        "message_is_from_owner": is_owner,
        "message": text,
        "output_schema": {
            "items": [
                {
                    "folder": "string",
                    "item_type": "task|promemoria|appuntamento|idea|decisione|follow_up|nota|attesa",
                    "title": "string",
                    "details": "string|null",
                    "priority": "bassa|media|alta|urgente",
                    "due_at": "ISO datetime/date or natural expression or null",
                    "waiting_for": "string|null",
                    "calendar_candidate": "boolean"
                }
            ]
        }
    }

    response = client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM,
        input=json.dumps(prompt, ensure_ascii=False),
    )
    raw = response.output_text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()
    data = json.loads(raw)
    return data.get("items", [])
