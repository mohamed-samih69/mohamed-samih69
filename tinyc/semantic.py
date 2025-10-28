from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .ast import *


@dataclass
class VarInfo:
    type: Type


@dataclass
class FuncInfo:
    params: list[Type]
    ret: Optional[Type]


class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self):
        self.scopes: list[dict[str, VarInfo]] = [{}]
        self.funcs: dict[str, FuncInfo] = {}

    def push(self) -> None:
        self.scopes.append({})

    def pop(self) -> None:
        self.scopes.pop()

    def declare_var(self, name: str, typ: Type) -> None:
        scope = self.scopes[-1]
        if name in scope:
            raise SemanticError(f"Variable '{name}' already declared")
        scope[name] = VarInfo(typ)

    def resolve_var(self, name: str) -> VarInfo:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Undefined variable '{name}'")

    def declare_func(self, name: str, param_types: list[Type], ret: Optional[Type]) -> None:
        if name in self.funcs:
            raise SemanticError(f"Function '{name}' already declared")
        self.funcs[name] = FuncInfo(param_types, ret)

    def resolve_func(self, name: str) -> FuncInfo:
        if name not in self.funcs:
            raise SemanticError(f"Undefined function '{name}'")
        return self.funcs[name]


class TypeChecker:
    def __init__(self):
        self.sym = SymbolTable()
        self.current_return: Optional[Type] = None

    def check(self, prog: Program) -> None:
        # First pass: declare functions
        for fn in prog:
            param_types = [p.type for p in fn.params]
            self.sym.declare_func(fn.name, param_types, fn.ret_type)
        # Second pass: check bodies
        for fn in prog:
            self._check_func(fn)

    def _check_func(self, fn: Func) -> None:
        self.sym.push()
        self.current_return = fn.ret_type
        for p in fn.params:
            self.sym.declare_var(p.name, p.type)
        for stmt in fn.body:
            self._check_stmt(stmt)
        self.sym.pop()

    def _type_equals(self, a: Type, b: Type) -> bool:
        return type(a) is type(b)

    def _expect(self, cond: bool, msg: str) -> None:
        if not cond:
            raise SemanticError(msg)

    def _check_stmt(self, s: Stmt) -> None:
        if isinstance(s, Let):
            if s.init is not None and s.type_ann is not None:
                init_t = self._check_expr(s.init)
                self._expect(self._type_equals(init_t, s.type_ann), "Initializer type does not match annotation")
                self.sym.declare_var(s.name, s.type_ann)
            elif s.init is not None:
                self.sym.declare_var(s.name, self._check_expr(s.init))
            else:
                self._expect(s.type_ann is not None, "Let without init requires type annotation")
                self.sym.declare_var(s.name, s.type_ann)
        elif isinstance(s, Return):
            if s.value is None:
                self._expect(self.current_return is None, "Return without value in non-void function")
            else:
                val_t = self._check_expr(s.value)
                self._expect(self.current_return is not None and self._type_equals(val_t, self.current_return), "Return type mismatch")
        elif isinstance(s, If):
            cond_t = self._check_expr(s.cond)
            self._expect(isinstance(cond_t, BoolType), "If condition must be bool")
            self.sym.push()
            for st in s.then_branch:
                self._check_stmt(st)
            self.sym.pop()
            if s.else_branch is not None:
                self.sym.push()
                for st in s.else_branch:
                    self._check_stmt(st)
                self.sym.pop()
        elif isinstance(s, While):
            cond_t = self._check_expr(s.cond)
            self._expect(isinstance(cond_t, BoolType), "While condition must be bool")
            self.sym.push()
            for st in s.body:
                self._check_stmt(st)
            self.sym.pop()
        elif isinstance(s, ExprStmt):
            self._check_expr(s.expr)
        else:
            raise SemanticError("Unknown statement")

    def _check_expr(self, e: Expr) -> Type:
        if isinstance(e, Literal):
            if isinstance(e.value, bool):
                return BoolType()
            if isinstance(e.value, int):
                return IntType()
            if isinstance(e.value, str):
                raise SemanticError("String literals unsupported in type system")
            raise SemanticError("Unsupported literal type")
        if isinstance(e, Var):
            return self.sym.resolve_var(e.name).type
        if isinstance(e, Unary):
            t = self._check_expr(e.expr)
            if e.op == '!':
                self._expect(isinstance(t, BoolType), "'!' expects bool")
                return BoolType()
            if e.op == '-':
                self._expect(isinstance(t, IntType), "Unary '-' expects int")
                return IntType()
            raise SemanticError("Unknown unary operator")
        if isinstance(e, Binary):
            lt = self._check_expr(e.left)
            rt = self._check_expr(e.right)
            if e.op in ('+', '-', '*', '/', '%'):
                self._expect(isinstance(lt, IntType) and isinstance(rt, IntType), "Arithmetic expects ints")
                return IntType()
            if e.op in ('==', '!=', '>', '>=', '<', '<='):
                self._expect(type(lt) is type(rt), "Comparison operands must be same type")
                return BoolType()
            raise SemanticError("Unknown binary operator")
        if isinstance(e, Call):
            info = self.sym.resolve_func(e.callee)
            self._expect(len(info.params) == len(e.args), "Arity mismatch in call")
            for i, arg in enumerate(e.args):
                at = self._check_expr(arg)
                self._expect(self._type_equals(at, info.params[i]), f"Argument {i+1} type mismatch")
            return info.ret if info.ret is not None else IntType()
        raise SemanticError("Unknown expression")
