from __future__ import annotations
from typing import List, Optional
from .tokens import TokenKind, Token
from .ast import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        funcs: Program = []
        while not self._check(TokenKind.EOF):
            funcs.append(self._function())
        return funcs

    # Helpers
    def _is_at_end(self) -> bool:
        return self._peek().kind == TokenKind.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, kind: TokenKind) -> bool:
        if self._is_at_end():
            return kind == TokenKind.EOF
        return self._peek().kind == kind

    def _match(self, *kinds: TokenKind) -> bool:
        for k in kinds:
            if self._check(k):
                self._advance()
                return True
        return False

    def _consume(self, kind: TokenKind, msg: str) -> Token:
        if self._check(kind):
            return self._advance()
        t = self._peek()
        raise SyntaxError(f"{msg} at line {t.line}")

    # Grammar
    # program     -> { function } EOF ;
    # function    -> 'fn' IDENT '(' [ params ] ')' [ '->' type ] '{' { statement } '}' ;
    # params      -> IDENT ':' type { ',' IDENT ':' type } ;
    # type        -> 'int' | 'bool' ;
    # statement   -> let | return | if | while | expr ';' ;
    # let         -> 'let' IDENT [ ':' type ] [ '=' expression ] ';' ;
    # return      -> 'return' [ expression ] ';' ;
    # if          -> 'if' '(' expression ')' block [ 'else' block ] ;
    # while       -> 'while' '(' expression ')' block ;
    # block       -> '{' { statement } '}' ;
    # expression  -> equality ;
    # equality    -> comparison ( ( '==' | '!=' ) comparison )* ;
    # comparison  -> term ( ( '>' | '>=' | '<' | '<=' ) term )* ;
    # term        -> factor ( ( '+' | '-' ) factor )* ;
    # factor      -> unary ( ( '*' | '/' | '%' ) unary )* ;
    # unary       -> ( '!' | '-' ) unary | call ;
    # call        -> primary ( '(' [ args ] ')' )? ;
    # args        -> expression { ',' expression } ;
    # primary     -> NUMBER | BOOL | STRING | IDENT | '(' expression ')' ;

    def _function(self) -> Func:
        self._consume(TokenKind.FN, "Expected 'fn'")
        name = self._consume(TokenKind.IDENT, "Expected function name").lexeme
        self._consume(TokenKind.LPAREN, "Expected '('")
        params: List[Param] = []
        if not self._check(TokenKind.RPAREN):
            params.append(self._param())
            while self._match(TokenKind.COMMA):
                params.append(self._param())
        self._consume(TokenKind.RPAREN, "Expected ')'")
        ret_type: Optional[Type] = None
        if self._match(TokenKind.ARROW):
            ret_type = self._type()
        body = self._block()
        return Func(name, params, ret_type, body)

    def _param(self) -> Param:
        name = self._consume(TokenKind.IDENT, "Expected parameter name").lexeme
        self._consume(TokenKind.COLON, "Expected ':' after parameter name")
        t = self._type()
        return Param(name, t)

    def _type(self) -> Type:
        if self._match(TokenKind.INT):
            return IntType()
        if self._match(TokenKind.BOOL_T):
            return BoolType()
        raise SyntaxError("Unknown type")

    def _block(self) -> List[Stmt]:
        self._consume(TokenKind.LBRACE, "Expected '{'")
        statements: List[Stmt] = []
        while not self._check(TokenKind.RBRACE):
            statements.append(self._statement())
        self._consume(TokenKind.RBRACE, "Expected '}'")
        return statements

    def _statement(self) -> Stmt:
        if self._match(TokenKind.LET):
            name = self._consume(TokenKind.IDENT, "Expected variable name").lexeme
            type_ann: Optional[Type] = None
            if self._match(TokenKind.COLON):
                type_ann = self._type()
            init: Optional[Expr] = None
            if self._match(TokenKind.EQ):
                init = self._expression()
            self._consume(TokenKind.SEMI, "Expected ';'")
            return Let(name, type_ann, init)
        if self._match(TokenKind.RETURN):
            value: Optional[Expr] = None
            if not self._check(TokenKind.SEMI):
                value = self._expression()
            self._consume(TokenKind.SEMI, "Expected ';'")
            return Return(value)
            
        if self._match(TokenKind.IF):
            self._consume(TokenKind.LPAREN, "Expected '('")
            cond = self._expression()
            self._consume(TokenKind.RPAREN, "Expected ')'")
            then_branch = self._block()
            else_branch = None
            if self._match(TokenKind.ELSE):
                else_branch = self._block()
            return If(cond, then_branch, else_branch)
        if self._match(TokenKind.WHILE):
            self._consume(TokenKind.LPAREN, "Expected '('")
            cond = self._expression()
            self._consume(TokenKind.RPAREN, "Expected ')'")
            body = self._block()
            return While(cond, body)
        expr = self._expression()
        self._consume(TokenKind.SEMI, "Expected ';'")
        return ExprStmt(expr)

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenKind.EQEQ, TokenKind.BANGEQ):
            op = self._previous().lexeme
            right = self._comparison()
            expr = Binary(expr, op, right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(TokenKind.GT, TokenKind.GTE, TokenKind.LT, TokenKind.LTE):
            op = self._previous().lexeme
            right = self._term()
            expr = Binary(expr, op, right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenKind.PLUS, TokenKind.MINUS):
            op = self._previous().lexeme
            right = self._factor()
            expr = Binary(expr, op, right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(TokenKind.STAR, TokenKind.SLASH, TokenKind.PERCENT):
            op = self._previous().lexeme
            right = self._unary()
            expr = Binary(expr, op, right)
        return expr

    def _unary(self) -> Expr:
        if self._match(TokenKind.BANG, TokenKind.MINUS):
            op = self._previous().lexeme
            right = self._unary()
            return Unary(op, right)
        return self._call()

    def _call(self) -> Expr:
        # function call: IDENT '(' args? ')'
        if self._check(TokenKind.IDENT) and self.tokens[self.current + 1].kind == TokenKind.LPAREN:
            name = self._advance().lexeme
            self._consume(TokenKind.LPAREN, "Expected '('")
            args: List[Expr] = []
            if not self._check(TokenKind.RPAREN):
                args.append(self._expression())
                while self._match(TokenKind.COMMA):
                    args.append(self._expression())
            self._consume(TokenKind.RPAREN, "Expected ')'")
            return Call(name, args)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenKind.NUMBER, TokenKind.STRING, TokenKind.BOOL):
            tok = self._previous()
            value = tok.literal if tok.literal is not None else tok.lexeme
            return Literal(value)
        if self._match(TokenKind.IDENT):
            return Var(self._previous().lexeme)
        if self._match(TokenKind.LPAREN):
            expr = self._expression()
            self._consume(TokenKind.RPAREN, "Expected ')'")
            return expr
        raise SyntaxError("Expected expression")
