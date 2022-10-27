"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Fact Check Okinawa Vote Cheating."""


if __name__ == "__main__":
    main(prog_name="fact-check-okinawa-vote-cheating")  # pragma: no cover
