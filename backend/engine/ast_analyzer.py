import ast
import math
import re
from typing import List, Dict, Any, Tuple
import uuid

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, filename: str, source_code: str):
        self.filename = filename
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.issues: List[Dict[str, Any]] = []
        self.complexity = 1
        self.imports = []
        self.functions_count = 0
        self.classes_count = 0
        self.current_function = None
        self.in_loop_depth = 0
        self.has_recursion = False
        self.calls_in_function = []
        self.identifiers = set()
        self.operators_count = 0
        self.operands_count = 0

    def analyze(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        try:
            tree = ast.parse(self.source_code, filename=self.filename)
            self.visit(tree)
        except SyntaxError as e:
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": e.lineno or 1,
                "end_line": e.lineno or 1,
                "column": e.offset or 1,
                "category": "bug",
                "severity": "critical",
                "title": f"Syntax Error: {e.msg}",
                "description": f"Code fails to parse due to a syntax error: {e.msg}",
                "impact": "Code cannot be executed or compiled; causes immediate crash at runtime.",
                "rule_id": "SYNTAX-001",
                "original_code": self.lines[e.lineno - 1] if e.lineno and e.lineno <= len(self.lines) else "",
                "suggested_fix": "# Correct the syntax error on this line",
                "explanation": "Python parser halted on invalid token/syntax. Ensure brackets, colons, and indentation match.",
                "diff": None,
                "confidence": 1.0
            })
            return self.issues, self._get_fallback_metrics()
        except Exception as e:
            pass

        metrics = self._calculate_metrics()
        return self.issues, metrics

    def _get_snippet(self, start_line: int, end_line: int = None) -> str:
        if end_line is None:
            end_line = start_line
        start = max(0, start_line - 1)
        end = min(len(self.lines), end_line)
        return "\n".join(self.lines[start:end])

    def _make_diff(self, old_code: str, new_code: str) -> str:
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        diff = []
        for l in old_lines:
            diff.append(f"- {l}")
        for l in new_lines:
            diff.append(f"+ {l}")
        return "\n".join(diff)

    # Complexity counters
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.in_loop_depth += 1
        self._check_loop_inefficiency(node)
        self.generic_visit(node)
        self.in_loop_depth -= 1

    def visit_While(self, node):
        self.complexity += 1
        self.in_loop_depth += 1
        self._check_loop_inefficiency(node)
        self.generic_visit(node)
        self.in_loop_depth -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        # Check for broad except / bare except
        if node.type is None or (isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException")):
            # Check if body only has 'pass'
            is_silent = False
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                is_silent = True
            
            orig = self._get_snippet(node.lineno)
            fix = "    except SpecificError as e:\n        logger.error(f'Handled error: {e}')"
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "end_line": node.lineno + len(node.body),
                "column": node.col_offset + 1,
                "category": "bug" if is_silent else "maintainability",
                "severity": "high" if is_silent else "medium",
                "title": "Silent / Overly Broad Exception Swallowing" if is_silent else "Broad Exception Catch",
                "description": "Catching generic 'Exception' or bare 'except:' masks critical errors (e.g. KeyboardInterrupt, MemoryError, NameError) and hinders debugging.",
                "impact": "Bugs fail silently without logging; system may enter inconsistent or corrupted state.",
                "rule_id": "ERR-BROAD-EXCEPT",
                "original_code": orig,
                "suggested_fix": fix,
                "explanation": "Catch specific exceptions (e.g. ValueError, KeyError, requests.RequestException) and at minimum log the traceback.",
                "diff": self._make_diff(orig, fix),
                "confidence": 0.96
            })
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
            # Check unsafe imports
            if alias.name == "telnetlib":
                orig = self._get_snippet(node.lineno)
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "category": "security",
                    "severity": "high",
                    "title": "Insecure Protocol Import (telnetlib)",
                    "description": "telnetlib uses unencrypted plaintext protocols vulnerable to sniffing and MITM attacks.",
                    "impact": "Credentials and commands transmitted in cleartext over the network.",
                    "rule_id": "SEC-INSECURE-PROTO",
                    "original_code": orig,
                    "suggested_fix": "import paramiko  # Or use SSH/TLS equivalent",
                    "explanation": "Replace unencrypted telnet with an encrypted SSH/TLS client.",
                    "diff": self._make_diff(orig, "import paramiko"),
                    "confidence": 0.99
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions_count += 1
        prev_func = self.current_function
        self.current_function = node.name
        self.calls_in_function = []

        # Check mutable default arguments: def foo(x=[])
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                orig = self._get_snippet(node.lineno)
                fix = f"def {node.name}(..., param=None):\n    if param is None:\n        param = []"
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "category": "bug",
                    "severity": "high",
                    "title": "Mutable Default Argument in Function Definition",
                    "description": f"Function '{node.name}' uses a mutable default argument (list/dict/set). Python creates default objects once at definition time, causing state to persist across calls.",
                    "impact": "Data leaks between function calls; erratic mutations cause subtle bugs.",
                    "rule_id": "BUG-MUTABLE-DEFAULT",
                    "original_code": orig,
                    "suggested_fix": fix,
                    "explanation": "Use `None` as the default argument value and initialize the collection inside the function body.",
                    "diff": self._make_diff(orig, fix),
                    "confidence": 0.99
                })

        self.generic_visit(node)

        # Check recursive calls in function
        if node.name in self.calls_in_function:
            self.has_recursion = True
            # Check if multiple recursive calls in same function (like fib(n-1) + fib(n-2) -> O(2^n))
            rec_count = self.calls_in_function.count(node.name)
            if rec_count >= 2:
                orig = self._get_snippet(node.lineno, min(node.lineno + 8, len(self.lines)))
                fix = f"from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef {node.name}(...):  # Or rewrite iteratively for O(1) space"
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "category": "efficiency",
                    "severity": "critical",
                    "title": f"Exponential Recursive Branching O(2^N) in '{node.name}'",
                    "description": f"Function '{node.name}' performs {rec_count} recursive calls per step without memoization, resulting in O(2^N) exponential time complexity.",
                    "impact": "Execution time blows up exponentially for N > 35, freezing the server and exceeding maximum call stack recursion depth.",
                    "rule_id": "PERF-EXPONENTIAL-RECURSION",
                    "original_code": orig,
                    "suggested_fix": fix,
                    "explanation": "Add `@functools.lru_cache` for O(N) memoization or convert to an iterative algorithm for O(1) space and O(N) time.",
                    "diff": self._make_diff(orig, fix),
                    "confidence": 0.98
                })

        self.current_function = prev_func

    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                full_name = f"{node.func.value.id}.{node.func.attr}"
                self._check_security_calls(full_name, node)

        if self.current_function and func_name:
            self.calls_in_function.append(func_name)

        # Direct calls: eval, exec, open
        if func_name == "eval":
            orig = self._get_snippet(node.lineno)
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "critical",
                "title": "Dangerous Use of eval() - Arbitrary Code Execution",
                "description": "Direct use of `eval()` can execute arbitrary Python commands if passed unverified user input.",
                "impact": "Remote Code Execution (RCE); complete system takeover.",
                "rule_id": "SEC-RCE-EVAL",
                "original_code": orig,
                "suggested_fix": "import ast\nparsed_value = ast.literal_eval(user_data)  # Safe literal evaluation",
                "explanation": "Use `ast.literal_eval()` for safely parsing Python literals, or use strict schema parsing (json/pydantic).",
                "diff": self._make_diff(orig, "ast.literal_eval(...)"),
                "confidence": 0.99
            })

        elif func_name == "exec":
            orig = self._get_snippet(node.lineno)
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "critical",
                "title": "Use of exec() - Dynamic Execution Risk",
                "description": "`exec()` evaluates arbitrary dynamic code blocks, breaking static analysis and introducing severe vulnerability.",
                "impact": "Total compromise of application host environment.",
                "rule_id": "SEC-RCE-EXEC",
                "original_code": orig,
                "suggested_fix": "# Refactor to static functions or a sandboxed dispatch table",
                "explanation": "Avoid dynamic code execution entirely by structuring logic with dictionaries or dispatcher functions.",
                "diff": None,
                "confidence": 0.99
            })

        # Check SQL Injection on database methods (SQLite, PostgreSQL, MySQL, Oracle, SQLAlchemy)
        db_exec_methods = ("execute", "executemany", "raw", "raw_query", "text", "query")
        if func_name in db_exec_methods:
            self._check_sql_injection(node)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in db_exec_methods:
            self._check_sql_injection(node)

        # Check NoSQL Injection on MongoDB collection methods
        nosql_methods = ("find", "find_one", "aggregate", "delete_many", "update_many", "count_documents")
        if func_name in nosql_methods or (isinstance(node.func, ast.Attribute) and node.func.attr in nosql_methods):
            self._check_nosql_injection(node)

        # Check resource leak: open() not inside with statement
        if func_name == "open" and not self._is_inside_with(node):
            orig = self._get_snippet(node.lineno)
            fix = "with open('filename', 'r') as f:\n    content = f.read()"
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "bug",
                "severity": "medium",
                "title": "Unclosed File Resource Leak (open without 'with')",
                "description": "Calling `open()` without a `with` context manager risks keeping file descriptors open if an exception occurs.",
                "impact": "Exhaustion of OS file descriptors, file lock contentions, and resource leaks.",
                "rule_id": "RES-UNCLOSED-FILE",
                "original_code": orig,
                "suggested_fix": fix,
                "explanation": "Always wrap file operations in a `with open(...) as f:` block to guarantee automatic closure.",
                "diff": self._make_diff(orig, fix),
                "confidence": 0.92
            })

        self.generic_visit(node)

    def _is_inside_with(self, node) -> bool:
        # Heuristic check: check line above or line itself for "with open"
        line_idx = node.lineno - 1
        if 0 <= line_idx < len(self.lines):
            line_str = self.lines[line_idx].strip()
            if line_str.startswith("with open") or "with " in line_str:
                return True
        return False

    def _check_security_calls(self, full_name: str, node: ast.Call):
        orig = self._get_snippet(node.lineno)

        # Command injection: os.system, subprocess.Popen(..., shell=True)
        if full_name == "os.system":
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "critical",
                "title": "Command Injection Risk via os.system()",
                "description": "`os.system()` runs commands in a system shell without sanitization, permitting command chaining (`&&`, `;`, `|`).",
                "impact": "Attacker can execute arbitrary shell commands with the application's privileges.",
                "rule_id": "SEC-CMD-INJECTION",
                "original_code": orig,
                "suggested_fix": "import subprocess\nsubprocess.run(['command', arg1, arg2], check=True, shell=False)",
                "explanation": "Use `subprocess.run()` with a list of arguments and `shell=False` to prevent shell metacharacter expansion.",
                "diff": self._make_diff(orig, "subprocess.run(['cmd', arg], shell=False)"),
                "confidence": 0.98
            })

        elif full_name in ("subprocess.Popen", "subprocess.call", "subprocess.run"):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.issues.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": self.filename,
                        "line": node.lineno,
                        "column": node.col_offset + 1,
                        "category": "security",
                        "severity": "high",
                        "title": "Subprocess Invoked with shell=True",
                        "description": "Passing `shell=True` to subprocess functions enables shell interpolation vulnerabilities.",
                        "impact": "Permits injection of malicious command flags or secondary commands.",
                        "rule_id": "SEC-SUBPROCESS-SHELL",
                        "original_code": orig,
                        "suggested_fix": "subprocess.run(['executable', param], shell=False)",
                        "explanation": "Set `shell=False` and supply command arguments as an array of strings.",
                        "diff": self._make_diff(orig, orig.replace("shell=True", "shell=False")),
                        "confidence": 0.99
                    })

        # Insecure deserialization: pickle.loads, pickle.load
        elif full_name in ("pickle.loads", "pickle.load", "_pickle.loads"):
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "critical",
                "title": "Insecure Deserialization via pickle",
                "description": "`pickle` deserialization executes arbitrary bytecode embedded in pickled streams (`__reduce__`).",
                "impact": "Remote code execution if untrusted or external input is deserialized.",
                "rule_id": "SEC-INSECURE-DESERIALIZATION",
                "original_code": orig,
                "suggested_fix": "import json\ndata = json.loads(payload)",
                "explanation": "Never deserialize untrusted data with pickle. Use JSON, MessagePack, or Protocol Buffers.",
                "diff": self._make_diff(orig, "json.loads(payload)"),
                "confidence": 0.98
            })

        # Weak cryptographic hashing: hashlib.md5, hashlib.sha1
        elif full_name in ("hashlib.md5", "hashlib.sha1"):
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "medium",
                "title": f"Weak Cryptographic Hash Function ({full_name})",
                "description": f"{full_name} is cryptographically broken and vulnerable to collision and preimage attacks.",
                "impact": "Compromised integrity verification; inadequate for password hashing or cryptographic signatures.",
                "rule_id": "SEC-WEAK-HASH",
                "original_code": orig,
                "suggested_fix": "import hashlib\nhashlib.sha256(data).hexdigest()  # Or bcrypt/argon2 for passwords",
                "explanation": "Use SHA-256 / SHA-3 for digests, or Argon2id / bcrypt for password storage.",
                "diff": self._make_diff(orig, orig.replace("md5", "sha256").replace("sha1", "sha256")),
                "confidence": 0.95
            })

    def _check_sql_injection(self, node: ast.Call):
        if not node.args:
            return
        first_arg = node.args[0]
        orig = self._get_snippet(node.lineno)

        def _is_dynamic_sql(target_node):
            if isinstance(target_node, ast.JoinedStr):
                return True
            if isinstance(target_node, ast.BinOp) and isinstance(target_node.op, (ast.Add, ast.Mod)):
                return True
            if isinstance(target_node, ast.Call):
                if isinstance(target_node.func, ast.Attribute) and target_node.func.attr == "format":
                    return True
                if target_node.args and _is_dynamic_sql(target_node.args[0]):
                    return True
            return False

        if _is_dynamic_sql(first_arg):
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "critical",
                "title": "SQL Injection via Dynamic String Formatting",
                "description": "SQL query is composed using string concatenation, f-strings, or format() instead of parameterized queries (CWE-89).",
                "impact": "Data exfiltration, unauthorized database writes, authentication bypass, or full database drop.",
                "rule_id": "SEC-SQL-INJECTION",
                "original_code": orig,
                "suggested_fix": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                "explanation": "Always pass SQL parameters separately using database driver parameter markers (`%s` for PostgreSQL/MySQL, `?` for SQLite, `:param` for Oracle/SQLAlchemy) to enforce automatic quoting and type safety.",
                "diff": self._make_diff(orig, "cursor.execute('SELECT ... WHERE id = %s', (param,))"),
                "confidence": 0.99
            })

    def _check_nosql_injection(self, node: ast.Call):
        orig = self._get_snippet(node.lineno)
        has_nosqli = False
        for child in ast.walk(node):
            val = getattr(child, "value", None)
            if val == "$where":
                has_nosqli = True
                break

        if has_nosqli:
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "security",
                "severity": "critical",
                "title": "NoSQL Injection via $where Expression",
                "description": "MongoDB $where executes arbitrary JavaScript expressions. Dynamic string interpolation allows arbitrary script execution (CWE-943).",
                "impact": "Remote JavaScript execution inside the database engine, database exfiltration, authentication bypass.",
                "rule_id": "SEC-NOSQL-INJECTION",
                "original_code": orig,
                "suggested_fix": "db.collection.find({'field': value})  # Use standard declarative query operators",
                "explanation": "Avoid $where with untrusted input; use standard MongoDB query operators ($eq, $in) or parameterize queries.",
                "diff": self._make_diff(orig, "db.collection.find({'key': value})"),
                "confidence": 0.98
            })

    def _check_loop_inefficiency(self, node):
        # Check nested loops (O(n^2), O(n^3))
        if self.in_loop_depth >= 2:
            orig = self._get_snippet(node.lineno)
            self.issues.append({
                "id": str(uuid.uuid4())[:8],
                "file": self.filename,
                "line": node.lineno,
                "column": node.col_offset + 1,
                "category": "efficiency",
                "severity": "high" if self.in_loop_depth == 2 else "critical",
                "title": f"Nested Loop Detected: Quadratic O(N^{self.in_loop_depth}) Complexity",
                "description": f"Encountered loop nesting depth of {self.in_loop_depth}. For large inputs N, execution requires O(N^{self.in_loop_depth}) operations.",
                "impact": "Drastic performance degradation when processing collections exceeding 1,000 items.",
                "rule_id": f"PERF-NESTED-LOOP-DEPTH-{self.in_loop_depth}",
                "original_code": orig,
                "suggested_fix": "# Consider using a Hash Map, Set lookup (O(1)), or vectorized operations",
                "explanation": "Replace nested linear scans with a dictionary lookup or pre-sorted binary search to drop complexity to O(N) or O(N log N).",
                "diff": None,
                "confidence": 0.93
            })

        # Check string concatenation inside loop: s += ...
        for child in ast.walk(node):
            if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                if isinstance(child.target, ast.Name):
                    orig = self._get_snippet(child.lineno)
                    self.issues.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": self.filename,
                        "line": child.lineno,
                        "column": child.col_offset + 1,
                        "category": "efficiency",
                        "severity": "medium",
                        "title": "Quadratic String Concatenation in Loop (s += item)",
                        "description": "Strings are immutable in Python. Concatenating strings in a loop reallocates memory and copies the entire string each iteration, resulting in O(N^2) memory copies.",
                        "impact": "Excessive CPU and GC churn when building large strings.",
                        "rule_id": "PERF-STRING-CONCAT-LOOP",
                        "original_code": orig,
                        "suggested_fix": "parts = []\nfor item in items:\n    parts.append(str(item))\nresult = ''.join(parts)",
                        "explanation": "Collect elements into a list and use `''.join(parts)` for linear O(N) allocation.",
                        "diff": self._make_diff(orig, "parts.append(item)  # then ''.join(parts)"),
                        "confidence": 0.94
                    })

    def visit_Assign(self, node):
        # Check hardcoded secrets: password = "...", api_key = "...", secret = "..."
        for target in node.targets:
            if isinstance(target, ast.Name):
                name_lower = target.id.lower()
                if any(k in name_lower for k in ("secret", "password", "api_key", "token", "auth_key", "private_key", "jwt", "_key")):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        val = node.value.value
                        if len(val) >= 6 and not val.startswith("ENV_") and not val.startswith("$"):
                            orig = self._get_snippet(node.lineno)
                            fix = f"{target.id} = os.getenv('{target.id.upper()}')"
                            self.issues.append({
                                "id": str(uuid.uuid4())[:8],
                                "file": self.filename,
                                "line": node.lineno,
                                "column": node.col_offset + 1,
                                "category": "security",
                                "severity": "critical",
                                "title": f"Hardcoded Credential / Secret in Variable '{target.id}'",
                                "description": f"Plaintext secret or key '{target.id}' is stored directly in source code.",
                                "impact": "Secret will leak to version control, logs, or unauthorized third parties.",
                                "rule_id": "SEC-HARDCODED-SECRET",
                                "original_code": orig,
                                "suggested_fix": fix,
                                "explanation": "Store credentials in environment variables or a secure secret manager (e.g. AWS Secrets Manager, HashiCorp Vault).",
                                "diff": self._make_diff(orig, fix),
                                "confidence": 0.99
                            })
        self.generic_visit(node)

    def _calculate_metrics(self) -> Dict[str, Any]:
        total_lines = len(self.lines)
        blank_lines = sum(1 for l in self.lines if not l.strip())
        comment_lines = sum(1 for l in self.lines if l.strip().startswith("#"))
        loc = max(1, total_lines - blank_lines - comment_lines)

        # Halstead & Maintainability Index estimation
        # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(LOC)
        # Bounded between 0 and 100
        vol = max(1.0, float(loc * 3.5))
        cyclomatic = max(1, self.complexity)
        try:
            mi_raw = 171.0 - 5.2 * math.log(vol) - 0.23 * cyclomatic - 16.2 * math.log(loc)
            mi = max(0.0, min(100.0, (mi_raw * 100.0 / 171.0)))
        except Exception:
            mi = 75.0

        critical_count = sum(1 for i in self.issues if i["severity"] == "critical")
        high_count = sum(1 for i in self.issues if i["severity"] == "high")

        if critical_count > 0:
            risk = "critical"
        elif high_count > 0 or mi < 50:
            risk = "high"
        elif len(self.issues) > 3 or mi < 70:
            risk = "medium"
        else:
            risk = "low"

        return {
            "loc": loc,
            "total_lines": total_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "cyclomatic_complexity": cyclomatic,
            "maintainability_index": round(mi, 1),
            "issues_count": len(self.issues),
            "critical_issues": critical_count,
            "risk_level": risk,
            "imports": list(set(self.imports)),
            "functions_count": self.functions_count,
            "classes_count": self.classes_count,
            "has_recursion": self.has_recursion
        }

    def _get_fallback_metrics(self) -> Dict[str, Any]:
        return {
            "loc": len(self.lines),
            "total_lines": len(self.lines),
            "blank_lines": 0,
            "comment_lines": 0,
            "cyclomatic_complexity": 5,
            "maintainability_index": 30.0,
            "issues_count": len(self.issues),
            "critical_issues": 1,
            "risk_level": "critical",
            "imports": [],
            "functions_count": 0,
            "classes_count": 0,
            "has_recursion": False
        }
