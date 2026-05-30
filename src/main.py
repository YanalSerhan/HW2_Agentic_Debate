"""Entry point (imports SDK, runs CLI)."""

from dotenv import load_dotenv
load_dotenv()

from debate.cli import app

if __name__ == "__main__":
    app()
