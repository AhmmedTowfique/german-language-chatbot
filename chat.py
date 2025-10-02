# web_agent.py
import streamlit as st
import subprocess
import re

# ---------- CONFIG ----------
MODEL = "mistral:7b"   # change to your local model (e.g. "gemma:7b" or "mistral:7b")
MAX_HISTORY_TURNS = 8

# ---------- CALL OLLAMA ----------
def call_ollama(prompt: str) -> str:
    """Call local Ollama model via stdin and return its raw text reply."""
    proc = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=60  # avoid hanging forever
    )
    # return stdout even if stderr has warnings
    return proc.stdout.strip()

# ---------- PROMPT WITH FEW-SHOT ----------
def build_prompt(history, user_input):
    history_text = ""
    for turn in history[-MAX_HISTORY_TURNS:]:
        history_text += f"Du: {turn['user']}\nAgent: {turn.get('bot','')}\n"

    # Strong, strict instructions + few-shot examples
    prompt = f"""
Du bist ein geduldiger Deutschlehrer und Sprachpartner.
WICHTIG: Antworte AUSSCHLIESSLICH auf Deutsch. Verwende kein Englisch.
ANTWORTFORMAT (genau so, ohne zusätzlichen Text):
KORREKTUR: <korrigierter Satz>
ERKLÄRUNG: <sehr kurze Erklärung, 1 Satz, einfach>
ANTWORT: <eine natürliche Fortsetzung oder Frage, 1-2 Sätze>

Regeln:
- Wenn der Satz korrekt ist, setze KORREKTUR identisch und ERKLÄRUNG = "Keine Änderung nötig."
- KORREKTUR soll vollständigen, grammatisch korrekten Satz enthalten (Groß-/Kleinschreibung).
- Keine Einleitungen wie "Hier ist..." oder "Guten Tag" extra — nur die drei Felder.
- Wenn die Frage verlangt, gib in ANTWORT konkrete Listen / Beispiele (kurz).

Beispiele (EIN HALT: die Antwort MUSS genau dieses Format haben):

Beispiel 1:
Nutzer: sagst du mir seven tages name
KORREKTUR: Sagst du mir die sieben Tagesnamen?
ERKLÄRUNG: "seven" ist Englisch; auf Deutsch heißt es "sieben".
ANTWORT: Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag.

Beispiel 2:
Nutzer: i möchte deutsch lernen
KORREKTUR: Ich möchte Deutsch lernen.
ERKLÄRUNG: Großschreibung von "Ich" und "Deutsch".
ANTWORT: Sehr gut! Warum möchtest du Deutsch lernen?

Beispiel 3:
Nutzer: Guten Tag
KORREKTUR: Guten Tag.
ERKLÄRUNG: Keine Änderung nötig.
ANTWORT: Guten Tag! Wie geht es dir?

Jetzt das Gespräch (nur der Verlauf, dann die neue Nachricht):
GESPRÄCHSVERLAUF:
{history_text if history_text else "(keine)"}

NEUE NACHRICHT:
{user_input}

ANTWORT:
"""
    return prompt

# ---------- PARSE MODEL OUTPUT ----------
label_pattern = {
    "KORREKTUR": re.compile(r"KORREKTUR\s*:\s*(.*?)\s*(?=ERKLÄRUNG\s*:|ANTWORT\s*:|$)", re.S | re.I),
    "ERKLÄRUNG": re.compile(r"ERKLÄRUNG\s*:\s*(.*?)\s*(?=KORREKTUR\s*:|ANTWORT\s*:|$)", re.S | re.I),
    "ANTWORT": re.compile(r"ANTWORT\s*:\s*(.*?)\s*$", re.S | re.I),
}

def parse_structured_reply(text: str) -> dict:
    """Extract KORREKTUR/ERKLÄRUNG/ANTWORT robustly; fallback to putting everything in ANTWORT."""
    res = {"KORREKTUR": "", "ERKLÄRUNG": "", "ANTWORT": ""}
    for k, pat in label_pattern.items():
        m = pat.search(text)
        if m:
            res[k] = m.group(1).strip()
    # fallback: if no labels found, put full text into ANTWORT
    if not any(res.values()):
        res["ANTWORT"] = text.strip()
    return res

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Deutsch Agent", page_icon="🇩🇪")
st.title("🇩🇪 Dein Deutsch-Lern-Agent (Local)")
st.write("The model will correct your German in the format: KORREKTUR / ERKLÄRUNG / ANTWORT")

if "history" not in st.session_state:
    st.session_state.history = []
if "msg_counter" not in st.session_state:
    st.session_state.msg_counter = 0

# Conversation display
for turn in st.session_state.history:
    st.markdown(f"**Du:** {turn['user']}")
    if turn.get("korrektur"):
        st.markdown(f"**Korrektur:** {turn['korrektur']}")
    if turn.get("erklaerung"):
        st.caption(f"**Erklärung:** {turn['erklaerung']}")
    st.markdown(f"**Agent:** {turn['bot']}")
    st.divider()

# Input (unique key each send so it resets)
user_input = st.text_input("Deine Nachricht:", key=f"input_{st.session_state.msg_counter}")

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Senden"):
        if user_input.strip():
            prompt = build_prompt(st.session_state.history, user_input.strip())

            # Call model and capture raw for debugging
            raw = call_ollama(prompt)

            parsed = parse_structured_reply(raw)

            st.session_state.history.append({
                "user": user_input.strip(),
                "korrektur": parsed.get("KORREKTUR",""),
                "erklaerung": parsed.get("ERKLÄRUNG",""),
                "bot": parsed.get("ANTWORT","")
            })

            st.session_state.msg_counter += 1
            st.rerun()

with col2:
    if st.button("Neues Gespräch"):
        st.session_state.history = []
        st.session_state.msg_counter = 0
        st.rerun()

# Show raw model output for debugging (helpful if model still misbehaves)
if st.button("Zeige Roh-Antwort (Debug)"):
    if st.session_state.history:
        last_prompt = build_prompt(st.session_state.history[:-1], st.session_state.history[-1]["user"])
        raw_out = call_ollama(last_prompt)
        st.expander("Raw model output").write(raw_out)
    else:
        st.info("Noch kein Verlauf vorhanden.")
