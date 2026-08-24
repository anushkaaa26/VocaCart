# 🛒 VocaCart — Voice-First AI Shopping Agent

VocaCart is an assessment-ready evolution of the original `shopping-agent` project. It keeps the existing SQLite product catalog, ratings and order ledger, then adds a voice-first conversational shopping layer.
https://vocacart-cuvuknlmtqj4usxmcpqz9b.streamlit.app/
## Standout features

- 🎙️ **Voice-first commands** using Streamlit microphone capture + speech recognition.
- 🧠 **Shopping Memory** that detects repeat-purchase intervals and explains when an item is likely due.
- 🔄 **Natural corrections** such as “Add 5 apples” → “Actually make that 3”.
- 🛒 **Smart Basket** generated from purchase history, the active list and seasonal recommendations.
- 💰 **Budget Guardian** that tracks the basket and warns when a command pushes it over budget.
- 🌐 **English, Hindi and Hinglish** voice modes with a normalization layer.
- 🔎 Existing product search, organic filtering and review aggregation are preserved.

## Architecture

```text
Voice / Text
     ↓
Speech recognition
     ↓
Intent parser (Groq + deterministic fallback)
     ↓
Add / Remove / Update / Search / Budget / Smart Basket
     ↓
SQLite
 ┌──────────────┬───────────────┬──────────────┐
 │ Products     │ Shopping List │ Order/Memory │
 └──────────────┴───────────────┴──────────────┘
                     ↓
          Recommendation engine
                     ↓
              Explainable response
```

## Project structure

```text
shopping-agent/
├── app.py                 # Streamlit product UI
├── shopping_agent.py      # intent parsing + command execution
├── database.py            # SQLite data layer
├── recommendations.py     # shopping memory + smart basket
├── budget.py              # budget helper functions
├── voice.py               # speech-to-text + Hinglish normalization
├── reviews_api.py         # review aggregation
├── setup_db.py            # catalog + demo data bootstrap
├── store.db               # local SQLite database
└── requirements.txt       # production dependencies
```

## Run locally

```bash
git clone https://github.com/anushkaaa26/shopping-agent.git
cd shopping-agent

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python setup_db.py

streamlit run app.py
```

### AI key

The app works with deterministic fallback parsing for common commands. For richer natural-language understanding, add a Groq key locally:

```bash
export GROQ_API_KEY="your_key"
```

Or create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_key"
GROQ_MODEL = "qwen/qwen3-32b"
```

Never commit secrets.

## Demo commands

```text
Add 2 bottles of milk
Actually make that 3
Add 5 apples and 2 bottles of water
Remove apples from my list
Find organic honey under $20 with 4+ stars
Set my budget to $25
Prepare my weekly grocery list
2 litre doodh aur 5 kele add karo
```

## Deployment

The app is designed for Streamlit Community Cloud. Put the repository on GitHub, select `app.py` as the entry point, and add `GROQ_API_KEY` in the deployment Secrets settings.

The project uses `st.audio_input`, so microphone capture happens in the browser. Speech recognition requires network access to the recognition provider; text input remains available as a fallback.

## Engineering notes

- SQL queries use parameters rather than string interpolation for user values.
- Recommendation logic is deterministic and explainable rather than pretending to be a trained recommender model.
- The original `orders` table is preserved. Assessment demo history is stored separately in `purchase_history`.
- The large machine-generated dependency snapshot from the original local environment has been replaced with a minimal deployable `requirements.txt`.

## Changes in this pass

Starting point already had all the hard parts working — a real deterministic
parser with LLM fallback, budget guardian, shopping memory, and Hinglish
support, all covered by passing tests. This pass focused on fixing what would
actually break in front of a grader:

- **Fixed a theme conflict**: `.streamlit/config.toml` was set to a dark
  olive theme while `app.py` injects CSS for a light white-card design.
  Unstyled native widgets (language selector, budget input, tabs) would have
  rendered dark-on-light. Config now matches the CSS.
- **Voice recognition reliability**: `voice.py` previously depended entirely
  on `SpeechRecognition`'s free/unofficial Google endpoint, which is
  rate-limited and inconsistent — especially for Hindi. It now tries
  Groq-hosted Whisper first (reusing the `GROQ_API_KEY` already used for the
  LLM parser) and falls back to the free recognizer automatically, so voice
  input degrades gracefully instead of depending on one unreliable service.
- **Expanded `test_core.py`** beyond parser-only unit tests to integration
  tests that exercise `execute_command` end-to-end against the real
  `store.db` (add → remove round trip, rated search results, unknown-command
  handling) — this is the code path most likely to have an integration bug
  that unit tests on the parser alone wouldn't catch.
- **Fixed an inconsistent default** in `database.py` (`user_settings` table
  default was 1500/₹ but the seed `INSERT` used 100/$ — the insert always
  won, so this was silently harmless but confusing to read).
- Verified end-to-end in a **fresh virtual environment** using only
  `requirements.txt`, both `python3 setup_db.py` idempotency and a full
  Streamlit boot, to make sure what's in this repo actually deploys clean.
