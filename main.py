"""Run the Smart Vacuum desktop application."""


def main() -> None:
    """Launch the Qt desktop application."""
    from src.app.app import main as app_main
    raise SystemExit(app_main())


if __name__ == "__main__":
    main()
