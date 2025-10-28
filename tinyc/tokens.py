from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class TokenKind(Enum):
    # single-char
    LPAREN = auto(); RPAREN = auto()
    LBRACE = auto(); RBRACE = auto()
    COMMA = auto(); SEMI = auto(); COLON = auto()
    PLUS = auto(); MINUS = auto(); STAR = auto(); SLASH = auto(); PERCENT = auto()
    EQ = auto(); BANG = auto(); LT = auto(); GT = auto()

    # two-char
    EQEQ = auto(); BANGEQ = auto(); LTE = auto(); GTE = auto(); ARROW = auto()

    # literals & identifiers
    IDENT = auto(); NUMBER = auto(); BOOL = auto(); STRING = auto()

    # keywords
    LET = auto(); FN = auto(); RETURN = auto(); IF = auto(); ELSE = auto(); WHILE = auto()
    INT = auto(); BOOL_T = auto()

    EOF = auto()


KEYWORDS: dict[str, TokenKind] = {
    "let": TokenKind.LET,
    "fn": TokenKind.FN,
    "return": TokenKind.RETURN,
    "if": TokenKind.IF,
    "else": TokenKind.ELSE,
    "while": TokenKind.WHILE,
    "true": TokenKind.TRUE if False else TokenKind.BOOL,  # mapped specially in lexer
    "false": TokenKind.FALSE if False else TokenKind.BOOL,  # mapped specially in lexer
    "int": TokenKind.INT,
    "bool": TokenKind.BOOL_T,
}


@dataclass
class Token:
    kind: TokenKind
    lexeme: str
    line: int
    col: int
    literal: object | None = None
