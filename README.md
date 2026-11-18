# ASAANIDE

**A beginner-friendly IDE and runtime for the imaginary ASAAN language.**

ASAANIDE is an early, working prototype. It includes:
- A browser-based editor with a file explorer, run/compile controls and terminal panel.
- A Python interpreter for a documented starter subset of ASAAN.
- A transpiler that converts supported ASAAN statements into Python.
- A CLI for running, compiling and checking `.asa` files.
- A starter example and tests.

> Status: prototype. It is not yet a production compiler, a native-code toolchain, or a complete implementation of every feature in the ASAAN language proposal.

## Quick start

Requirements: Python 3.10+

```bash
python -m asaan run examples/hello.asa
python -m asaan compile examples/hello.asa -o build/hello.py
python -m asaan check examples/hello.asa
python -m asaan ide
```

Then open http://127.0.0.1:8765 in your browser.

## ASAAN starter syntax

```asa
var.name/str = "World"
var.count/int = 3

print: "Hello " + name

for var.i/int in 1..count:
    print: i

calc.calculate | 6 * (2 + 3)
print: calculate
```

Supported in this prototype:
- `var.name/type = expression`
- `print: expression`
- `input: var.name/type = "prompt"`
- `if`, `elif`, `else`
- `for var.x/type in start..end`
- `while`
- `func.name | arg/type, ...:` with `return`
- `calc.calculate | expression`
- lists with literal values
- comments beginning with `#`

The interpreter uses Python's AST for expression evaluation and a restricted set of built-ins. It does not execute arbitrary Python statements.

## Project layout

```text
ASAANIDE/
├── Asaanlogo.png
├── asaan/
│   ├── __init__.py
│   ├── __main__.py
│   ├── interpreter.py
│   └── transpiler.py
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── examples/
│   └── hello.asa
├── tests/
│   └── test_interpreter.py
└── pyproject.toml
```

## Roadmap

1. Lexer and parser with a formal grammar.
2. Better diagnostics and safe automatic fixes.
3. Modules, classes, maps, richer collections and imports.
4. OS-specific system adapters with explicit permissions.
5. Java/Rust/Python interoperability bridges.
6. A real language server, debugger and native compiler backend.

## Safety

The prototype's `sys` commands are intentionally not implemented as unrestricted shell execution. Do not add arbitrary `eval`, `exec`, or shell passthrough to the runtime. Any future file, network or process API should use explicit permissions.
