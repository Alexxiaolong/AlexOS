import httpx

from .config import settings


def normalize_phone(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


async def send_text_to_owner(text: str) -> None:
    """Unico punto del software autorizzato a inviare WhatsApp.

    Il destinatario è forzato nel codice sul numero del proprietario.
    Non accetta un numero come parametro: quindi non può scrivere a clienti,
    fornitori, dipendenti o altri contatti.
    """
    owner = normalize_phone(settings.owner_phone_number)
    url = f"https://graph.facebook.com/v25.0/{settings.meta_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.meta_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": owner,
        "type": "text",
        "text": {"preview_url": False, "body": text[:4000]},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
