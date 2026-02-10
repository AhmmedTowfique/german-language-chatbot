# 🇩🇪 Deutsch Learning Agent

An interactive German language assistant that helps you practice German through conversation. Built with Streamlit and powered by Ollama running Mistral 7B locally — fully containerized with Docker.

---

## What It Does

- Chat with an AI agent that responds only in German
- Corrects your German sentences and explains mistakes
- Teaches vocabulary in context — for example, ask it about the days of the week (Montag, Dienstag, Mittwoch...) and it walks you through them
- Runs entirely locally — no API keys, no cloud costs

---

## Tech Stack

| Component | Tool |
|---|---|
| Frontend | Streamlit |
| LLM | Mistral 7B Instruct (via Ollama) |
| Containerization | Docker, Docker Compose |
| Language | Python |

---

## Getting Started

### Prerequisites
- Docker & Docker Compose installed

### Run

```bash
git clone https://github.com/AhmmedTowfique/deutsch-language-agent.git
cd deutsch-language-agent
docker compose up
```

> On first run, Ollama will download the Mistral 7B model (~4 GB). This may take a few minutes.

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Stop

```bash
docker compose down
```

---

## Why I Built This

I'm learning German and wanted to experiment with running open-source LLMs locally using Ollama. This was a weekend project to combine language learning with hands-on Docker and AI experimentation — not a production app, just a fun side project.

---

## Status

🧪 Experimental — works for basic conversations and vocabulary practice, but not fully polished. Built for learning and tinkering.
