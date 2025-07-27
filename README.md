# 🧠 MindMate

A personal AI assistant that helps you stay organized, informed, and in control

---

## 🚀 Features

- 💬 Chat endpoint backed by OpenAI GPT-4o (`responses.create`)
- 🔧 Tool calling support (e.g., fetch latest news)
- 🌐 FastAPI server with auto-reload support via `uvicorn`
- 🔐 Environment config via `.env`
- 🧪 Local development with virtualenv + pyenv

---

## 🛠️ Setup

### 1. Install Python (with OpenSSL)
Make sure your Python is compiled with OpenSSL ≥ 1.1.1. Recommended setup:

```bash
brew install openssl xz
env \
  LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix xz)/lib" \
  CPPFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix xz)/include" \
  PKG_CONFIG_PATH="$(brew --prefix openssl)/lib/pkgconfig:$(brew --prefix xz)/lib/pkgconfig" \
  pyenv install 3.9.18
pyenv local 3.9.18
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file with your OpenAI key:

```
OPENAI_API_KEY=sk-...
```

---

## 🧪 Running the App

Start the local server:

```bash
uvicorn main:app --reload --port 8000
```

Then send a request:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"immi", "message":"What’s the latest on Nvidia?"}'
```

---

## 🧩 Project Structure

```
mindmate/
├── main.py              # FastAPI app with OpenAI integration
├── tools/
│   └── news.py          # Custom tool implementation (e.g., fetch news)
├── requirements.txt     # Python dependencies
├── .venv/               # Virtual environment (not committed)
└── .python-version      # Locked Python version via pyenv
```

---

## 🧼 Notes

- Uses OpenAI's [`responses.create`](https://platform.openai.com/docs/guides/gpt/function-calling) API with function calling
- Output depends on implementation of `get_latest_news()` in `tools/news.py`
- Logging is configured via `logging` module (INFO + DEBUG levels)

---

## ✅ Example Output

```json
{
  "reply": "Here are the latest updates on Nvidia:\n\n1. [Breaking Nvidia News #1](https://example.com/nvidia/1)..."
}
```

---

## 📎 License

Private / Internal Use Only — Immanuel Baur © 2025
