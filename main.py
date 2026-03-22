#!/usr/bin/env python3
"""Main entry point for Recap CLI."""

import sys
from cli import RecapCLI


def main():
    """Run the CLI application."""
    cli = RecapCLI()
    exit_code = cli.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
