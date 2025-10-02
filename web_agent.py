import streamlit as st
import re
import requests
import os
import json

# ------------------ AGENT CLASS ------------------
class DeutschAgent:
    def __init__(self, model="mistral:7b-instruct", max_history=8):
        self.model = model
        self.max_history = max_history
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        if "history" not in st.session_state:
            st.session_state.history = []
        if "msg_counter" not in st.session_state:
            st.session_state.msg_counter = 0

    # ---------- Call Ollama (HTTP) ----------
    def call_ollama(self, prompt: str) -> str:
        """Call Ollama via REST API instead of subprocess."""
        url = f"{self.ollama_host}/api/generate"
        try:
            response = requests.post(
                url,
                json={"model": self.model, "prompt": prompt},
                stream=True,
                timeout=120
            )
            response.raise_for_status()

            output = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        output += data["response"]
            return output.strip()

        except Exception as e:
            print("Error calling Ollama:", e)
            return "Fehler: Konnte Ollama nicht erreichen."

    # ---------- Prompt builder ----------
    def build_prompt(self, history, user_input: str) -> str:
        history_text = "\n".join(
            [f"Du: {h['user']}\nAgent: {h['bot']}" for h in history[-self.max_history:]]
        )
        return f"""
Du bist mein persönlicher Deutschlehrer.

WICHTIG: Antworte **AUSSCHLIESSLICH auf Deutsch**.
Format **IMMER GENAU SO**:

KORREKTUR: <korrigierter Satz>
ERKLÄRUNG: <kurze Erklärung auf Deutsch>
ANTWORT: <nächste sinnvolle Antwort oder Frage>

Beispiel:
Du: i möchte deutsch lernen
Agent:
KORREKTUR: Ich möchte Deutsch lernen.
ERKLÄRUNG: Großschreibung von "Ich" und "Deutsch".
ANTWORT: Super! Warum möchtest du Deutsch lernen?

---
Bisherige Unterhaltung:
{history_text if history_text else "(keine)"}

Neue Nachricht vom Nutzer:
{user_input}

Bitte antworte jetzt:
"""

    # ---------- Parser ----------
    def parse_reply(self, raw: str) -> dict:
        result = {"KORREKTUR": "", "ERKLÄRUNG": "", "ANTWORT": ""}
        patterns = {
            "KORREKTUR": r"KORREKTUR\s*:\s*(.*?)(?=ERKLÄRUNG:|ANTWORT:|$)",
            "ERKLÄRUNG": r"ERKLÄRUNG\s*:\s*(.*?)(?=KORREKTUR:|ANTWORT:|$)",
            "ANTWORT":   r"ANTWORT\s*:\s*(.*)$"
        }
        for key, pat in patterns.items():
            m = re.search(pat, raw, re.S | re.I)
            if m:
                result[key] = m.group(1).strip()
        if not any(result.values()):
            result["ANTWORT"] = raw.strip()
        return result

    # ---------- Conversation update ----------
    def add_turn(self, user_input: str):
        prompt = self.build_prompt(st.session_state.history, user_input)
        raw = self.call_ollama(prompt)
        parsed = self.parse_reply(raw)
        st.session_state.history.append({
            "user": user_input.strip(),
            "korrektur": parsed.get("KORREKTUR", ""),
            "erklaerung": parsed.get("ERKLÄRUNG", ""),
            "bot": parsed.get("ANTWORT", "")
        })
        st.session_state.msg_counter += 1
        return raw  # also return raw for debugging
# ------------------ END CLASS ------------------

# ------------------ STREAMLIT APP ------------------
st.set_page_config(page_title="Deutsch Agent", page_icon="🇩🇪")
st.title("🇩🇪 Dein Deutsch-Lern-Agent (Local)")

agent = DeutschAgent(model="mistral:7b-instruct")

# Show history
for h in st.session_state.history:
    st.markdown(f"**Du:** {h['user']}")
    if h.get("korrektur"):
        st.markdown(f"✏️ **Korrektur:** {h['korrektur']}")
    if h.get("erklaerung"):
        st.caption(f"ℹ️ {h['erklaerung']}")
    st.markdown(f"🤖 **Agent:** {h['bot']}")
    st.divider()

# Input box
user_input = st.text_input(
    "Deine Nachricht:",
    key=f"input_{st.session_state.msg_counter}"
)

col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("Senden"):
        if user_input.strip():
            raw = agent.add_turn(user_input.strip())
            st.rerun()

with col2:
    if st.button("Neues Gespräch"):
        st.session_state.history = []
        st.session_state.msg_counter = 0
        st.rerun()

with col3:
    if st.button("🔍 Debug Roh-Ausgabe"):
        if st.session_state.history:
            st.code(agent.call_ollama(
                agent.build_prompt(st.session_state.history[:-1],
                st.session_state.history[-1]["user"])
            ), language="text")
