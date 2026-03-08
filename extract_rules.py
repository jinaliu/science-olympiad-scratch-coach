"""Run once to extract rules from the scanned PDF and save to rules.txt."""

import sys
from dotenv import load_dotenv
load_dotenv()

from pdf_parser import read_pdf_as_base64
from agent import extract_rules_from_pdf


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 extract_rules.py path/to/rules.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    print("Reading PDF and sending to Claude (takes ~15 seconds)...")
    pdf_base64 = read_pdf_as_base64(pdf_path)
    rules_text = extract_rules_from_pdf(pdf_base64)

    with open("rules.txt", "w") as f:
        f.write(rules_text)

    print(f"Done! Saved {len(rules_text)} characters to rules.txt")


if __name__ == "__main__":
    main()
