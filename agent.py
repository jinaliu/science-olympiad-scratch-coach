"""Claude API agent for Science Olympiad Game On Scratch guidance."""

import anthropic
from typing import Generator

client = anthropic.Anthropic()


def extract_rules_from_pdf(pdf_base64: str) -> str:
    """Use Claude vision to extract text from a scanned rules PDF.

    Args:
        pdf_base64: Base64-encoded PDF content.

    Returns:
        Extracted rules text.
    """
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_base64,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "Please extract and transcribe ALL the text from this "
                        "Science Olympiad rules document. Include every rule, "
                        "scoring guideline, and requirement. Be thorough and complete."
                    ),
                },
            ],
        }],
    )
    return response.content[0].text

SYSTEM_PROMPT = """You are a friendly, encouraging Science Olympiad coach helping a student build a "Game On" Scratch game. You have access to the official rules PDF for the event.

Your job is to:
1. Read through the rules carefully and understand all requirements
2. Break down the Scratch game build into clear, numbered steps a middle or high school student can follow
3. Answer follow-up questions patiently and clearly
4. Use simple, kid-friendly language
5. Reference specific rule numbers or sections when relevant
6. Celebrate progress and keep the student motivated!

When the student first uploads the rules, immediately:
- Summarize the key game requirements in plain English
- List the scoring categories
- Give them a numbered build plan (Step 1, Step 2, etc.) for creating the Scratch game

Keep responses focused, friendly, and actionable. Use emojis occasionally to keep it fun!"""


def build_system_with_rules(rules_text: str) -> str:
    """Build the full system prompt with the rules embedded.

    Args:
        rules_text: Extracted text from the rules PDF.

    Returns:
        Complete system prompt string.
    """
    return f"""{SYSTEM_PROMPT}

---
OFFICIAL GAME ON RULES:
{rules_text}
---"""


def stream_chat(
    messages: list[dict],
    rules_text: str,
) -> Generator[str, None, None]:
    """Stream a chat response from Claude.

    Args:
        messages: Conversation history in Claude message format.
        rules_text: Extracted rules text from the uploaded PDF.

    Yields:
        Text chunks as they stream from the API.
    """
    system = build_system_with_rules(rules_text)

    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=2048,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
