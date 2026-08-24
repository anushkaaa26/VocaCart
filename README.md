<div align="center">

# 🛒 VocaCart
### Voice concierge for your pantry

*Speak naturally. VocaCart adds it, remembers it, and watches your budget for you.*

![Python](https://img.shields.io/badge/Python-3.10+-14151A?style=flat-square&logo=python&logoColor=C9A227)
![Streamlit](https://img.shields.io/badge/Streamlit-1.44-14151A?style=flat-square&logo=streamlit&logoColor=C9A227)
![Tests](https://img.shields.io/badge/tests-8%20passing-14151A?style=flat-square&logo=pytest&logoColor=C9A227)
![Voice](https://img.shields.io/badge/voice-Groq%20Whisper-14151A?style=flat-square&logoColor=C9A227)
![License](https://img.shields.io/badge/status-assessment%20build-14151A?style=flat-square&logoColor=C9A227)

**[Live demo →]([#](https://vocacart-cuvuknlmtqj4usxmcpqz9b.streamlit.app/)) &nbsp;·&nbsp; [Setup](#setup) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Feature checklist](#feature-checklist) &nbsp;·&nbsp; [Testing](#testing)**

*[Live](https://vocacart-cuvuknlmtqj4usxmcpqz9b.streamlit.app/)*

</div>

---

## What this is

VocaCart is a voice-first shopping list assistant. You talk to it the way
you'd talk to someone doing the shopping for you — "add two bottles of
milk," "actually make that three," "keep my budget under a hundred dollars,"
"2 litre doodh aur 5 kele add karo" — and it updates a real SQLite-backed
list, tracks a running budget, and learns what you tend to reorder.

It isn't a chatbot wrapped around a to-do list. Every command runs through a
**deterministic parser first** (fast, free, works with zero API calls) with
an **LLM fallback** for phrasing the parser doesn't recognize — so the app
is fully functional offline-of-Groq, and gets more flexible when a
`GROQ_API_KEY` is configured.

## Feature checklist

Mapped against the original assessment brief:

| Requirement | Status | Notes |
|---|:---:|---|
| Voice command recognition | ✅ | Browser mic (`st.audio_input`) → transcription pipeline below |
| Natural language flexibility | ✅ | Rule-based parser handles varied phrasing; LLM fallback for the rest |
| Multilingual voice input | ✅ | English · Hindi · **Hinglish** (code-mixed) — see [`voice.py`](voice.py) |
| Product recommendations | ✅ | `shopping_memory()` flags items you're statistically "due" to reorder |
| Seasonal recommendations | ✅ | `smart_basket()` blends memory + seasonal picks with a stated reason |
| Substitutes | ✅ | `cheaper_substitutes()` — same-category alternatives, cheapest first |
| Add / remove / modify items | ✅ | Including natural corrections: *"actually make that 3"* |
| Auto-categorization | ✅ | Every catalog product carries a category, applied on add |
| Quantity by voice | ✅ | Units parsed too — *"2 bottles of water"*, *"5 kele"* |
| Voice search incl. price range | ✅ | *"find toothpaste under $5"*, rating filters (*"4+ stars"*) |
| Budget tracking | ✅ | **Budget Guardian** — live basket total vs. a spoken budget limit |
| Minimalist, visual-feedback UI | ✅ | Live transcript, spoken + written replies, real-time ledger |
| Loading states | ✅ | Distinct states for transcribing vs. thinking |
| Basic error handling | ✅ | Every voice/LLM call degrades gracefully with a plain-English message |
| Hosting | ✅ | Deploy to Streamlit Community Cloud — see [Deployed](https://vocacart-cuvuknlmtqj4usxmcpqz9b.streamlit.app/) |

## Architecture

```
                    🎙️  Voice (st.audio_input)
                            │
                            ▼
              ┌── voice.py — transcription ──┐
              │  1. Groq Whisper (primary)    │
              │  2. Google/SpeechRecognition  │  ← free fallback, no key needed
              │     (fallback)                │
              └────────────┬───────────────────┘
                            │  transcript text
                            ▼
              ┌── shopping_agent.py ──────────┐
              │  1. deterministic rule parser  │  ← fast, free, always available
              │  2. LLM fallback (Groq)        │  ← only if the rules miss
              └────────────┬───────────────────┘
                            │  {intent, items, filters}
                            ▼
              ┌── database.py ─────────────────┐
              │  shopping_list · purchase_history│
              │  products · reviews · settings   │
              └────────────┬───────────────────┘
                            │
              ┌─────────────┼──────────────────┐
              ▼              ▼                  ▼
      recommendations.py  budget.py        reviews_api.py
      (memory, seasonal,  (Budget          (rating
       substitutes,        Guardian)        aggregation)
       smart basket)
                            │
                            ▼
                    app.py — Streamlit UI
              (voice console · ledger · tabs)
```

Nothing here is faked for the demo: the parser is real regex/heuristics you
can read in `shopping_agent.py`, the recommendation logic runs real SQL
aggregation over `purchase_history` in `recommendations.py`, and the budget
math is a real running total from the live shopping list, not a mock number.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| UI | Streamlit | Fast to build a stateful, reactive interface in pure Python |
| Voice capture | `st.audio_input` | Native browser mic capture, no extra JS |
| Transcription | Groq-hosted Whisper (`whisper-large-v3`), with `SpeechRecognition`'s free Google recognizer as fallback | Whisper is materially more accurate on Hindi/Hinglish; the fallback keeps voice input working with zero setup |
| Intent parsing | Custom rule-based parser + `langchain-groq` LLM fallback | Deterministic path is instant and free; LLM only engages for phrasing the rules don't cover |
| Data | SQLite (`store.db`) | Zero-config, portable, easy to inspect and reset |
| Styling | Hand-written CSS injected via `st.markdown` | A voice console and a receipt ledger aren't native Streamlit components |

## Project structure

```
.
├── app.py                    # Streamlit UI — voice console, ledger, budget panel, tabs
├── shopping_agent.py         # Command parsing (rules + LLM fallback) and response rendering
├── voice.py                  # Audio transcription: Groq Whisper → free-recognizer fallback
├── database.py                # SQLite schema, shopping list, settings, purchase history
├── recommendations.py        # Shopping memory, seasonal picks, substitutes, smart basket
├── budget.py                  # Budget Guardian helpers
├── reviews_api.py             # Rating aggregation (AVG/COUNT over reviews)
├── setup_db.py                 # Schema + seed catalog, idempotent
├── test_core.py                # Unit tests (parser) + integration tests (full pipeline)
├── requirements.txt
└── .streamlit/
    ├── config.toml            # App theme
    └── secrets.toml.example   # Copy to secrets.toml and add your GROQ_API_KEY
```

## Setup

```bash
git clone <your-repo-url>
cd vocacart
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and add your free key from console.groq.com

python setup_db.py               # creates/migrates store.db — safe to re-run
streamlit run app.py
```

The app runs and is fully usable **without** a `GROQ_API_KEY` — the
deterministic parser and the free transcription fallback both work with zero
configuration. The key unlocks the more accurate Whisper transcription and
the LLM fallback for phrasing the rule parser doesn't recognize.

Voice input needs mic access, which browsers only grant on `https://` or
`localhost` — both are covered automatically (local dev, and Streamlit
Community Cloud serves over HTTPS by default).

## Deploying

**Streamlit Community Cloud** (free, and what this stack is built for):

1. Push this repo to GitHub.
2. [share.streamlit.io](https://share.streamlit.io) → New app → point at this repo, branch `main`, file `app.py`.
3. Under **Advanced settings → Secrets**, paste the contents of your local `secrets.toml`:
   ```toml
   GROQ_API_KEY = "your_key_here"
   GROQ_MODEL = "qwen/qwen3-32b"
   ```
4. Deploy, then replace the placeholder link at the top of this README with the live URL.

## Testing

```bash
python -m unittest test_core -v
```

8 tests, two layers:
- **Parser unit tests** — multi-item adds, quantity corrections, budget commands, price/rating search filters, Hinglish parsing.
- **Integration tests** — run `execute_command` end-to-end against the real database (add → remove round trip, rated search results, unknown-command handling), since that's where a change is most likely to break something a parser-only test wouldn't catch.

## Known limitations

- The free transcription fallback (unofficial Google Web Speech endpoint) is rate-limited and weaker on Hindi — configure `GROQ_API_KEY` for a materially better experience.
- Seasonal recommendations use a fixed calendar mapping rather than real sales/weather data.
- "Due for reorder" uses purchase-history intervals per item rather than a learned per-user model.
- Single-session app — the shopping list isn't scoped per user account.

## Approach write-up

See [`WRITEUP.md`](WRITEUP.md) for the ~200-word summary for the submission form.
