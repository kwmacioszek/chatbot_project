# FAQ Agent

Przykładowy agent FAQ linii lotniczej Example Air, zbudowany na [Pydantic AI](https://ai.pydantic.dev/).
Odpowiada po polsku na podstawie wewnętrznej bazy FAQ (bagaż, check-in, zmiany rezerwacji, zwroty, opóźnienia itd.).

## Wymagania

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- klucz API OpenAI

## Instalacja

```bash
uv sync
```

## Konfiguracja

Skopiuj plik `.env.example` do `.env` i uzupełnij klucz API:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini
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
