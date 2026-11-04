import ast
import math
import re
from typing import Dict, Any, List, Tuple
from models import ComplexityDetails, DuelComparisonResponse, OperationPoint
from engine.algorithm_detector import AlgorithmDetector

class DuelComplexityAnalyzer:
    def __init__(self, code_a: str, code_b: str, language: str = "python", label_a: str = "Candidate A", label_b: str = "Candidate B"):
        self.code_a = code_a.strip()
        self.code_b = code_b.strip()
        self.language = language.lower()
        self.label_a = label_a
        self.label_b = label_b

    def analyze(self) -> DuelComparisonResponse:
        # Step 1: Detect algorithms dynamically using intelligent pattern analyzer
        detection_a = AlgorithmDetector.detect(self.code_a, self.language)
        detection_b = AlgorithmDetector.detect(self.code_b, self.language)

        # Dynamic label assignment if using defaults or outdated fibonacci labels on new code
        auto_label_a = self._resolve_label(self.label_a, detection_a, "Candidate A")
        auto_label_b = self._resolve_label(self.label_b, detection_b, "Candidate B")

        details_a = self._analyze_snippet(self.code_a, auto_label_a, detection_a)
        details_b = self._analyze_snippet(self.code_b, auto_label_b, detection_b)

        comparison_type = f"{detection_a['algorithm_name']} vs {detection_b['algorithm_name']}"

        winner, verdict_title, exec_verdict, key_reasoning, brevity_lesson = self._decide_winner(
            details_a, details_b, auto_label_a, auto_label_b, detection_a, detection_b
        )
        sim_points = self._generate_simulation_points(details_a["time_category"], details_b["time_category"], detection_a, detection_b)
        recommended = self._generate_recommended_code(details_a, details_b, winner)

        return DuelComparisonResponse(
            winner=winner,
            scenario_name=comparison_type,
            detected_comparison_type=comparison_type,
            verdict_title=verdict_title,
            executive_verdict=exec_verdict,
            key_reasoning=key_reasoning,
            why_brevity_can_fail=brevity_lesson,
            candidate_a=ComplexityDetails(**details_a),
            candidate_b=ComplexityDetails(**details_b),
            simulation_points=sim_points,
            scalability_summary=self._generate_scalability_summary(details_a, details_b, winner),
            recommended_hybrid_or_best_code=recommended
        )

    def _resolve_label(self, current_label: str, detection: Dict[str, Any], fallback: str) -> str:
        # If user explicitly provides Code A, Code B, Code 1, Code 2, or Candidate A, preserve clean categorization
        if current_label and any(k in current_label.lower() for k in ["code a", "code b", "code 1", "code 2", "candidate a", "candidate b"]):
            return current_label
        # If label is outdated fibonacci on non-fibonacci code
        if "fibonacci" in current_label.lower() and "fib" not in detection["algorithm_name"].lower():
            return fallback
        return current_label or fallback

    def _analyze_snippet(self, code: str, label: str, detection: Dict[str, Any]) -> Dict[str, Any]:
        lines = code.splitlines()
        loc = len([l for l in lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//")])
        char_count = len(code)

        time_big_o = detection["time_big_o"]
        space_big_o = detection["space_big_o"]
        time_category = detection["time_category"]
        space_category = detection["space_category"]
        cyclomatic = 1
        recursion_depth = "None (Iterative Loop)"
        memory_profile = "Constant Heap/Stack Allocation"
        safety_score = 85
        pros = []
        cons = []
        warnings = []

        # Highlight detected algorithm
        pros.append(f"Identified Pattern: {detection['algorithm_name']} ({detection['paradigm']})")

        is_python = self.language in ("python", "py")

        if is_python:
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                        cyclomatic += 1

                for func_node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
                    calls = [c.func.id for c in ast.walk(func_node) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)]
                    rec_calls = calls.count(func_node.name)
                    if rec_calls >= 2:
                        recursion_depth = "O(n) Call Stack Frames"
                        memory_profile = "Heavy Call Stack Pressure"
                        safety_score = 35
                        warnings.append("Catastrophic exponential recursion: will crash on inputs N >= 40.")
                        warnings.append("Exceeds default Python recursion limit (1000 frames) leading to RecursionError.")
                        cons.append("Redundant subtree recalculation without memoization.")
                    elif rec_calls == 1:
                        recursion_depth = "O(n) Recursion Stack"
                        memory_profile = "Linear Stack Allocation"
                        warnings.append("Recursion stack frames scale with input depth.")
            except Exception:
                pass

        # Algorithm-specific pros & cons
        algo_name_lower = detection["algorithm_name"].lower()
        if "binary search" in algo_name_lower:
            pros.append("Logarithmic search time O(log N) — handles millions of records in <= 25 comparisons.")
            pros.append("Optimal search algorithm for sorted collections.")
            safety_score = max(90, safety_score)
        elif "linear search" in algo_name_lower:
            pros.append("Simple implementation without requiring sorted inputs.")
            cons.append("O(N) search time scales linearly; inefficient for large collections (>10,000 items).")
            warnings.append("Performs up to N sequential comparisons.")
        elif "hash set" in algo_name_lower or "two-sum hash" in algo_name_lower:
            pros.append("Employs O(1) average-time hash table lookups.")
            pros.append("Single-pass linear scan eliminates quadratic nested loops.")
            safety_score = max(92, safety_score)
        elif "nested" in algo_name_lower or "bubble" in algo_name_lower:
            cons.append("Quadratic O(N^2) complexity: computation multiplies quadratically as data grows.")
            warnings.append("Excessive CPU cycles on medium-to-large collections.")
            safety_score = min(60, safety_score)
        elif "join" in algo_name_lower or "buffered" in algo_name_lower:
            pros.append("Pre-allocated linear string construction avoids memory fragmentation.")
        elif "loop string concat" in algo_name_lower:
            cons.append("Repeated string memory reallocation forces O(N^2) memory copies.")

        # Brevity vs Readability
        if loc <= 5:
            pros.append(f"Highly concise ({loc} lines of code).")
            if time_category in ("O(2^n)", "O(n^2)", "O(n^3)"):
                cons.append("Superficial brevity masks poor algorithmic scaling.")
        else:
            pros.append(f"Structured implementation ({loc} lines) prioritizing efficiency and clarity.")

        # Guard checks
        if "if not " in code or "len(" in code or "n <= 0" in code or "null" in code or "return -1" in code:
            pros.append("Contains defensive guard clauses for boundary conditions.")
        else:
            warnings.append("Missing defensive boundary checks for empty or out-of-bounds input.")
            safety_score = max(30, safety_score - 8)

        halstead = round(float(loc * math.log2(max(2, char_count // max(1, loc)))), 1)

        return {
            "algorithm_name": detection["algorithm_name"],
            "paradigm": detection["paradigm"],
            "brief_explanation": detection["brief_explanation"],
            "scale_label": detection["scale_label"],
            "time_big_o": time_big_o,
            "space_big_o": space_big_o,
            "time_category": time_category,
            "space_category": space_category,
            "loc": loc,
            "cyclomatic_complexity": cyclomatic,
            "halstead_volume": halstead,
            "recursion_depth": recursion_depth,
            "memory_profile": memory_profile,
            "safety_score": safety_score,
            "reusability_index": 88 if loc > 3 else 70,
            "pros": pros,
            "cons": cons,
            "edge_case_warnings": warnings
        }

    def _decide_winner(
        self,
        a: Dict[str, Any],
        b: Dict[str, Any],
        label_a: str,
        label_b: str,
        det_a: Dict[str, Any],
        det_b: Dict[str, Any]
    ) -> Tuple[str, str, str, str, str]:
        rank = {
            "O(1)": 1,
            "O(log n)": 2,
            "O(n)": 3,
            "O(n log n)": 4,
            "O(n^2)": 5,
            "O(n^3)": 6,
            "O(2^n)": 7
        }

        rank_a = rank.get(a["time_category"], 4)
        rank_b = rank.get(b["time_category"], 4)

        space_rank = {"O(1)": 1, "O(log n)": 2, "O(n)": 3, "O(n^2)": 4}
        s_rank_a = space_rank.get(a["space_category"], 3)
        s_rank_b = space_rank.get(b["space_category"], 3)

        # Build dynamically tailored brevity lesson based on detected algorithms
        brevity_lesson = self._craft_brevity_lesson(a, b, det_a, det_b)

        if rank_a < rank_b:
            winner = "A"
            verdict_title = f"{label_a} Wins on Efficiency ({a['time_big_o']} vs {b['time_big_o']})"
            exec_verdict = (
                f"{label_a} is substantially superior in computational scaling. "
                f"It achieves {a['time_big_o']} efficiency ({det_a['paradigm']}) compared to {label_b}'s {b['time_big_o']} ({det_b['paradigm']}). "
                f"Even if one snippet has fewer or more lines, {label_a} scales gracefully without hardware bottlenecks."
            )
            key_reasoning = (
                f"{label_a} operates in {a['time_big_o']} time, avoiding the heavy algorithmic degradation of {label_b} ({b['time_big_o']})."
            )
        elif rank_b < rank_a:
            winner = "B"
            verdict_title = f"{label_b} Wins on Efficiency ({b['time_big_o']} vs {a['time_big_o']})"
            exec_verdict = (
                f"{label_b} is substantially superior in computational scaling. "
                f"While {label_a} may look simpler or shorter ({a['loc']} lines vs {b['loc']} lines), "
                f"it suffers from slower {a['time_big_o']} complexity. {label_b} achieves {b['time_big_o']} ({det_b['paradigm']}), "
                f"running exponentially or polynomially faster under realistic workloads."
            )
            key_reasoning = (
                f"{label_b} trades a few lines of code ({b['loc']} vs {a['loc']}) to upgrade from {a['time_big_o']} down to {b['time_big_o']}, "
                f"delivering order-of-magnitude faster responses as data scales."
            )
        else:
            # Same time complexity: compare space complexity or safety
            if s_rank_a < s_rank_b:
                winner = "A"
                verdict_title = f"{label_a} Wins on Memory Profile ({a['space_big_o']} vs {b['space_big_o']})"
                exec_verdict = f"Both candidates share {a['time_big_o']} time complexity, but {label_a} achieves optimal {a['space_big_o']} memory footprint without auxiliary allocation bloat."
                key_reasoning = f"{label_a} operates in {a['space_big_o']} memory space."
            elif s_rank_b < s_rank_a:
                winner = "B"
                verdict_title = f"{label_b} Wins on Memory Profile ({b['space_big_o']} vs {a['space_big_o']})"
                exec_verdict = f"Both candidates share {b['time_big_o']} time complexity, but {label_b} achieves optimal {b['space_big_o']} memory footprint."
                key_reasoning = f"{label_b} operates in {b['space_big_o']} auxiliary memory space."
            else:
                if a["safety_score"] > b["safety_score"]:
                    winner = "A"
                    verdict_title = f"{label_a} Wins on Defensive Safety & Edge Cases"
                    exec_verdict = f"Both share {a['time_big_o']} complexity, but {label_a} includes superior boundary validation and defensive guards."
                    key_reasoning = f"{label_a} scores {a['safety_score']}% safety compared to {b['safety_score']}%."
                elif b["safety_score"] > a["safety_score"]:
                    winner = "B"
                    verdict_title = f"{label_b} Wins on Defensive Safety & Edge Cases"
                    exec_verdict = f"Both share {b['time_big_o']} complexity, but {label_b} includes robust error boundaries and edge checks."
                    key_reasoning = f"{label_b} scores {b['safety_score']}% safety compared to {a['safety_score']}%."
                else:
                    winner = "TIE"
                    verdict_title = "Algorithmic Parity - Equivalent Complexity"
                    exec_verdict = "Both implementations deliver equivalent algorithmic scaling and memory bounds."
                    key_reasoning = "Identical Big-O time and space complexity classes."

        return winner, verdict_title, exec_verdict, key_reasoning, brevity_lesson

    def _craft_brevity_lesson(self, a: Dict[str, Any], b: Dict[str, Any], det_a: Dict[str, Any], det_b: Dict[str, Any]) -> str:
        name_a = det_a["algorithm_name"].lower()
        name_b = det_b["algorithm_name"].lower()

        if "linear search" in name_a or "linear search" in name_b:
            if "binary search" in name_a or "binary search" in name_b:
                return (
                    "The Search Brevity Trap (Linear vs Binary Search): A linear search can be written in just 2 or 3 lines of code "
                    "('for x in arr: if x == target: return True'). It looks compact and effortless. However, as your list grows "
                    "to 1,000,000 items, Linear Search takes up to 1,000,000 comparisons! Binary Search requires about 8 lines of code "
                    "to calculate midpoints and update interval bounds, but it finds the element in only 20 comparisons. That is a 50,000x "
                    "hardware performance leap that proves fewer lines does not mean better code."
                )

        if "duplicate" in name_a or "duplicate" in name_b or "two-sum" in name_a or "two-sum" in name_b:
            if "hash" in name_a or "hash" in name_b:
                return (
                    "The Collection Scan Trap (Nested Loops vs Hash Lookups): Writing two nested loops to check for duplicates "
                    "or pair sums takes only 3 to 4 lines. But it forces N*(N-1)/2 operations—meaning 10,000 items trigger 50,000,000 operations! "
                    "Adding 3 extra lines to introduce a Hash Set or Hash Map leverages O(1) average lookup time, solving the exact same problem "
                    "in a single 10,000-operation pass. Brevity at the cost of quadratic CPU lockups is an anti-pattern."
                )

        if "fibonacci" in name_a or "fibonacci" in name_b or "2^n" in a["time_category"] or "2^n" in b["time_category"]:
            return (
                "The Recursive Tree Trap (Exponential vs Dynamic Programming): A 4-line recursive function looks elegant, "
                "but without memoization it recomputes identical subproblems repeatedly. At N=40, it triggers over 1.1 Trillion operations "
                "and overflows call stacks. An 8-to-10 line iterative or dynamic programming solution requires 40 operations and completes "
                "in less than 2 microseconds with zero recursion overhead."
            )

        if "sort" in name_a or "sort" in name_b:
            return (
                "The Sorting Scalability Lesson: Concise quadratic algorithms like Bubble or Insertion sort are easy to write, "
                "but collapse under data loads. Divide-and-conquer algorithms like Quick Sort or Merge Sort trade concise simplicity "
                "for robust O(N log N) scalability, cutting 1,000,000^2 (1 Trillion) operations down to 20 Million operations."
            )

        # General lesson
        return (
            "The Fallacy of Brevity in Software Engineering: In software development, people often assume "
            "'fewer lines = better code'. However, an algorithm's real-world cost is governed by computational complexity (Big-O), "
            "hardware memory access patterns, and runtime stack safety. A concise snippet with poor scaling will choke production servers, "
            "while a properly structured implementation with clear invariants guarantees predictable, lightning-fast execution."
        )

    def _generate_simulation_points(
        self,
        cat_a: str,
        cat_b: str,
        det_a: Dict[str, Any],
        det_b: Dict[str, Any]
    ) -> List[OperationPoint]:
        is_search = "search" in det_a["algorithm_name"].lower() or "search" in det_b["algorithm_name"].lower()
        
        if is_search and (cat_a == "O(log n)" or cat_b == "O(log n)"):
            test_n = [10, 100, 1000, 10000, 100000, 1000000]
        elif cat_a == "O(2^n)" or cat_b == "O(2^n)":
            test_n = [5, 10, 15, 20, 30, 40, 50]
        else:
            test_n = [10, 50, 100, 500, 1000, 5000, 10000]

        points = []

        def get_ops(cat: str, n: int) -> float:
            if cat == "O(1)":
                return 1.0
            elif cat == "O(log n)":
                return max(1.0, math.log2(n))
            elif cat == "O(n)":
                return float(n)
            elif cat == "O(n log n)":
                return float(n * math.log2(n))
            elif cat == "O(n^2)":
                return float(n * n)
            elif cat == "O(n^3)":
                return float(n * n * n)
            elif cat == "O(2^n)":
                return float(2 ** min(n, 45))
            return float(n)

        for n in test_n:
            ops_a = get_ops(cat_a, n)
            ops_b = get_ops(cat_b, n)
            time_a = ops_a * 0.05
            time_b = ops_b * 0.05
            points.append(OperationPoint(
                n=n,
                ops_a=round(ops_a, 1),
                ops_b=round(ops_b, 1),
                time_est_a_us=round(time_a, 2),
                time_est_b_us=round(time_b, 2)
            ))

        return points

    def _generate_scalability_summary(self, a: Dict[str, Any], b: Dict[str, Any], winner: str) -> str:
        return (
            f"Candidate {winner} maintains optimal computational scaling ({a['time_big_o'] if winner == 'A' else b['time_big_o']}), "
            f"preventing execution timeouts and memory exhaustion as input sizes expand."
        )

    def _generate_recommended_code(self, a: Dict[str, Any], b: Dict[str, Any], winner: str) -> str:
        if winner == "A":
            return self.code_a
        return self.code_b
