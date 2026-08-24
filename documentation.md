# Approach

VocaCart is parser-first, LLM-second. Every command runs through a
deterministic rule parser (`shopping_agent.py`) handling multi-item adds,
quantity corrections ("actually make that 3"), budget commands, price/rating
filters, and Hinglish — instant, free, and unit tested. An LLM (Groq)
engages only as a fallback for phrasing the rules miss, so the app works
with zero API calls and gets more flexible once a key is configured.

Voice transcription follows the same pattern: Groq-hosted Whisper is tried
first for accuracy (especially Hindi/Hinglish), falling back automatically
to `SpeechRecognition`'s free Google recognizer if no key is set or the call
fails — voice input never hard-depends on a paid service.

Smart suggestions come from real SQL aggregation over purchase history in
`recommendations.py`: `shopping_memory()` computes each item's average
reorder interval and flags what's statistically due, `smart_basket()`
blends that with seasonal picks and states its reasoning, and
`cheaper_substitutes()` ranks same-category alternatives for Budget Guardian
when a basket exceeds its spoken limit.

The interface treats voice as the primary surface, not a bolt-on mic button:
a console dial is the hero, the list renders as a receipt ledger with real
per-item pricing, and every reply is both spoken and shown as text with a
visible transcript, so the loop stays legible off-mic too.
