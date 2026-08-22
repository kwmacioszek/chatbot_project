# FAQ Agent

Przykładowy agent FAQ linii lotniczej Example Air, zbudowany na [Pydantic AI](https://ai.pydantic.dev/).
Odpowiada po polsku na podstawie wewnętrznej bazy FAQ (bagaż, check-in, zmiany rezerwacji, zwroty, opóźnienia itd.).

## Wymagania

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- klucz API OpenAI lub Gemini, albo lokalnie uruchomiony LM Studio

## Instalacja

```bash
uv sync
```

## Konfiguracja

Skopiuj plik `.env.example` do `.env` i wybierz provider:

```bash
cp .env.example .env
```

```
# OpenAI
PROVIDER=openai
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini

# Gemini
# PROVIDER=gemini
# GEMINI_API_KEY=...
# MODEL_NAME=gemini-3.5-flash-lite

# LM Studio (uruchom serwer w zakładce Developer)
# PROVIDER=lmstudio
# LMSTUDIO_BASE_URL=http://localhost:1234/v1
# LMSTUDIO_API_KEY=lm-studio
# MODEL_NAME=lmstudio-community/qwen2.5-7b-instruct

LOGFIRE_TOKEN=          # opcjonalnie
```

## Uruchomienie

Interaktywny czat w terminalu:

```bash
uv run faq-agent
```

Wpisz pytanie i naciśnij Enter. Aby zakończyć, wpisz `exit` lub naciśnij Ctrl+C.

```
Example Air FAQ agent — wpisz pytanie (Ctrl+C lub 'exit' aby zakończyć)

Ty: ile kosztuje nadbagaż?
Agent: Nadbagaż kosztuje 50 PLN za każdy rozpoczęty kilogram...
```

Handoff 

```
uv run faq-agent-handoff
```
