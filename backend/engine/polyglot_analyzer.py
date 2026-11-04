import re
import math
import uuid
from typing import List, Dict, Any, Tuple

class PolyglotAnalyzer:
    def __init__(self, filename: str, content: str, language: str):
        self.filename = filename
        self.content = content
        self.language = language.lower()
        self.lines = content.splitlines()
        self.issues: List[Dict[str, Any]] = []

    def analyze(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        self._check_hardcoded_secrets()
        self._check_insecure_urls()

        if self.language in ("javascript", "typescript", "js", "ts", "jsx", "tsx"):
            self._analyze_js_ts()
        elif self.language in ("java",):
            self._analyze_java()
        elif self.language in ("c", "cpp", "c++"):
            self._analyze_cpp()

        metrics = self._calculate_metrics()
        return self.issues, metrics

    def _get_snippet(self, line_num: int) -> str:
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1]
        return ""

    def _make_diff(self, old_code: str, new_code: str) -> str:
        return f"- {old_code}\n+ {new_code}"

    def _check_hardcoded_secrets(self):
        # AWS Key pattern (supports production patterns and safe mock test keys)
        aws_regex = re.compile(r'(AKIA[0-9A-Z]{16}|MOCK_AWS_KEY_[0-9A-Z]{10})')
        # Generic API key pattern
        api_key_regex = re.compile(r'''(?i)(api[_-]?key|secret|token|password|auth_token)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{12,})["']''')

        for idx, line in enumerate(self.lines, 1):
            if line.strip().startswith("//") or line.strip().startswith("#"):
                continue

            aws_match = aws_regex.search(line)
            if aws_match:
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": aws_match.start() + 1,
                    "category": "security",
                    "severity": "critical",
                    "title": "AWS Access Key Exposed in Source Code",
                    "description": "Hardcoded AWS Access Key ID detected. Committing credentials risks total cloud account compromise.",
                    "impact": "Unauthorized AWS infrastructure access, cloud resource hijacking, and billing extortion.",
                    "rule_id": "SEC-AWS-CREDENTIAL",
                    "original_code": line.strip(),
                    "suggested_fix": "process.env.AWS_ACCESS_KEY_ID",
                    "explanation": "Store credentials exclusively in server-side environment variables or IAM roles.",
                    "diff": self._make_diff(line.strip(), "const key = process.env.AWS_ACCESS_KEY_ID;"),
                    "confidence": 0.99
                })

            secret_match = api_key_regex.search(line)
            if secret_match and not any(kw in line.lower() for kw in ("dummy", "example", "placeholder", "test")):
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": secret_match.start() + 1,
                    "category": "security",
                    "severity": "high",
                    "title": f"Hardcoded Credential in '{secret_match.group(1)}'",
                    "description": "Sensitive credential string hardcoded directly in application source code.",
                    "impact": "Credential leakage via git history, client-side bundles, or third-party audits.",
                    "rule_id": "SEC-HARDCODED-SECRET",
                    "original_code": line.strip(),
                    "suggested_fix": f"{secret_match.group(1)}: process.env.{secret_match.group(1).upper()}",
                    "explanation": "Extract sensitive values to secure environment configuration (`.env`).",
                    "diff": self._make_diff(line.strip(), f"// Read from process.env.{secret_match.group(1).upper()}"),
                    "confidence": 0.94
                })

    def _check_insecure_urls(self):
        insecure_http = re.compile(r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)([a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})')
        for idx, line in enumerate(self.lines, 1):
            if "http://" in line and not line.strip().startswith("//"):
                match = insecure_http.search(line)
                if match:
                    self.issues.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": self.filename,
                        "line": idx,
                        "column": match.start() + 1,
                        "category": "security",
                        "severity": "medium",
                        "title": f"Insecure Plaintext HTTP URL: {match.group(0)}",
                        "description": "Communication over unencrypted HTTP exposes data and session cookies to eavesdropping and tampering.",
                        "impact": "Man-in-the-Middle (MITM) attacks; session hijacking.",
                        "rule_id": "SEC-INSECURE-HTTP",
                        "original_code": line.strip(),
                        "suggested_fix": line.strip().replace("http://", "https://"),
                        "explanation": "Enforce HTTPS for all external API endpoints and network communications.",
                        "diff": self._make_diff(line.strip(), line.strip().replace("http://", "https://")),
                        "confidence": 0.91
                    })

    def _analyze_js_ts(self):
        loop_depth = 0
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue

            # XSS: innerHTML
            if ".innerHTML" in stripped and "=" in stripped:
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": line.find(".innerHTML") + 1,
                    "category": "security",
                    "severity": "high",
                    "title": "Cross-Site Scripting (XSS) via innerHTML",
                    "description": "Assigning unescaped data to `innerHTML` permits execution of malicious client-side JavaScript.",
                    "impact": "Session token theft, credential harvesting, unauthorized user actions in browser.",
                    "rule_id": "SEC-DOM-XSS",
                    "original_code": stripped,
                    "suggested_fix": stripped.replace(".innerHTML", ".textContent"),
                    "explanation": "Use `textContent` to render plain text safely, or sanitize HTML using DOMPurify before rendering.",
                    "diff": self._make_diff(stripped, stripped.replace(".innerHTML", ".textContent")),
                    "confidence": 0.97
                })

            # Dangerous eval
            if re.search(r'\beval\(', stripped):
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": stripped.find("eval(") + 1,
                    "category": "security",
                    "severity": "critical",
                    "title": "Arbitrary Code Execution via eval()",
                    "description": "`eval()` parses strings as JavaScript code, introducing high vulnerability and disabling V8 optimizations.",
                    "impact": "Arbitrary client-side or server-side code execution.",
                    "rule_id": "SEC-EVAL-JS",
                    "original_code": stripped,
                    "suggested_fix": "JSON.parse(data)",
                    "explanation": "Replace `eval()` with `JSON.parse()` or dedicated declarative expression parsers.",
                    "diff": self._make_diff(stripped, "const result = JSON.parse(sanitizedPayload);"),
                    "confidence": 0.99
                })

            # Loose equality: == instead of ===
            if re.search(r'[^=!<>]={2}[^=]', stripped) and not stripped.startswith("for ("):
                # filter out '=='
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": stripped.find("==") + 1,
                    "category": "bug",
                    "severity": "low",
                    "title": "Loose Equality Operator (==)",
                    "description": "The loose equality operator performs implicit type coercion, causing unpredictable behavior (e.g. `0 == ''` is true).",
                    "impact": "Subtle logic bugs caused by unexpected type coercion.",
                    "rule_id": "STYLE-LOOSE-EQUALITY",
                    "original_code": stripped,
                    "suggested_fix": stripped.replace("==", "==="),
                    "explanation": "Use strict equality `===` and `!==` to compare both value and type reliably.",
                    "diff": self._make_diff(stripped, stripped.replace("==", "===")),
                    "confidence": 0.92
                })

            # Missing await on async function or fetch
            if re.search(r'\bfetch\(', stripped) and "await" not in stripped and "then" not in stripped and "=" in stripped:
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": stripped.find("fetch(") + 1,
                    "category": "bug",
                    "severity": "high",
                    "title": "Unawaited Promise on fetch()",
                    "description": "`fetch()` returns a Promise. Assigning it without `await` or `.then()` assigns the pending Promise rather than response data.",
                    "impact": "Code reads properties of pending Promise (`undefined` runtime bugs) and ignores network errors.",
                    "rule_id": "BUG-UNAWAITED-PROMISE",
                    "original_code": stripped,
                    "suggested_fix": stripped.replace("fetch(", "await fetch("),
                    "explanation": "Always `await` asynchronous calls inside async functions or handle with `.then().catch()`.",
                    "diff": self._make_diff(stripped, stripped.replace("fetch(", "await fetch(")),
                    "confidence": 0.93
                })

            # Node.js Database Query SQL Injection (query, execute, raw, rawQuery)
            if re.search(r'\b(query|execute|raw|rawQuery)\s*\(', stripped):
                is_sql_call = any(kw in stripped.upper() for kw in ("SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "FROM"))
                if is_sql_call and (("`" in stripped and "${" in stripped) or ("+" in stripped and ("'" in stripped or '"' in stripped))):
                    self.issues.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": self.filename,
                        "line": idx,
                        "column": 1,
                        "category": "security",
                        "severity": "critical",
                        "title": "SQL Injection in Database Query",
                        "description": "Database query composed using string concatenation or template literal interpolation instead of parameterized placeholders.",
                        "impact": "Data exfiltration, unauthorized database writes, authentication bypass.",
                        "rule_id": "SEC-SQL-INJECTION",
                        "original_code": stripped,
                        "suggested_fix": "pool.query('SELECT * FROM tbl WHERE id = $1', [id])",
                        "explanation": "Use parameterized queries ($1, ?, :param) or ORM parameter binding.",
                        "diff": self._make_diff(stripped, "pool.query('SELECT ... WHERE id = $1', [param]);"),
                        "confidence": 0.98
                    })

            # Node.js MongoDB NoSQL Injection ($where)
            if "$where" in stripped and ("+" in stripped or "${" in stripped):
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": stripped.find("$where") + 1,
                    "category": "security",
                    "severity": "critical",
                    "title": "NoSQL Injection via $where Clause",
                    "description": "MongoDB $where executes arbitrary JavaScript expressions. String concatenation permits arbitrary JavaScript injection.",
                    "impact": "Remote JavaScript code execution, database breach.",
                    "rule_id": "SEC-NOSQL-INJECTION",
                    "original_code": stripped,
                    "suggested_fix": "collection.find({ field: value })",
                    "explanation": "Use declarative query filters instead of $where string concatenation.",
                    "diff": self._make_diff(stripped, "collection.find({ field: value });"),
                    "confidence": 0.98
                })

    def _analyze_java(self):
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            # SQL Injection
            if ("executeQuery(" in stripped or "executeUpdate(" in stripped) and "+" in stripped:
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": 1,
                    "category": "security",
                    "severity": "critical",
                    "title": "SQL Injection via Concatenation",
                    "description": "SQL statement built dynamically using string concatenation.",
                    "impact": "Arbitrary database access, data loss.",
                    "rule_id": "SEC-JAVA-SQLI",
                    "original_code": stripped,
                    "suggested_fix": "PreparedStatement stmt = conn.prepareStatement(\"SELECT * FROM tbl WHERE id = ?\");",
                    "explanation": "Use PreparedStatement with parameter placeholders.",
                    "diff": self._make_diff(stripped, "PreparedStatement stmt = conn.prepareStatement(...);"),
                    "confidence": 0.98
                })

    def _analyze_cpp(self):
        for idx, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if "strcpy(" in stripped or "gets(" in stripped:
                self.issues.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": self.filename,
                    "line": idx,
                    "column": 1,
                    "category": "security",
                    "severity": "critical",
                    "title": "Unsafe Buffer Operation (strcpy / gets)",
                    "description": "Functions without bounds checking introduce buffer overflow vulnerabilities.",
                    "impact": "Stack smashing, remote code execution, program crashes.",
                    "rule_id": "SEC-BUFFER-OVERFLOW",
                    "original_code": stripped,
                    "suggested_fix": "strncpy(dest, src, sizeof(dest) - 1);",
                    "explanation": "Use bounded alternatives such as `strncpy`, `snprintf`, or `std::string`.",
                    "diff": self._make_diff(stripped, "strncpy(dest, src, sizeof(dest) - 1);"),
                    "confidence": 0.99
                })

    def _calculate_metrics(self) -> Dict[str, Any]:
        total_lines = len(self.lines)
        blank_lines = sum(1 for l in self.lines if not l.strip())
        comment_lines = sum(1 for l in self.lines if l.strip().startswith("//") or l.strip().startswith("/*"))
        loc = max(1, total_lines - blank_lines - comment_lines)

        # Estimate complexity from control keywords
        keywords = ["if ", "for ", "while ", "case ", "catch ", "&&", "||"]
        complexity = 1
        for line in self.lines:
            for kw in keywords:
                complexity += line.count(kw)

        vol = max(1.0, float(loc * 3.5))
        try:
            mi_raw = 171.0 - 5.2 * math.log(vol) - 0.23 * complexity - 16.2 * math.log(loc)
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

        # Extract imported modules for JS/TS
        imports = []
        import_regex = re.compile(r'''(?:import\s+.*?\s+from\s+['"](.*?)['"]|require\(['"](.*?)['"]\))''')
        for line in self.lines:
            m = import_regex.search(line)
            if m:
                imp = m.group(1) or m.group(2)
                if imp:
                    imports.append(imp)

        return {
            "loc": loc,
            "total_lines": total_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "cyclomatic_complexity": complexity,
            "maintainability_index": round(mi, 1),
            "issues_count": len(self.issues),
            "critical_issues": critical_count,
            "risk_level": risk,
            "imports": list(set(imports)),
            "functions_count": len(re.findall(r'\bfunction\b|\bconst\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', self.content)),
            "classes_count": len(re.findall(r'\bclass\b', self.content)),
            "has_recursion": False
        }
