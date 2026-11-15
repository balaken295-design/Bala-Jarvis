"""BALA JARVIS local AI brain, powered by Ollama.

Install Ollama, run: ollama pull qwen2.5:7b
Then install Python dependencies and start jarvis_server.py.
"""
import os
import platform
import shutil
import subprocess
import webbrowser
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import ollama

MODEL = os.getenv("JARVIS_MODEL", "qwen2.5:7b")
NOTES_FILE = Path(__file__).with_name("notes.txt")
OS = platform.system()

SYSTEM_PROMPT = (
    f"You are BALA JARVIS, a concise, friendly personal assistant on the user's {OS} computer. "
    "Use your available tools when the user asks for a supported action. "
    "For normal questions, answer directly. Never claim an action succeeded unless its tool confirms it. "
    "Only open applications from the supported app list. Before saving a note, make sure you have "
    "the note text. Do not ask for passwords, one-time codes, or private credentials. "
    "Keep replies short and use the language the user speaks."
)

# Explicit aliases only: arbitrary shell commands are never passed to the operating system.
APP_ALIASES = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox": "firefox.exe",
}


def get_time() -> str:
    """Get the current date and local time."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")


def system_info() -> str:
    """Get operating system, CPU, RAM and battery status."""
    import psutil
    info = [f"OS: {platform.platform()}",
            f"CPU: {psutil.cpu_percent(interval=0.4)}%",
            f"RAM: {psutil.virtual_memory().percent}% used "
            f"of {psutil.virtual_memory().total // 2**30} GB"]
    battery = psutil.sensors_battery()
    if battery:
        state = "charging" if battery.power_plugged else "on battery"
        info.append(f"Battery: {battery.percent:.0f}% ({state})")
    return "\n".join(info)




def find_windows_browser(executable: str):
    """Find common browser installations even when their folders are not on PATH."""
    candidates = []
    local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    program_files = [os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"),
                     os.environ.get("PROGRAMW6432")]
    if executable == "chrome.exe":
        candidates.extend([local / "Google/Chrome/Application/chrome.exe"])
        for base in program_files:
            if base:
                candidates.append(Path(base) / "Google/Chrome/Application/chrome.exe")
    elif executable == "msedge.exe":
        candidates.append(local / "Microsoft/Edge/Application/msedge.exe")
        for base in program_files:
            if base:
                candidates.append(Path(base) / "Microsoft/Edge/Application/msedge.exe")
    elif executable == "firefox.exe":
        candidates.append(local / "Mozilla Firefox/firefox.exe")
        for base in program_files:
            if base:
                candidates.append(Path(base) / "Mozilla Firefox/firefox.exe")
    try:
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive, rf"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{executable}") as key:
                    value, _ = winreg.QueryValueEx(key, None)
                    candidates.insert(0, Path(value))
            except OSError:
                pass
    except ImportError:
        pass
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def open_app(name: str) -> str:
    """Open a supported desktop app: Chrome, Edge, Firefox, Notepad, Calculator, Paint or File Explorer."""
    key = name.strip().lower()
    executable = APP_ALIASES.get(key)
    if not executable:
        return "That app is not in my safe app list. I can open Chrome, Edge, Firefox, Notepad, Calculator, Paint or File Explorer."
    if OS == "Windows":
        path = shutil.which(executable)
        if not path and executable in {"chrome.exe", "msedge.exe", "firefox.exe"}:
            path = find_windows_browser(executable)
        if path:
            subprocess.Popen([path], shell=False)
        elif key in {"file explorer", "explorer"}:
            subprocess.Popen(["explorer.exe"], shell=False)
        else:
            return f"I couldn't find {name} on this PC. Check that it is installed for this Windows user."
    elif OS == "Darwin":
        mac_names = {"notepad": "TextEdit", "calculator": "Calculator", "calc": "Calculator",
                     "chrome": "Google Chrome", "google chrome": "Google Chrome",
                     "edge": "Microsoft Edge", "microsoft edge": "Microsoft Edge",
                     "firefox": "Firefox"}
        app_name = mac_names.get(key)
        if not app_name:
            return "That app alias is not supported on this Mac."
        subprocess.Popen(["open", "-a", app_name])
    else:
        linux_names = {"notepad": "gedit", "calculator": "gnome-calculator",
                       "calc": "gnome-calculator", "chrome": "google-chrome",
                       "google chrome": "google-chrome", "firefox": "firefox"}
        command = linux_names.get(key)
        path = shutil.which(command) if command else None
        if not path:
            return f"I couldn't find {name} on this computer."
        subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"Launched {name}."


def open_website(url: str) -> str:
    """Open a website in the default browser. Accepts a domain or an http/https URL."""
    candidate = url.strip()
    if not candidate.startswith(("http://", "https://")):
        candidate = "https://" + candidate
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "That doesn't look like a valid website address."
    webbrowser.open(candidate)
    return f"Opened {candidate}."


def web_search(query: str) -> str:
    """Search Google in the default browser for the supplied query."""
    if not query.strip():
        return "Please provide something to search for."
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(query.strip()))
    return f"Opened a Google search for: {query}"


def add_note(text: str) -> str:
    """Save a short note in the local notes.txt file."""
    note = text.strip()
    if not note:
        return "The note was empty, so I did not save it."
    with NOTES_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {note[:2000]}\n")
    return "Note saved."


def read_notes() -> str:
    """Read notes previously saved by BALA JARVIS."""
    if not NOTES_FILE.exists():
        return "No notes yet."
    return NOTES_FILE.read_text(encoding="utf-8")[-4000:]


def list_files(path: str = ".") -> str:
    """List names of files in a folder under the current user's home directory."""
    requested = Path(path).expanduser()
    if not requested.is_absolute():
        requested = Path.home() / requested
    try:
        folder = requested.resolve()
        home = Path.home().resolve()
        if folder != home and home not in folder.parents:
            return "For privacy, I can only list folders inside your user home directory."
        if not folder.is_dir():
            return f"{folder} is not a folder."
        items = sorted(folder.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))[:100]
        return "\n".join(("[dir] " if item.is_dir() else "      ") + item.name for item in items) or "(empty)"
    except OSError as exc:
        return f"I couldn't read that folder: {exc}"


TOOLS = [get_time, system_info, open_app, open_website, web_search,
         add_note, read_notes, list_files]
TOOL_MAP = {tool.__name__: tool for tool in TOOLS}


def chat_turn(messages) -> str:
    """Run one chat turn, handling a limited number of Ollama tool-call rounds."""
    for _ in range(5):
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        messages.append(response.message)
        if not response.message.tool_calls:
            return response.message.content or ""
        for call in response.message.tool_calls:
            name = call.function.name
            args = dict(call.function.arguments or {})
            function = TOOL_MAP.get(name)
            try:
                result = function(**args) if function else f"Unknown tool: {name}"
            except Exception as exc:
                result = f"Tool error: {exc}"
            messages.append({"role": "tool", "tool_name": name, "content": str(result)})
    return "I couldn't complete that request in the available tool steps."


def main():
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    print(f"BALA JARVIS online (local Ollama model: {MODEL}). Type 'exit' to quit.\n")
    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break
        conversation.append({"role": "user", "content": prompt})
        try:
            print("BALA JARVIS:", chat_turn(conversation), "\n")
        except Exception as exc:
            print(f"Error: {exc}\n(Is Ollama running, and did you run 'ollama pull {MODEL}'?)\n")
    print("BALA JARVIS offline.")


if __name__ == "__main__":
    main()
