# API Reference

This API reference documents the public functions, classes, and components in a typical tiny-compiler implementation for this project. If your codebase differs, adapt the names while keeping the contracts below.

## Lexer (Lexical Analyzer)

- `tokenize(source: string) -> Token[]`
  - Splits `source` into a sequence of tokens per the language spec.
  - Throws `LexError` with `{message, line, column}` on invalid characters or unterminated comments.
  - Tokens include type (`Identifier`, `Number`, `Float`, `Reserved`, `Symbol`), lexeme, and position.

- `Token` (type)
  - `kind: TokenKind`
  - `lexeme: string`
  - `line: number`, `column: number`

- `TokenKind` (enum)
  - `If`, `Then`, `Else`, `End`, `Repeat`, `Until`, `Read`, `Write`,
  - `Plus`, `Minus`, `Star`, `Slash`, `LParen`, `RParen`, `Semi`, `Assign`, `Equal`, `Less`,
  - `Identifier`, `IntLiteral`, `FloatLiteral`, `EOF`

## Parser (Syntax Analyzer)

- `parse(tokens: Token[]) -> Ast.Program`
  - Builds an abstract syntax tree from `tokens`.
  - Throws `ParseError` when grammar rules are violated, including expected token diagnostics.

- `Ast` (namespace/types)
  - `Program { statements: Statement[] }`
  - `Statement = If | Repeat | Assign | Read | Write`
  - `If { test: Expression, thenBranch: Statement[], elseBranch?: Statement[] }`
  - `Repeat { body: Statement[], until: Expression }`
  - `Assign { name: string, value: Expression }`
  - `Read { name: string }`
  - `Write { value: Expression }`
  - `Expression = Binary | Grouping | Literal | Variable`
  - `Binary { left: Expression, op: BinaryOp, right: Expression }`
  - `BinaryOp = Plus | Minus | Star | Slash | Less | Equal`
  - `Grouping { expr: Expression }`
  - `Literal { kind: 'int'|'float', value: number }`
  - `Variable { name: string }`

## Semantic Analyzer (Typing)

- `analyze(ast: Ast.Program) -> TypedProgram`
  - Performs name resolution, type inference, and checks conversions between `int` and `float`.
  - Returns an AST annotated with types; throws `SemanticError` on undefined identifiers or invalid operations.

- `Type` (enum/ADT)
  - `Int`, `Float`, `Bool`

- `TypedExpression` extends `Expression` with `type: Type`.

## Intermediate Representation (IR)

- `lowerToIR(program: TypedProgram) -> IR.Function`
  - Produces three-address code (TAC) with temporaries.

- `IR.Instruction`
  - `op: 'add'|'sub'|'mul'|'div'|'lt'|'eq'|'assign'|'param'|'call'|'label'|'goto'|'ifz'|'read'|'write'`
  - `args: string[]` (temporary names, constants, or labels)

## Optimizer

- `optimize(ir: IR.Function, options?: { constFold?: boolean, algebraic?: boolean, dce?: boolean }) -> IR.Function`
  - Enables constant folding, algebraic simplifications, and dead-code elimination on TAC.

## Code Generator

- `generate(ir: IR.Function, target?: 'tac'|'pseudo') -> string`
  - Emits final text representation of optimized three-address code.

## Driver / CLI

- `compile(source: string, options?: CompileOptions) -> { tokens: Token[], ast: Ast.Program, typed: TypedProgram, ir: IR.Function, optimized: IR.Function, output: string }`
  - Runs all phases and returns the artifacts.

- `runCli(argv: string[]) -> Promise<number>`
  - CLI entry point. Supports:
    - `--tokens`: print tokens
    - `--ast`: print AST
    - `--typed`: print typed AST
    - `--ir`: print IR
    - `--optimized`: print optimized IR
    - `--out file`: write final code to file

## Error Types

- `LexError`, `ParseError`, `SemanticError` extend a base `CompileError` with location.

## Public Constants

- `LANGUAGE_SPEC`: exported object summarizing tokens, grammar, and types.

## Extension Points

- Hook interfaces:
  - `Logger { log(info), warn(msg), error(err) }`
  - `FileSystem { read(path), write(path, content) }`
