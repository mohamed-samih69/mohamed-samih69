# Components and Modules

This section maps the conceptual components of the compiler and their responsibilities. If your implementation is in a single file or a different language, you can still keep these module boundaries conceptually.

## `lexer`
- Responsibility: tokenization of source code to `Token[]`.
- Inputs: source text.
- Outputs: token stream with positions.
- Public API: `tokenize` and token/type exports.

## `parser`
- Responsibility: grammar parsing to untyped `Ast`.
- Inputs: `Token[]`.
- Outputs: `Ast.Program`.
- Public API: `parse` and AST node type exports.

## `semantics`
- Responsibility: name resolution and typing.
- Inputs: `Ast.Program`.
- Outputs: `TypedProgram`.
- Public API: `analyze`, `Type`, and typed AST types.

## `ir`
- Responsibility: intermediate representation and lowering.
- Inputs: `TypedProgram`.
- Outputs: three-address code function.
- Public API: `lowerToIR`, IR instruction types.

## `optimizer`
- Responsibility: TAC optimization passes.
- Inputs: `IR.Function`.
- Outputs: optimized `IR.Function`.
- Public API: `optimize`.

## `codegen`
- Responsibility: final code emission.
- Inputs: `IR.Function` and options.
- Outputs: textual three-address code.
- Public API: `generate`.

## `driver`
- Responsibility: orchestrate full compilation and provide CLI.
- Inputs: source code or file path.
- Outputs: artifacts and emitted code.
- Public API: `compile`, `runCli`.
