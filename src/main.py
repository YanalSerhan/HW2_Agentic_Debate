# ruff: noqa: E402
"""Main entry point for the Debate Agent."""

from dotenv import load_dotenv

load_dotenv()

import sys

from debate.cli import app
from debate.menu import run_menu

if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            run_menu()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
    else:
        app()
