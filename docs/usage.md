# Usage Guide

This guide shows how to use the compiler programmatically and from a CLI. Examples are language-agnostic; adapt to your chosen implementation (Java, C, or Python).

## Programmatic API

Example (TypeScript-like pseudocode) using the APIs in the reference:

```ts
import { tokenize, parse, analyze, lowerToIR, optimize, generate } from 'tiny-compiler';

const source = `y := x*2.0 + z*3.0*r; write y;`;

const tokens = tokenize(source);
const ast = parse(tokens);
const typed = analyze(ast);
const ir = lowerToIR(typed);
const optimized = optimize(ir, { constFold: true, algebraic: true, dce: true });
const output = generate(optimized, 'tac');

console.log(output);
```

## CLI

Assuming a CLI executable named `tinyc`:

```bash
# Compile and emit optimized TAC to stdout
echo "y := x*2.0 + z*3.0*r; write y;" | tinyc --optimized

# Show tokens only
echo "write 3+4;" | tinyc --tokens

# Show AST and save output to a file
echo "write 3+4;" | tinyc --ast --out out.tac
```

## Error Handling

- Lexical errors include the line and column of the offending character.
- Parse errors report the unexpected token and expected set.
- Semantic errors include the variable name and the operation that failed.

## Data Types and Conversions

- Mixed arithmetic promotes `int` to `float`.
- Assignments convert RHS to LHS type when safe; otherwise error.

## Tips

- Use semicolons to separate statements.
- Parentheses control precedence in complex expressions.
- For comments, wrap with `{}` or start a line with `%%`.
