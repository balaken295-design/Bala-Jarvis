"""Local Ollama conversation engine."""
import os
import ollama
MODEL=os.getenv("JARVIS_MODEL","qwen2.5:7b")
SYSTEM_PROMPT="""You are BALA JARVIS, a concise and helpful personal assistant. Be honest about what you can and cannot do. Never claim to have performed an action unless a tool did it. Do not ask for passwords or private authentication codes. Reply in the user's language."""
def chat_turn(messages):
    result=ollama.chat(model=MODEL,messages=messages,options={"temperature":0.5})
    return result["message"]["content"].strip()
