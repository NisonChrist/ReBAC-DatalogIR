"""DatalogIR syntax checker — CLI entry point."""

import sys
from pathlib import Path

from src import check_syntax, LexerError, SyntaxError


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.dlir>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    source = filepath.read_text()

    try:
        program = check_syntax(source)
    except (LexerError, SyntaxError) as e:
        print(f"✗ {e}")
        sys.exit(1)

    n = len(program.clauses)
    print(f"✓ Syntax OK — {n} clause{'s' if n != 1 else ''} parsed")
    for clause in program.clauses:
        print(f"  {clause!r}")


if __name__ == "__main__":
    main()
