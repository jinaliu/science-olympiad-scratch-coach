# Science Olympiad Game On — Scratch Coach

An AI-powered coaching assistant that guides students step-by-step through building their Science Olympiad "Game On" Scratch game.

## What It Does

- Loads the official Game On rules automatically at startup
- Greets students and summarizes the game requirements
- Coaches students **one step at a time**, waiting for confirmation before moving on
- Answers follow-up questions in simple, kid-friendly language
- Streams responses in real time via a clean chat UI

## Tech Stack

- **Backend:** Python / Flask
- **AI:** Claude Haiku (Anthropic API) with streaming
- **Frontend:** Vanilla JS + SSE (Server-Sent Events)
- **Deployment:** Render.com

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/jinaliu/science-olympiad-scratch-coach.git
cd science-olympiad-scratch-coach

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. (Optional) Pre-extract rules from a PDF
python3 extract_rules.py path/to/rules.pdf

# 6. Run the app
python3 app.py
```

Open `http://localhost:5000` in your browser.

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SECRET_KEY` | Flask session secret (any random string) |

## Deployment (Render.com)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo — Render will detect `render.yaml` automatically
4. Add `ANTHROPIC_API_KEY` under Environment Variables
5. Deploy — your app will be live at `https://science-olympiad-scratch-coach.onrender.com`

## Project Structure

```
science-olympiad-agent/
├── app.py            # Flask routes and session management
├── agent.py          # Claude API calls and system prompt
├── pdf_parser.py     # PDF → base64 utility
├── extract_rules.py  # One-time CLI to pre-extract rules PDF
├── rules.txt         # Pre-extracted rules (loaded at startup)
├── templates/
│   └── index.html    # Chat UI
├── static/
│   └── style.css     # Styles
├── render.yaml       # Render.com deployment config
└── requirements.txt
```
