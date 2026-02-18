from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Union

"""
a ∈ Const
X ∈ Var
p ∈ PredicateSym
t ∈ Term ::= a | X
A ∈ Atom ::= p | p(t, ..., t)
φ ∈ Premise ::= A | not A | t = t | t != t
C ∈ Clause ::= A. | A :- φ, ..., φ.

a 属于常量集
X 属于变量集
p 属于谓词符号集
t 属于项集，定义为：t 等于 a 或 X
A 属于原子公式集，定义为：A 等于 p，或 A 等于 p(t, ..., t)
φ 属于前提集，定义为：φ 等于 A、非 A、t = t 或 t ≠ t
C 属于子句集，定义为：C 等于 A.（事实），或 C 等于 A :- φ, ..., φ.（规则）

a ∈ 常量
X ∈ 变量
p ∈ 谓词符号
t ∈ 项 ::= a | X
A ∈ 原子 ::= p | p(t, ..., t)
φ ∈ 前提 ::= A | 非A | t = t | t != t
C ∈ 子句 ::= A. | A :- φ, ..., φ.
"""


# ──────────────────────────────────────────────
#  Tokens
# ──────────────────────────────────────────────


class DatalogIRToken(Enum):
    """Token types produced by the DatalogIR lexer."""

    # Identifiers & literals
    IDENT_LOWER = auto()  # lowercase id: constant / predicate symbol
    IDENT_UPPER = auto()  # uppercase id: variable
    WILDCARD = auto()  # _

    # Punctuation
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    COMMA = auto()  # ,
    DOT = auto()  # .

    # Operators
    COLON_DASH = auto()  # :-
    EQUALS = auto()  # =
    NOT_EQUALS = auto()  # !=

    # Keywords
    NOT = auto()  # not

    # Query
    QUESTION = auto()  # ?

    # Special
    EOF = auto()


@dataclass
class Token:
    """A single lexical token with position information."""

    type: DatalogIRToken
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.col})"


# ──────────────────────────────────────────────
#  Lexer
# ──────────────────────────────────────────────


class LexerError(Exception):
    """Raised when the lexer encounters an unexpected character."""

    def __init__(self, message: str, line: int, col: int) -> None:
        self.line = line
        self.col = col
        super().__init__(f"Lexer error at L{line}:{col}: {message}")


class Lexer:
    """Tokeniser for DatalogIR source text."""

    def __init__(self, source: str) -> None:
        self._src = source
        self._pos = 0
        self._line = 1
        self._col = 1

    # -- helpers ------------------------------------------------

    def _peek(self) -> str | None:
        if self._pos < len(self._src):
            return self._src[self._pos]
        return None

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return ch

    def _skip_whitespace_and_comments(self) -> None:
        while self._pos < len(self._src):
            ch = self._src[self._pos]
            if ch in " \t\r\n":
                self._advance()
            elif ch == "%":
                # skip to end of line
                while self._pos < len(self._src) and self._src[self._pos] != "\n":
                    self._advance()
            else:
                break

    def _read_identifier(self) -> str:
        start = self._pos
        while self._pos < len(self._src) and (
            self._src[self._pos].isalnum() or self._src[self._pos] == "_"
        ):
            self._advance()
        return self._src[start : self._pos]

    # -- public -------------------------------------------------

    def tokenize(self) -> list[Token]:
        """Return all tokens (excluding comments/whitespace), ending with EOF."""
        tokens: list[Token] = []
        while True:
            self._skip_whitespace_and_comments()
            if self._pos >= len(self._src):
                tokens.append(Token(DatalogIRToken.EOF, "", self._line, self._col))
                break

            line, col = self._line, self._col
            ch = self._peek()
            assert ch is not None

            if ch == "(":
                self._advance()
                tokens.append(Token(DatalogIRToken.LPAREN, "(", line, col))
            elif ch == ")":
                self._advance()
                tokens.append(Token(DatalogIRToken.RPAREN, ")", line, col))
            elif ch == ",":
                self._advance()
                tokens.append(Token(DatalogIRToken.COMMA, ",", line, col))
            elif ch == ".":
                self._advance()
                tokens.append(Token(DatalogIRToken.DOT, ".", line, col))
            elif ch == "?":
                self._advance()
                tokens.append(Token(DatalogIRToken.QUESTION, "?", line, col))
            elif ch == "=":
                self._advance()
                tokens.append(Token(DatalogIRToken.EQUALS, "=", line, col))
            elif (
                ch == "!"
                and self._pos + 1 < len(self._src)
                and self._src[self._pos + 1] == "="
            ):
                self._advance()
                self._advance()
                tokens.append(Token(DatalogIRToken.NOT_EQUALS, "!=", line, col))
            elif (
                ch == ":"
                and self._pos + 1 < len(self._src)
                and self._src[self._pos + 1] == "-"
            ):
                self._advance()
                self._advance()
                tokens.append(Token(DatalogIRToken.COLON_DASH, ":-", line, col))
            elif ch == "_" and (
                self._pos + 1 >= len(self._src)
                or not (
                    self._src[self._pos + 1].isalnum()
                    or self._src[self._pos + 1] == "_"
                )
            ):
                self._advance()
                tokens.append(Token(DatalogIRToken.WILDCARD, "_", line, col))
            elif ch.isalpha() or ch == "_":
                ident = self._read_identifier()
                if ident == "not":
                    tokens.append(Token(DatalogIRToken.NOT, "not", line, col))
                elif ident[0].isupper():
                    tokens.append(Token(DatalogIRToken.IDENT_UPPER, ident, line, col))
                else:
                    tokens.append(Token(DatalogIRToken.IDENT_LOWER, ident, line, col))
            else:
                raise LexerError(f"Unexpected character {ch!r}", line, col)

        return tokens


# ──────────────────────────────────────────────
#  AST Nodes
# ──────────────────────────────────────────────


@dataclass
class Constant:
    """A constant term (lowercase identifier)."""

    name: str
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return self.name


@dataclass
class Variable:
    """A variable term (uppercase identifier)."""

    name: str
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return self.name


@dataclass
class Wildcard:
    """An anonymous variable (_)."""

    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return "_"


Term = Union[Constant, Variable, Wildcard]


@dataclass
class Atom:
    """An atomic formula: p  or  p(t1, ..., tn)."""

    predicate: str
    args: list[Term] = field(default_factory=list)
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        if not self.args:
            return self.predicate
        args_str = ", ".join(repr(a) for a in self.args)
        return f"{self.predicate}({args_str})"


@dataclass
class NegatedAtom:
    """Negation-as-failure premise: not A."""

    atom: Atom
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return f"not {self.atom!r}"


@dataclass
class Equality:
    """Unification premise: t = t."""

    left: Term
    right: Term
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return f"{self.left!r}={self.right!r}"


@dataclass
class Inequality:
    """Disunification premise: t != t."""

    left: Term
    right: Term
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return f"{self.left!r}!={self.right!r}"


Premise = Union[Atom, NegatedAtom, Equality, Inequality]


@dataclass
class Fact:
    """A fact clause: A."""

    head: Atom
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return f"{self.head!r}."


@dataclass
class Rule:
    """A rule clause: A :- φ1, ..., φn."""

    head: Atom
    body: list[Premise]
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        body_str = ", ".join(repr(p) for p in self.body)
        return f"{self.head!r} :- {body_str}."


@dataclass
class Query:
    """A query: A?"""

    atom: Atom
    line: int = 0
    col: int = 0

    def __repr__(self) -> str:
        return f"{self.atom!r}?"


Clause = Union[Fact, Rule, Query]


@dataclass
class Program:
    """A complete DatalogIR program: a sequence of clauses."""

    clauses: list[Clause] = field(default_factory=list)

    def __repr__(self) -> str:
        return "\n".join(repr(c) for c in self.clauses)


# ──────────────────────────────────────────────
#  Parser (Syntax Checker)
# ──────────────────────────────────────────────


class SyntaxError(Exception):
    """Raised when the parser encounters a syntax error."""

    def __init__(self, message: str, line: int, col: int) -> None:
        self.line = line
        self.col = col
        super().__init__(f"Syntax error at L{line}:{col}: {message}")


class Parser:
    """Recursive-descent parser and syntax checker for DatalogIR.

    Grammar (EBNF):
        program   ::= { clause }
        clause    ::= atom ( '.' | ':-' premise { ',' premise } '.' | '?' )
        premise   ::= atom ( ( '=' | '!=' ) term )?
                     | 'not' atom
                     | term ( '=' | '!=' ) term       (handled via backtrack)
        atom      ::= IDENT_LOWER [ '(' term { ',' term } ')' ]
        term      ::= IDENT_LOWER | IDENT_UPPER | '_'
    """

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -- helpers ------------------------------------------------

    def _cur(self) -> Token:
        return self._tokens[self._pos]

    def _peek_type(self) -> DatalogIRToken:
        return self._tokens[self._pos].type

    def _expect(self, tt: DatalogIRToken) -> Token:
        tok = self._cur()
        if tok.type != tt:
            raise SyntaxError(
                f"Expected {tt.name}, got {tok.type.name} ({tok.value!r})",
                tok.line,
                tok.col,
            )
        self._pos += 1
        return tok

    def _match(self, tt: DatalogIRToken) -> Token | None:
        if self._peek_type() == tt:
            tok = self._cur()
            self._pos += 1
            return tok
        return None

    # -- grammar rules ------------------------------------------

    def parse_program(self) -> Program:
        """Parse the full program and check syntax."""
        program = Program()
        while self._peek_type() != DatalogIRToken.EOF:
            program.clauses.append(self._parse_clause())
        self._expect(DatalogIRToken.EOF)
        return program

    def _parse_clause(self) -> Clause:
        """clause ::= atom ( '.' | ':-' premise { ',' premise } '.' | '?' )"""
        head = self._parse_atom()

        if self._match(DatalogIRToken.DOT):
            return Fact(head=head, line=head.line, col=head.col)

        if self._match(DatalogIRToken.QUESTION):
            return Query(atom=head, line=head.line, col=head.col)

        self._expect(DatalogIRToken.COLON_DASH)
        body: list[Premise] = [self._parse_premise()]
        while self._match(DatalogIRToken.COMMA):
            body.append(self._parse_premise())
        self._expect(DatalogIRToken.DOT)
        return Rule(head=head, body=body, line=head.line, col=head.col)

    def _parse_atom(self) -> Atom:
        """atom ::= IDENT_LOWER [ '(' term { ',' term } ')' ]"""
        tok = self._expect(DatalogIRToken.IDENT_LOWER)
        args: list[Term] = []
        if self._match(DatalogIRToken.LPAREN):
            args.append(self._parse_term())
            while self._match(DatalogIRToken.COMMA):
                args.append(self._parse_term())
            self._expect(DatalogIRToken.RPAREN)
        return Atom(predicate=tok.value, args=args, line=tok.line, col=tok.col)

    def _parse_term(self) -> Term:
        """term ::= IDENT_LOWER | IDENT_UPPER | '_'"""
        tok = self._cur()
        if tok.type == DatalogIRToken.IDENT_LOWER:
            self._pos += 1
            return Constant(name=tok.value, line=tok.line, col=tok.col)
        if tok.type == DatalogIRToken.IDENT_UPPER:
            self._pos += 1
            return Variable(name=tok.value, line=tok.line, col=tok.col)
        if tok.type == DatalogIRToken.WILDCARD:
            self._pos += 1
            return Wildcard(line=tok.line, col=tok.col)
        raise SyntaxError(
            f"Expected a term (constant, variable, or '_'), got {tok.type.name} ({tok.value!r})",
            tok.line,
            tok.col,
        )

    def _parse_premise(self) -> Premise:
        """premise ::= 'not' atom
        | atom [ ('=' | '!=') term ]
        | term ('=' | '!=') term
        """
        # Negation
        if self._match(DatalogIRToken.NOT):
            atom = self._parse_atom()
            return NegatedAtom(atom=atom, line=atom.line, col=atom.col)

        # Could be an atom, or a bare term followed by = / !=
        tok = self._cur()

        if tok.type == DatalogIRToken.IDENT_LOWER:
            # Could be atom or constant-as-term
            saved = self._pos
            atom = self._parse_atom()

            # Check for = or !=  after atom — only valid when atom has no args
            # (i.e. it was parsed as a propositional atom but is really a term)
            if self._peek_type() == DatalogIRToken.EQUALS:
                if atom.args:
                    raise SyntaxError(
                        "Left side of '=' must be a term, not a compound atom",
                        tok.line,
                        tok.col,
                    )
                self._expect(DatalogIRToken.EQUALS)
                right = self._parse_term()
                left = Constant(name=atom.predicate, line=atom.line, col=atom.col)
                return Equality(left=left, right=right, line=tok.line, col=tok.col)

            if self._peek_type() == DatalogIRToken.NOT_EQUALS:
                if atom.args:
                    raise SyntaxError(
                        "Left side of '!=' must be a term, not a compound atom",
                        tok.line,
                        tok.col,
                    )
                self._expect(DatalogIRToken.NOT_EQUALS)
                right = self._parse_term()
                left = Constant(name=atom.predicate, line=atom.line, col=atom.col)
                return Inequality(left=left, right=right, line=tok.line, col=tok.col)

            return atom

        # Must be a variable/wildcard term followed by = or !=
        left = self._parse_term()

        if self._match(DatalogIRToken.EQUALS):
            right = self._parse_term()
            return Equality(left=left, right=right, line=tok.line, col=tok.col)

        if self._match(DatalogIRToken.NOT_EQUALS):
            right = self._parse_term()
            return Inequality(left=left, right=right, line=tok.line, col=tok.col)

        raise SyntaxError(
            f"Expected '=' or '!=' after term in premise, got {self._cur().type.name}",
            self._cur().line,
            self._cur().col,
        )


# ──────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────


def check_syntax(source: str) -> Program:
    """Lex and parse a DatalogIR source string.

    Returns the parsed Program AST on success.
    Raises LexerError or SyntaxError on failure.
    """
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse_program()
