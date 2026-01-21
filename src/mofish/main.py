"""Main entry point for Mofish client."""

from mofish.app import MofishApp


def main() -> None:
    """Run the Mofish application."""
    app = MofishApp()
    app.run()


if __name__ == "__main__":
    main()
