from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List


# Types
class Type:
    pass


@dataclass
class IntType(Type):
    pass


@dataclass
class BoolType(Type):
    pass


# Expressions
class Expr:
    ...


@dataclass
class Literal(Expr):
    value: object


@dataclass
class Var(Expr):
    name: str


@dataclass
class Binary(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class Unary(Expr):
    op: str
    expr: Expr


@dataclass
class Call(Expr):
    callee: str
    args: List[Expr]


# Statements
class Stmt:
    ...


@dataclass
class Let(Stmt):
    name: str
    type_ann: Optional[Type]
    init: Optional[Expr]


@dataclass
class Return(Stmt):
    value: Optional[Expr]


@dataclass
class If(Stmt):
    cond: Expr
    then_branch: List[Stmt]
    else_branch: Optional[List[Stmt]]


@dataclass
class While(Stmt):
    cond: Expr
    body: List[Stmt]


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class Param:
    name: str
    type: Type


@dataclass
class Func:
    name: str
    params: List[Param]
    ret_type: Optional[Type]
    body: List[Stmt]


Program = List[Func]
