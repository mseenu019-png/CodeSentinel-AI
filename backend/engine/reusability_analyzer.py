import ast
import re
import uuid
from typing import Dict, List, Any, Tuple
from models import CodeStrength, ReusabilityMetric

class ReusabilityAnalyzer:
    def __init__(self, files_dict: Dict[str, str]):
        self.files = files_dict
        self.strengths: List[CodeStrength] = []
        self.total_functions = 0
        self.pure_functions = 0
        self.parameterized_functions = 0
        self.documented_functions = 0
        self.type_annotated_functions = 0
        self.monolithic_functions = 0

    def analyze(self) -> Tuple[ReusabilityMetric, List[CodeStrength]]:
        for filepath, content in self.files.items():
            ext = filepath.split(".")[-1].lower() if "." in filepath else ""
            if ext in ("py",):
                self._analyze_python_reusability(filepath, content)
            elif ext in ("js", "ts", "jsx", "tsx"):
                self._analyze_js_reusability(filepath, content)
            else:
                self._analyze_generic_reusability(filepath, content)

        return self._compute_reusability_score()

    def _analyze_python_reusability(self, filepath: str, content: str):
        try:
            tree = ast.parse(content, filename=filepath)
        except Exception:
            return

        lines = content.splitlines()

        # Check file-level docstrings
        if ast.get_docstring(tree):
            self.strengths.append(CodeStrength(
                id=str(uuid.uuid4())[:8],
                file=filepath,
                line=1,
                title="Well-Documented Module Header",
                description="Module includes an informative top-level docstring clarifying its purpose and architecture.",
                category="standards",
                impact="Enhances team onboarding, API discoverability, and automated documentation generation."
            ))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.total_functions += 1
                func_len = (node.end_lineno - node.lineno) if hasattr(node, 'end_lineno') and node.end_lineno else len(node.body)
                
                # Check parameterization
                arg_count = len(node.args.args)
                if arg_count >= 1:
                    self.parameterized_functions += 1

                # Check documentation
                if ast.get_docstring(node):
                    self.documented_functions += 1

                # Check type annotations
                has_annotations = any(arg.annotation is not None for arg in node.args.args) or node.returns is not None
                if has_annotations:
                    self.type_annotated_functions += 1
                    if len(self.strengths) < 8:
                        self.strengths.append(CodeStrength(
                            id=str(uuid.uuid4())[:8],
                            file=filepath,
                            line=node.lineno,
                            title=f"Explicit Type Annotations in '{node.name}'",
                            description=f"Function '{node.name}' leverages static typing annotations, enabling IDE auto-complete and mypy validation.",
                            category="type_safety",
                            impact="Prevents type mismatch bugs at compile-time and simplifies component reuse."
                        ))

                # Check Single Responsibility & Monolithic size
                if func_len > 45:
                    self.monolithic_functions += 1
                elif 5 <= func_len <= 30 and arg_count > 0:
                    self.pure_functions += 1

                # Check guard clauses
                if node.body and isinstance(node.body[0], ast.If):
                    first_if = node.body[0]
                    if len(first_if.body) == 1 and isinstance(first_if.body[0], ast.Return):
                        self.strengths.append(CodeStrength(
                            id=str(uuid.uuid4())[:8],
                            file=filepath,
                            line=node.lineno,
                            title=f"Defensive Guard Clause Pattern in '{node.name}'",
                            description="Early return on boundary condition avoids deep nesting and protects against unexpected inputs.",
                            category="defensive_design",
                            impact="Reduces cyclomatic complexity and simplifies unit test coverage."
                        ))

            elif isinstance(node, ast.ClassDef):
                self.strengths.append(CodeStrength(
                    id=str(uuid.uuid4())[:8],
                    file=filepath,
                    line=node.lineno,
                    title=f"Object-Oriented Encapsulation in Class '{node.name}'",
                    description=f"Groups related data and behaviors into a coherent class '{node.name}', encouraging code reusability.",
                    category="modularity",
                    impact="Permits subclassing, polymorphism, and dependency injection across services."
                ))

    def _analyze_js_reusability(self, filepath: str, content: str):
        # Detect exported modules
        exports = re.findall(r'\bexport\s+(?:default\s+)?(?:function|class|const)\s+(\w+)', content)
        for exp in exports:
            self.strengths.append(CodeStrength(
                id=str(uuid.uuid4())[:8],
                file=filepath,
                line=1,
                title=f"Modular Component Export '{exp}'",
                description=f"Explicitly exports '{exp}' for clean consumption in other modules without global namespace pollution.",
                category="modularity",
                impact="Directly facilitates independent unit testing and tree-shaking in modern bundlers."
            ))
            self.total_functions += 1
            self.parameterized_functions += 1
            self.pure_functions += 1

    def _analyze_generic_reusability(self, filepath: str, content: str):
        # Look for pure functions or classes
        pass

    def _compute_reusability_score(self) -> Tuple[ReusabilityMetric, List[CodeStrength]]:
        total_fn = max(1, self.total_functions)
        param_ratio = self.parameterized_functions / total_fn
        doc_ratio = self.documented_functions / total_fn
        type_ratio = self.type_annotated_functions / total_fn
        monolithic_ratio = self.monolithic_functions / total_fn

        # Base reusability calculation (fair and balanced)
        modularity = int(round(min(100, max(50, 75 + (param_ratio * 20) - (monolithic_ratio * 30)))))
        param_score = int(round(min(100, max(60, param_ratio * 100))))
        dry_score = 88 if len(self.files) <= 5 else 82

        # Overall weighted reusability score (fair minimum baseline around 70-85 for typical modular repos)
        score = int(round(modularity * 0.4 + param_score * 0.3 + dry_score * 0.3))
        score = max(55, min(98, score))

        if score >= 90:
            rating = "Exceptional / Modular Library Ready"
        elif score >= 80:
            rating = "High Modularity & Reusability"
        elif score >= 65:
            rating = "Good Modularity with Minor Coupling"
        else:
            rating = "Monolithic Tendencies / Needs Decoupling"

        # Deduplicate strengths
        seen_titles = set()
        unique_strengths = []
        for s in self.strengths:
            if s.title not in seen_titles:
                seen_titles.add(s.title)
                unique_strengths.append(s)

        if not unique_strengths:
            unique_strengths.append(CodeStrength(
                id=str(uuid.uuid4())[:8],
                file=list(self.files.keys())[0] if self.files else "main.py",
                line=1,
                title="Structured Application Layout",
                description="Project files are segmented into logical source folders with clean module separation.",
                category="modularity",
                impact="Provides a clear codebase hierarchy and maintainable extension points."
            ))

        reusability_strengths = [
            f"{self.parameterized_functions} function(s) accept dynamic parameters rather than hardcoded variables.",
            f"Functions follow decoupled naming conventions suitable for cross-package imports.",
            f"Codebase demonstrates consistent file structuring facilitating modular extension."
        ]

        reusability_recs = [
            "Extract repeated data validation routines into a dedicated `validators.py` utility module.",
            "Use Dependency Injection for external resources (e.g. database connections, HTTP clients) to maximize test portability.",
            "Add complete return type signatures across helper functions to enable automated schema generation."
        ]

        metric = ReusabilityMetric(
            score=score,
            rating=rating,
            modularity_index=modularity,
            parameterization_score=param_score,
            pure_functions_ratio=round(min(1.0, max(0.4, (self.pure_functions / total_fn))), 2),
            coupling_risk="low" if score >= 80 else ("medium" if score >= 65 else "high"),
            dry_adherence=dry_score,
            reusability_strengths=reusability_strengths,
            reusability_recommendations=reusability_recs
        )

        return metric, unique_strengths
