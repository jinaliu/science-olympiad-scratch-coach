"""Flask web app for Science Olympiad Game On Scratch Assistant."""

import os
import uuid
import json
import tempfile
from typing import Any

from flask import (
    Flask,
    Response,
    request,
    render_template,
    session,
    jsonify,
    stream_with_context,
)
from dotenv import load_dotenv

from pdf_parser import read_pdf_as_base64
from agent import stream_chat, extract_rules_from_pdf

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

# Load pre-extracted rules at startup if available
_RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.txt")
_DEFAULT_RULES: str | None = None
if os.path.exists(_RULES_FILE):
    with open(_RULES_FILE) as f:
        _DEFAULT_RULES = f.read()
    print(f"Loaded rules.txt ({len(_DEFAULT_RULES)} chars)")

# In-memory store: session_id -> {rules_text, messages}
_store: dict[str, dict[str, Any]] = {}


def get_store() -> dict[str, Any]:
    """Get or create the current session's data store."""
    sid = session.get("id")
    if not sid or sid not in _store:
        sid = str(uuid.uuid4())
        session["id"] = sid
        _store[sid] = {"rules_text": _DEFAULT_RULES, "messages": []}
    return _store[sid]


@app.route("/")
def index() -> str:
    """Render the main chat page."""
    get_store()  # ensure session exists
    return render_template("index.html", rules_preloaded=_DEFAULT_RULES is not None)


@app.route("/upload", methods=["POST"])
def upload_pdf() -> Response:
    """Handle PDF upload and extract rules text."""
    if "pdf" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    pdf_file = request.files["pdf"]
    if pdf_file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file."}), 400

    # Save to a temp file, encode as base64, then use Claude vision to extract text
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        pdf_base64 = read_pdf_as_base64(tmp_path)
        rules_text = extract_rules_from_pdf(pdf_base64)
    finally:
        os.unlink(tmp_path)

    if not rules_text.strip():
        return jsonify({"error": "Could not extract text from the PDF."}), 400

    store = get_store()
    store["rules_text"] = rules_text
    store["messages"] = []  # reset conversation on new upload

    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat() -> Response:
    """Handle a chat message and stream the response via SSE."""
    store = get_store()

    if not store["rules_text"]:
        return jsonify({"error": "Please upload the rules PDF first!"}), 400

    data = request.get_json()
    user_message: str = (data or {}).get("message", "").strip()
    image_base64: str | None = (data or {}).get("image_base64")
    image_type: str | None = (data or {}).get("image_type")

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Add user message to history (store plain text; image is sent to API only)
    store["messages"].append({"role": "user", "content": user_message})

    def generate():
        """SSE generator — yields chunks and then the [DONE] sentinel."""
        full_response: list[str] = []
        try:
            for chunk in stream_chat(store["messages"], store["rules_text"], image_base64, image_type):
                full_response.append(chunk)
                # SSE format: "data: <payload>\n\n"
                payload = json.dumps({"text": chunk})
                yield f"data: {payload}\n\n"
        except Exception as exc:
            err_payload = json.dumps({"error": str(exc)})
            yield f"data: {err_payload}\n\n"
        else:
            # Save assistant response to history
            store["messages"].append(
                {"role": "assistant", "content": "".join(full_response)}
            )
        finally:
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering on Render
        },
    )


@app.route("/reset", methods=["POST"])
def reset() -> Response:
    """Clear the conversation history (keep rules)."""
    store = get_store()
    store["messages"] = []
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
