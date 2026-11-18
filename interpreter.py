"""Small, deliberately restricted interpreter for the ASAAN starter grammar."""
from __future__ import annotations
import ast
import re
from pathlib import Path

class AsaanError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"ASAAN ERROR on line {line}: {message}")
        self.line = line
        self.message = message

class Interpreter:
    def __init__(self, input_fn=input, output_fn=print):
        self.env = {}
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.functions = {}

    def expression(self, source: str, line: int):
        source = source.strip()
        source = re.sub(r'\bT\b', 'True', source)
        source = re.sub(r'\bF\b', 'False', source)
        source = source.replace(" && ", " and ").replace(" || ", " or ")
        try:
            tree = ast.parse(source, mode="eval")
            return self._eval(tree.body, line)
        except AsaanError:
            raise
        except Exception as exc:
            raise AsaanError(f"invalid expression: {exc}", line) from exc

    def _eval(self, node, line):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in self.env:
                raise AsaanError(f"undefined variable '{node.id}'", line)
            return self.env[node.id]
        if isinstance(node, ast.List):
            return [self._eval(x, line) for x in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self._eval(x, line) for x in node.elts)
        if isinstance(node, ast.Dict):
            return {self._eval(k, line): self._eval(v, line) for k, v in zip(node.keys, node.values)}
        if isinstance(node, ast.BinOp):
            a, b = self._eval(node.left, line), self._eval(node.right, line)
            ops = {ast.Add: lambda:a+b, ast.Sub:lambda:a-b, ast.Mult:lambda:a*b,
                   ast.Div:lambda:a/b, ast.FloorDiv:lambda:a//b, ast.Mod:lambda:a%b,
                   ast.Pow:lambda:a**b}
            for typ, fn in ops.items():
                if isinstance(node.op, typ):
                    try: return fn()
                    except Exception as exc: raise AsaanError(str(exc), line) from exc
            raise AsaanError("operator not supported", line)
        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand, line)
            if isinstance(node.op, ast.USub): return -value
            if isinstance(node.op, ast.UAdd): return +value
            if isinstance(node.op, ast.Not): return not value
        if isinstance(node, ast.BoolOp):
            vals = [self._eval(v, line) for v in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)
        if isinstance(node, ast.Compare):
            left = self._eval(node.left, line)
            for op, comp in zip(node.ops, node.comparators):
                right = self._eval(comp, line)
                checks = {ast.Eq: left == right, ast.NotEq: left != right,
                          ast.Lt: left < right, ast.LtE: left <= right,
                          ast.Gt: left > right, ast.GtE: left >= right,
                          ast.In: left in right, ast.NotIn: left not in right}
                if type(op) not in checks or not checks[type(op)]: return False
                left = right
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            funcs = {"str":str, "int":int, "len":len, "bool":bool, "abs":abs,
                     "min":min, "max":max, "round":round}
            if node.func.id not in funcs:
                raise AsaanError(f"function '{node.func.id}' is not available", line)
            return funcs[node.func.id](*[self._eval(a, line) for a in node.args])
        raise AsaanError(f"expression feature '{type(node).__name__}' is not supported yet", line)

    def execute(self, source: str):
        lines = source.splitlines()
        self._block(lines, 0, 0)
        return self.env

    def _block(self, lines, start, indent):
        i = start
        while i < len(lines):
            raw = lines[i]
            if not raw.strip() or raw.lstrip().startswith("#"):
                i += 1; continue
            current = len(raw) - len(raw.lstrip(" "))
            if current < indent: return i
            if current > indent:
                raise AsaanError("unexpected indentation", i+1)
            s = raw.strip()
            if s in ("else:",) or s.startswith("elif "):
                return i
            if s.startswith("if ") and s.endswith(":"):
                condition = s[3:-1]
                body_start = i + 1
                body_end = self._find_end(lines, body_start, indent)
                if self.expression(condition, i+1):
                    self._block(lines, body_start, indent+4)
                    i = body_end
                    # skip optional else/elif chain for this initial implementation
                    if i < len(lines) and lines[i].strip() == "else:":
                        i = self._find_end(lines, i+1, indent)
                    continue
                i = body_end
                if i < len(lines) and lines[i].strip() == "else:":
                    i = self._block(lines, i+1, indent+4)
                    continue
                continue
            m = re.match(r"var\.([A-Za-z_]\w*)/([A-Za-z]+)\s*=\s*(.+)$", s)
            if m:
                name, typ, expr = m.groups()
                value = self.expression(expr, i+1)
                converters = {"int":int, "str":str, "bol":bool, "list":list, "dec":float,
                              "auto":lambda x:x, "map":dict}
                if typ not in converters:
                    raise AsaanError(f"unknown type '{typ}'", i+1)
                try: value = converters[typ](value)
                except Exception:
                    raise AsaanError(f"cannot assign {type(value).__name__} to {typ}", i+1)
                self.env[name] = value; i += 1; continue
            if s.startswith("print:"):
                self.output_fn(self.expression(s[6:], i+1)); i += 1; continue
            if s.startswith("input:"):
                m = re.match(r'input:\s*var\.([A-Za-z_]\w*)/(\w+)\s*=\s*(.+)', s)
                if not m: raise AsaanError("expected input: var.name/type = prompt", i+1)
                name, typ, prompt = m.groups()
                self.env[name] = self.input_fn(str(self.expression(prompt, i+1)))
                if typ == "int":
                    try: self.env[name] = int(self.env[name])
                    except ValueError: raise AsaanError("input is not a valid integer", i+1)
                i += 1; continue
            if s.startswith("calc.calculate |"):
                self.env["calculate"] = self.expression(s.split("|",1)[1], i+1)
                i += 1; continue
            if s.startswith("for ") and s.endswith(":"):
                m = re.match(r"for\s+var\.([A-Za-z_]\w*)/\w+\s+in\s+(-?\d+)\.\.(-?\d+):", s)
                if not m: raise AsaanError("supported loop form: for var.i/int in 1..5:", i+1)
                name, a, b = m.groups()
                body_start = i+1; body_end = self._find_end(lines, body_start, indent)
                for value in range(int(a), int(b)+1):
                    self.env[name] = value
                    self._block(lines[body_start:body_end], 0, indent+4)
                i = body_end; continue
            if s.startswith("while ") and s.endswith(":"):
                raise AsaanError("while loops are planned; use a for loop in this prototype", i+1)
            raise AsaanError(f"unrecognized statement: {s}", i+1)
        return i

    def _find_end(self, lines, start, parent_indent):
        i = start
        while i < len(lines):
            raw = lines[i]
            if raw.strip() and not raw.lstrip().startswith("#"):
                level = len(raw) - len(raw.lstrip(" "))
                if level <= parent_indent: break
            i += 1
        return i

def run_file(path):
    source = Path(path).read_text(encoding="utf-8")
    Interpreter().execute(source)

def check_file(path):
    source = Path(path).read_text(encoding="utf-8")
    # Validate by executing with output/input suppressed; this is a prototype check.
    Interpreter(input_fn=lambda _: "", output_fn=lambda *_: None).execute(source)
