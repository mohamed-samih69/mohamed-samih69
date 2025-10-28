from __future__ import annotations
import argparse
from .lexer import Lexer
from .parser import Parser
from .semantic import TypeChecker, SemanticError


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="TinyC: lexical, syntax, semantic analyzers")
    ap.add_argument("file", help="source file to compile")
    ap.add_argument("--dump-tokens", action="store_true")
    ap.add_argument("--dump-ast", action="store_true")
    args = ap.parse_args(argv)

    with open(args.file, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        if args.dump_tokens:
            for t in tokens:
                print(f"{t.kind.name}\t{t.lexeme!r} @ {t.line}:{t.col}")
        parser = Parser(tokens)
        prog = parser.parse()
        if args.dump_ast:
            print(prog)
        checker = TypeChecker()
        checker.check(prog)
        print("Semantic analysis succeeded ✅")
        return 0
    except (SyntaxError, SemanticError) as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
