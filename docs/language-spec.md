# Language Specification

This spec is derived from the assignment sheet. It defines tokens, lexical rules, grammar, semantics, and data types supported by the tiny compiler.

## Tokens

- Reserved words: `if`, `then`, `else`, `end`, `repeat`, `until`, `read`, `write`
- Special symbols:
  - Arithmetic: `+`, `-`, `*`, `/`
  - Comparison: `=` (equality), `<` (less-than)
  - Parentheses: `(`, `)`
  - Semicolon: `;`
  - Assignment operator: `:` `=` (written as `:=`)
  - Comment delimiters: `{` `}` for block comments, and any line starting with `%%` for line comments
- Other:
  - Numbers: unsigned integers and floats (per project requirement to have `int` and `float` types)
  - Identifiers: begin with a letter, followed by letters, digits, or `_`

## Lexical rules

- Whitespace separates tokens and is otherwise ignored.
- Comments:
  - Block comments: any text between `{` and `}` is ignored.
  - Line comments: if a line starts with `%%`, the rest of the line is ignored.
- Numbers: a sequence of digits forms an integer; a sequence with a single `.` forms a float, e.g., `12`, `3.0`.
- Identifiers and reserved words are case-sensitive.

## Grammar (informal)

- program → stmt-seq
- stmt-seq → stmt { `;` stmt }
- stmt → if-stmt | repeat-stmt | assign-stmt | read-stmt | write-stmt
- if-stmt → `if` exp `then` stmt-seq [ `else` stmt-seq ] `end`
- repeat-stmt → `repeat` stmt-seq `until` exp
- assign-stmt → identifier `:=` exp
- read-stmt → `read` identifier
- write-stmt → `write` exp
- exp → simple-exp [ comparison-op simple-exp ]
- comparison-op → `<` | `=`
- simple-exp → term { addop term }
- addop → `+` | `-`
- term → factor { mulop factor }
- mulop → `*` | `/`
- factor → `(` exp `)` | number | identifier

## Types

- Primitive types: `int`, `float`.
- Implicit conversions:
  - `int` can be promoted to `float` in mixed expressions.
  - Assignments convert RHS to LHS type if safe; otherwise, report a semantic error.

## Semantic rules

- Variables must be declared on first assignment; their type is inferred from the first assigned expression, unless a prior declaration feature is added.
- Type checking:
  - Arithmetic ops on `int` + `float` produce `float`.
  - Comparison ops yield a boolean (internal type used for control flow conditions).
- Scope: single global scope for the project unless extended.

## Example source

```
y := x*2.0 + z*3.0 * r;
write y;
```
