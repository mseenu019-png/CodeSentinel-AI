import ast
import re
from typing import Dict, Any, Tuple

class AlgorithmDetector:
    """
    Intelligently inspects code syntax and patterns to detect the exact algorithm,
    data structure paradigm, and algorithmic purpose.
    """

    @staticmethod
    def detect(code: str, language: str = "python") -> Dict[str, Any]:
        code_str = code.strip()
        lines = [l for l in code_str.splitlines() if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//")]
        loc = len(lines)
        code_lower = code_str.lower()

        # Default detection results
        algo_name = "Custom Algorithm"
        paradigm = "Sequential / Iterative"
        time_big_o = "O(n)"
        space_big_o = "O(1)"
        time_category = "O(n)"
        space_category = "O(1)"
        brief_explanation = "Iterative routine processing input collections."
        scale_label = "Items in Collection"

        # 1. Fibonacci & Exponential Trees
        if re.search(r'\b\w+\([^)]*n\s*-\s*1\)[^)]*\+[^)]*\b\w+\([^)]*n\s*-\s*2\)', code_str) or \
           re.search(r'return\s+\w+\([^)]*-\s*1\)\s*\+\s*\w+\([^)]*-\s*2\)', code_str):
            algo_name = "Naive Recursive Fibonacci"
            paradigm = "Exponential Divide & Conquer (Unmemoized)"
            time_big_o = "O(2^n)"
            space_big_o = "O(n)"
            time_category = "O(2^n)"
            space_category = "O(n)"
            brief_explanation = "Computes terms by spawning two recursive calls per step without caching, causing catastrophic O(2^N) branch explosion."
            scale_label = "Sequence Index N"

        elif ("fib" in code_lower or "fibonacci" in code_lower) and ("prev" in code_lower or "curr" in code_lower or "range" in code_lower or "while" in code_lower):
            algo_name = "Iterative DP Fibonacci"
            paradigm = "Bottom-Up Dynamic Programming"
            time_big_o = "O(n)"
            space_big_o = "O(1)"
            time_category = "O(n)"
            space_category = "O(1)"
            brief_explanation = "Accumulates state using two rolling variables in a single linear pass with constant O(1) memory."
            scale_label = "Sequence Index N"

        # 2. Search Algorithms: Linear vs Binary Search
        elif ("mid" in code_lower or "low" in code_lower or "high" in code_lower or "// 2" in code_str or "/ 2" in code_str) and \
             ("while" in code_lower or "search" in code_lower or "binary" in code_lower):
            algo_name = "Binary Search"
            paradigm = "Logarithmic Interval Bisection"
            time_big_o = "O(log n)"
            space_big_o = "O(1)" if "while" in code_lower else "O(log n)"
            time_category = "O(log n)"
            space_category = "O(1)" if "while" in code_lower else "O(log n)"
            brief_explanation = "Halves the active search space at every step, resolving items in a 1,000,000-element list in only 20 comparisons."
            scale_label = "Array Elements N"

        elif ("search" in code_lower or "find" in code_lower or "target" in code_lower or "item ==" in code_str or "== target" in code_lower or "in arr" in code_lower) and \
             ("for " in code_lower and ("for " not in code_lower[code_lower.find("for ")+4:])):
            algo_name = "Linear Search"
            paradigm = "Brute-Force Sequential Scan"
            time_big_o = "O(n)"
            space_big_o = "O(1)"
            time_category = "O(n)"
            space_category = "O(1)"
            brief_explanation = "Iterates sequentially through each element from index 0 to N-1, requiring N comparisons in the worst case."
            scale_label = "Array Elements N"

        # 3. Duplicate Detection: Hash Set vs Nested Loops
        elif ("seen = set" in code_lower or "set()" in code_lower or "new set" in code_lower or "hashset" in code_lower) and \
             ("in seen" in code_lower or "seen.add" in code_lower or "has(" in code_lower):
            algo_name = "Hash Set Duplicate Lookup"
            paradigm = "Hash-Indexed Membership Check"
            time_big_o = "O(n)"
            space_big_o = "O(n)"
            time_category = "O(n)"
            space_category = "O(n)"
            brief_explanation = "Leverages O(1) average-time hash table lookups to detect duplicates in a single linear pass."
            scale_label = "Items in Dataset"

        elif ("duplicate" in code_lower or "dupe" in code_lower or "has_" in code_lower) and \
             (code_lower.count("for ") >= 2 or (code_lower.count("while") >= 1 and code_lower.count("for") >= 1)):
            algo_name = "Quadratic Nested Duplicate Scan"
            paradigm = "Brute-Force Pairwise Comparison"
            time_big_o = "O(n^2)"
            space_big_o = "O(1)"
            time_category = "O(n^2)"
            space_category = "O(1)"
            brief_explanation = "Compares every element against every other element using nested loops, performing N*(N-1)/2 comparisons."
            scale_label = "Items in Dataset"

        # 4. Sorting Algorithms: Bubble/Selection vs Quick/Merge
        elif ("bubble" in code_lower or ("> arr[" in code_str or "> nums[" in code_str or "> a[" in code_str)) and \
             (code_lower.count("for ") >= 2 and ("swap" in code_lower or ", arr[" in code_str or ", nums[" in code_str or "= arr[j+1]" in code_str)):
            algo_name = "Bubble / Selection Sort"
            paradigm = "Quadratic Iterative Exchange"
            time_big_o = "O(n^2)"
            space_big_o = "O(1)"
            time_category = "O(n^2)"
            space_category = "O(1)"
            brief_explanation = "Repeatedly steps through the list, swapping adjacent elements. Quadratic complexity makes it unsuitable for large inputs."
            scale_label = "Unsorted Items N"

        elif "pivot" in code_lower or "quicksort" in code_lower or "quick_sort" in code_lower:
            algo_name = "Quick Sort"
            paradigm = "Divide and Conquer Partitioning"
            time_big_o = "O(n log n)"
            space_big_o = "O(log n)"
            time_category = "O(n log n)"
            space_category = "O(log n)"
            brief_explanation = "Partitions the dataset around a chosen pivot element and recursively sorts sub-arrays in O(N log N) average time."
            scale_label = "Unsorted Items N"

        elif "merge" in code_lower and ("left" in code_lower or "right" in code_lower) and ("sort" in code_lower or "mid" in code_lower):
            algo_name = "Merge Sort"
            paradigm = "Stable Divide and Conquer"
            time_big_o = "O(n log n)"
            space_big_o = "O(n)"
            time_category = "O(n log n)"
            space_category = "O(n)"
            brief_explanation = "Recursively divides array in half, sorting and interleaving them in guaranteed O(N log N) time."
            scale_label = "Unsorted Items N"

        # 5. String Aggregation: Loop Concatenation vs Join / Buffer
        elif ("+=" in code_str and ("str(" in code_str or '"' in code_str or "'" in code_str)) and \
             ("for " in code_lower or "while " in code_lower) and (".join" not in code_lower):
            algo_name = "Loop String Concatenation"
            paradigm = "Immutable Buffer Re-allocation"
            time_big_o = "O(n^2)"
            space_big_o = "O(n^2)"
            time_category = "O(n^2)"
            space_category = "O(n^2)"
            brief_explanation = "Re-allocates string memory on every iteration, leading to O(N^2) total byte copies for N concatenations."
            scale_label = "String Segments N"

        elif ".join(" in code_lower or "stringbuilder" in code_lower:
            algo_name = "Buffered Array Join"
            paradigm = "Single-Pass Linear Aggregation"
            time_big_o = "O(n)"
            space_big_o = "O(n)"
            time_category = "O(n)"
            space_category = "O(n)"
            brief_explanation = "Collects tokens into an array buffer and performs a single C-level memory allocation to join them."
            scale_label = "String Segments N"

        # 6. Two Sum Problem
        elif ("two_sum" in code_lower or "twosum" in code_lower or "target - " in code_lower) and ("{" in code_str or "dict" in code_lower or "seen" in code_lower):
            algo_name = "Two-Sum Hash Map"
            paradigm = "Complement Hash Indexing"
            time_big_o = "O(n)"
            space_big_o = "O(n)"
            time_category = "O(n)"
            space_category = "O(n)"
            brief_explanation = "Finds complement pairs in a single linear pass by checking if (target - num) exists in a hash map."
            scale_label = "Numbers in Array"

        # 7. Palindrome Checks
        elif "palindrome" in code_lower or "[::-1]" in code_str:
            algo_name = "Palindrome Validator"
            paradigm = "Bidirectional Equality Check"
            time_big_o = "O(n)"
            space_big_o = "O(1)" if "while" in code_lower else "O(n)"
            time_category = "O(n)"
            space_category = "O(1)" if "while" in code_lower else "O(n)"
            brief_explanation = "Verifies string symmetry by comparing characters from endpoints toward center."
            scale_label = "Characters in String"

        # 8. Factorial / Math Recursion vs Iteration
        elif ("fact" in code_lower or "factorial" in code_lower) and ("*" in code_str):
            if re.search(r'\w+\([^)]*n\s*-\s*1\)', code_str):
                algo_name = "Recursive Factorial"
                paradigm = "Linear Recursion Tree"
                time_big_o = "O(n)"
                space_big_o = "O(n)"
                time_category = "O(n)"
                space_category = "O(n)"
                brief_explanation = "Multiplies numbers by descending recursion stack frames, bounded by O(N) memory."
                scale_label = "Input Integer N"
            else:
                algo_name = "Iterative Factorial"
                paradigm = "Iterative Product Accumulator"
                time_big_o = "O(n)"
                space_big_o = "O(1)"
                time_category = "O(n)"
                space_category = "O(1)"
                brief_explanation = "Multiplies numbers in a single for-loop with constant O(1) auxiliary space."
                scale_label = "Input Integer N"

        # 9. Generic AST Fallback (Loop Nesting Depth)
        else:
            try:
                tree = ast.parse(code_str)
                max_depth = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        depth = 1
                        for child in ast.walk(node):
                            if child is not node and isinstance(child, (ast.For, ast.While)):
                                depth = 2
                                for gchild in ast.walk(child):
                                    if gchild is not child and isinstance(gchild, (ast.For, ast.While)):
                                        depth = 3
                        max_depth = max(max_depth, depth)

                if max_depth >= 3:
                    algo_name = f"Cubic O(N^3) Nested Algorithm"
                    paradigm = "Multi-Dimensional Iteration"
                    time_big_o = "O(n^3)"
                    time_category = "O(n^3)"
                elif max_depth == 2:
                    algo_name = f"Quadratic O(N^2) Nested Loop"
                    paradigm = "Nested Pairwise Scan"
                    time_big_o = "O(n^2)"
                    time_category = "O(n^2)"
                elif max_depth == 1:
                    algo_name = f"Linear O(N) Loop Algorithm"
                    paradigm = "Single-Pass Linear Iteration"
                    time_big_o = "O(n)"
                    time_category = "O(n)"
                else:
                    algo_name = "Constant O(1) Direct Logic"
                    paradigm = "Direct Arithmetic / Schema Access"
                    time_big_o = "O(1)"
                    time_category = "O(1)"
            except Exception:
                pass

        return {
            "algorithm_name": algo_name,
            "paradigm": paradigm,
            "time_big_o": time_big_o,
            "space_big_o": space_big_o,
            "time_category": time_category,
            "space_category": space_category,
            "brief_explanation": brief_explanation,
            "scale_label": scale_label,
            "loc": loc
        }
