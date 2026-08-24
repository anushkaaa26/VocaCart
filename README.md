# 🛒 VocaCart — Voice Command Shopping Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vocacart-cuvuknlmtqj4usxmcpqz9b.streamlit.app/)
![Python Version](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live%20Production-success)
![UI/UX](https://img.shields.io/badge/Interface-Minimalist%20%26%20Responsive-purple)

> **Live Demo:** 🚀 [Experience VocaCart Live on Streamlit Cloud](https://vocacart-cuvuknlmtqj4usxmcpqz9b.streamlit.app/)

**VocaCart** is an intelligent, voice-activated shopping management system designed for friction-free inventory control, hands-free product discovery, and automated budget optimization. Built using Python, Streamlit, and modern browser speech recognition APIs, VocaCart parses continuous audio input into structured transactional data in real time.

---

## 🌟 Key Features

| Feature | Capabilities | Implementation |
| :--- | :--- | :--- |
| **🎙️ Voice Recognition** | Multi-phrase intent detection, Hands-free cart control | Web Speech API & JavaScript SpeechRecognition wrapper |
| **🌐 Multilingual Support** | Accent-tolerant voice parsing across English, Spanish, French, German | Dynamic speech locale parameters (`en-US`, `es-ES`, `fr-FR`, `de-DE`) |
| **🤖 Smart Recommendations** | Automated dietary substitutions (e.g., Oat Milk for Milk), seasonal suggestions, stock alerts | Rule-based decision heuristics & preference matrix |
| **🏷️ Automated Taxonomy** | Instant auto-categorization (Dairy, Produce, Snacks, Household) | Fuzzy keyword pattern matching & NLP categorization |
| **💰 Budget & Price Filter** | Real-time expense computation, voice-based range filtering (*"find items under $10"*) | Defensive regex entity extraction & status calculators |
| **📦 Order Lifecycle** | Full multi-page experience: Catalog ➔ Cart ➔ Checkout ➔ Receipts | Session-state state engine with defensive error handling |

---

## 🏗️ Architecture & Data Flow

```text
[ User Voice Input ] 
       │
       ▼
[ Web Speech API (Client STT) ]
       │
       ▼
[ NLP & Intent Parsing Engine ] ──► (Action: Add / Remove / Filter / Search)
       │
       ▼
[ State Manager & Budget Calculator ] ──► (Categorization, Substitutions, Status)
       │
       ▼
[ Reactive Streamlit UI Engine ] ──► (Catalog | Cart | Checkout | Order History)
