"""Local Ollama conversation engine for BALA JARVIS."""
import os
import ollama

MODEL = os.getenv("JARVIS_MODEL", "qwen2.5:7b")
SYSTEM_PROMPT = """You are BALA JARVIS, a helpful personal desktop assistant.
Be concise, practical, and friendly. You can answer questions and explain tasks.
Never claim you performed a computer action unless the application actually did it.
Never request passwords, one-time codes, or private credentials.
"""

def chat_turn(messages):
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        options={"temperature": 0.5},
    )
    return response["message"]["content"].strip()
