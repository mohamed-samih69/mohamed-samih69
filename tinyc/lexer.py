from __future__ import annotations
from .tokens import Token, TokenKind, KEYWORDS


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._is_at_end():
            self.start = self.current
            tok = self._scan_token()
            if tok is not None:
                tokens.append(tok)
        tokens.append(Token(TokenKind.EOF, "", self.line, self.col))
        return tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        self.col += 1
        return ch

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.col += 1
        return True

    def _add_token(self, kind: TokenKind, lexeme: str, literal=None) -> Token:
        # Compute start column by subtracting lexeme length - 1 from current col
        start_col = self.col - len(lexeme)
        return Token(kind, lexeme, self.line, start_col + 1, literal)

    def _scan_token(self) -> Token | None:
        ch = self._advance()
        # whitespace
        if ch in " \r\t":
            return None
        if ch == "\n":
            self.line += 1
            self.col = 1
            return None
        # line comment
        if ch == "/" and self._peek() == "/":
            while not self._is_at_end() and self._peek() != "\n":
                self._advance()
            return None

        if ch == "(":
            return self._add_token(TokenKind.LPAREN, ch)
        if ch == ")":
            return self._add_token(TokenKind.RPAREN, ch)
        if ch == "{":
            return self._add_token(TokenKind.LBRACE, ch)
        if ch == "}":
            return self._add_token(TokenKind.RBRACE, ch)
        if ch == ",":
            return self._add_token(TokenKind.COMMA, ch)
        if ch == ";":
            return self._add_token(TokenKind.SEMI, ch)
        if ch == ":":
            return self._add_token(TokenKind.COLON, ch)
        if ch == "+":
            return self._add_token(TokenKind.PLUS, ch)
        if ch == "-":
            if self._match(">"):
                return self._add_token(TokenKind.ARROW, "->")
            return self._add_token(TokenKind.MINUS, ch)
        if ch == "*":
            return self._add_token(TokenKind.STAR, ch)
        if ch == "%":
            return self._add_token(TokenKind.PERCENT, ch)
        if ch == "!":
            if self._match("="):
                return self._add_token(TokenKind.BANGEQ, "!=")
            return self._add_token(TokenKind.BANG, "!")
        if ch == "=":
            if self._match("="):
                return self._add_token(TokenKind.EQEQ, "==")
            return self._add_token(TokenKind.EQ, "=")
        if ch == "<":
            if self._match("="):
                return self._add_token(TokenKind.LTE, "<=")
            return self._add_token(TokenKind.LT, "<")
        if ch == ">":
            if self._match("="):
                return self._add_token(TokenKind.GTE, ">=")
            return self._add_token(TokenKind.GT, ">")
        if ch == "/":
            return self._add_token(TokenKind.SLASH, ch)
        if ch == '"':
            return self._string()

        if ch.isdigit():
            return self._number(ch)
        if ch.isalpha() or ch == "_":
            return self._identifier(ch)

        raise SyntaxError(f"Unexpected character '{ch}' at {self.line}:{self.col}")

    def _string(self) -> Token:
        start_col = self.col - 1
        value_chars: list[str] = []
        while not self._is_at_end() and self._peek() != '"':
            ch = self._advance()
            if ch == "\n":
                self.line += 1
                self.col = 1
            value_chars.append(ch)
        if self._is_at_end():
            raise SyntaxError(f"Unterminated string at {self.line}:{start_col}")
        self._advance()  # consume closing quote
        value = "".join(value_chars)
        return Token(TokenKind.STRING, value, self.line, start_col, value)

    def _number(self, first: str) -> Token:
        lex = [first]
        while self._peek().isdigit():
            lex.append(self._advance())
        value_str = "".join(lex)
        return self._add_token(TokenKind.NUMBER, value_str, int(value_str))

    def _identifier(self, first: str) -> Token:
        lex = [first]
        while True:
            p = self._peek()
            if p.isalnum() or p == "_":
                lex.append(self._advance())
            else:
                break
        word = "".join(lex)
        # handle boolean literals specially
        if word == "true":
            return self._add_token(TokenKind.BOOL, word, True)
        if word == "false":
            return self._add_token(TokenKind.BOOL, word, False)
        kind = KEYWORDS.get(word)
        if kind is not None:
            return self._add_token(kind, word)
        return self._add_token(TokenKind.IDENT, word)
