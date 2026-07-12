# AlexOS WhatsApp — versione iniziale

Questa versione fa quattro cose:

1. riceve i nuovi messaggi del numero WhatsApp Business tramite webhook;
2. li salva nel database;
3. estrae automaticamente task, note, appuntamenti, follow-up e cose in attesa;
4. può rispondere **soltanto al numero personale del proprietario**.

## Blocco di sicurezza fondamentale

Nel codice non esiste una funzione generica `send_message(numero, testo)`.

Esiste solo `send_text_to_owner(testo)`, che forza sempre il destinatario sul valore
`OWNER_PHONE_NUMBER`. AlexOS non può quindi rispondere a clienti, fornitori,
dipendenti o altri contatti.

## Cosa funziona già

Scrivendo dal numero personale autorizzato al numero WhatsApp Business:

- `Aggiornami`
- `Fammi il resoconto`
- `Cosa ho in sospeso?`

AlexOS restituisce attività aperte, appuntamenti da confermare e cose in attesa.

Un appunto come:

`Ricordami domani di chiamare il tecnico della cella di Rivoli`

viene archiviato e classificato automaticamente.

I messaggi degli altri contatti vengono soltanto letti, salvati e analizzati.
Non ricevono alcuna risposta.

## Installazione locale

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Pubblicazione su Render

1. Crea un repository GitHub e carica tutti i file.
2. Su Render scegli **New > Blueprint** e collega il repository.
3. Render leggerà `render.yaml` e creerà:
   - il servizio web;
   - il database PostgreSQL.
4. Inserisci nelle variabili segrete:
   - `OPENAI_API_KEY`
   - `META_ACCESS_TOKEN`
   - `META_PHONE_NUMBER_ID`
   - `META_VERIFY_TOKEN`
   - `OWNER_PHONE_NUMBER`
5. Dopo il deploy, l'indirizzo webhook sarà:

```text
https://NOME-SERVIZIO.onrender.com/webhook
```

## Collegamento del webhook in Meta

Nella configurazione WhatsApp dell'app Meta:

- **Callback URL:** `https://NOME-SERVIZIO.onrender.com/webhook`
- **Verify token:** lo stesso valore scelto per `META_VERIFY_TOKEN`
- sottoscrivi almeno il campo `messages`.

## Dati Meta già visibili nella configurazione di prova

Inserisci come `META_PHONE_NUMBER_ID` il Phone Number ID mostrato da Meta.

Il token di prova scade. Per l'uso continuativo servirà successivamente un token
permanente tramite utente di sistema e la configurazione del numero di produzione.

## Prossime estensioni

- audio e documenti;
- dashboard per modificare cartelle e stati;
- Google Calendar con conferma esplicita;
- briefing programmati;
- cronologia e ricerca semantica;
- importazione/coexistence del numero WhatsApp Business reale.
