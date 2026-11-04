import sys
import os
import io
import zipfile
import unittest

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from engine.ast_analyzer import PythonASTAnalyzer
from engine.polyglot_analyzer import PolyglotAnalyzer
from engine.dependency_indexer import DependencyIndexer
from engine.ranking_engine import RankingAndDeduplicationEngine
from engine.duel_analyzer import DuelComplexityAnalyzer
from engine.reusability_analyzer import ReusabilityAnalyzer
from engine.optimization_engine import MultiFormOptimizationEngine
from engine.report_generator import ReportGenerator
from engine.sample_repos import SAMPLE_REPOSITORIES
from main import analyze_file_dict

class TestCodeSentinelAllDataSections(unittest.TestCase):

    def setUp(self):
        self.sample_files = SAMPLE_REPOSITORIES["vulnerable_ecommerce"]

    def test_01_ast_analyzer_precision(self):
        """Verify AST analyzer detects security, bugs, and performance patterns accurately."""
        code = """import os, hashlib
JWT_KEY = "SUPER_SECRET_12345"
def calc(x=[]):
    os.system("echo " + str(x))
    h = hashlib.md5(b"pw").hexdigest()
    f = open("/tmp/test.log", "w")
    try:
        val = 1 / 0
    except Exception:
        pass
"""
        analyzer = PythonASTAnalyzer("test.py", code)
        issues, metrics = analyzer.analyze()
        
        rule_ids = [i["rule_id"] for i in issues]
        self.assertIn("SEC-HARDCODED-SECRET", rule_ids)
        self.assertIn("SEC-CMD-INJECTION", rule_ids)
        self.assertIn("SEC-WEAK-HASH", rule_ids)
        self.assertIn("BUG-MUTABLE-DEFAULT", rule_ids)
        self.assertIn("RES-UNCLOSED-FILE", rule_ids)
        self.assertIn("ERR-BROAD-EXCEPT", rule_ids)
        self.assertGreater(metrics["loc"], 5)
        print("[PASS] Test 01: AST Analyzer Precision Passed")

    def test_02_polyglot_analyzer_precision(self):
        """Verify JS/TS and multi-language analyzer detects XSS, unawaited promises, and secrets."""
        code = """export async function render(id, html) {
    const data = fetch("http://insecure-api.internal.com/data");
    document.getElementById(id).innerHTML = html;
    const AWS = "AKIAIOSFODNN7EXAMPLE";
}"""
        analyzer = PolyglotAnalyzer("view.ts", code, "typescript")
        issues, metrics = analyzer.analyze()

        rule_ids = [i["rule_id"] for i in issues]
        self.assertIn("SEC-DOM-XSS", rule_ids)
        self.assertIn("BUG-UNAWAITED-PROMISE", rule_ids)
        self.assertIn("SEC-AWS-CREDENTIAL", rule_ids)
        self.assertIn("SEC-INSECURE-HTTP", rule_ids)
        print("[PASS] Test 02: Polyglot Analyzer Precision Passed")

    def test_03_reusability_and_strengths_engine(self):
        """Verify reusability scoring and positive engineering strengths detection."""
        reus_engine = ReusabilityAnalyzer(self.sample_files)
        metric, strengths = reus_engine.analyze()

        self.assertGreaterEqual(metric.score, 50)
        self.assertLessEqual(metric.score, 100)
        self.assertIn(metric.coupling_risk, ["low", "medium", "high"])
        self.assertGreater(len(strengths), 0)
        print(f"[PASS] Test 03: Reusability Engine Passed (Score: {metric.score}/100, Strengths: {len(strengths)})")

    def test_04_multi_form_optimizations(self):
        """Verify generation of multi-form optimization pathways (Speed, Memory, Reusability, Idiomatic)."""
        opt_engine = MultiFormOptimizationEngine(self.sample_files)
        optimizations = opt_engine.generate_optimizations()

        self.assertGreater(len(optimizations), 0)
        first_opt = optimizations[0]
        self.assertTrue(hasattr(first_opt, "pathways"))
        self.assertGreaterEqual(len(first_opt.pathways), 2)
        
        form_types = [p.form_type for p in first_opt.pathways]
        self.assertTrue(any(f in form_types for f in ["speed", "memory", "reusability"]))
        print(f"[PASS] Test 04: Multi-Form Optimization Passed ({len(optimizations)} targets with multi-form pathways)")

    def test_05_balanced_and_fair_scoring(self):
        """Verify the scoring algorithm produces balanced, encouraging, and unbiased results."""
        review = analyze_file_dict(self.sample_files, "E-Commerce Test")
        sum = review.summary

        self.assertGreaterEqual(sum.health_score, 40)
        self.assertLessEqual(sum.health_score, 100)
        self.assertIn(sum.grade, ["A+", "A", "B", "C", "D", "E"])
        self.assertIsNotNone(sum.fairness_statement)
        self.assertGreater(len(sum.positive_achievements), 0)
        print(f"[PASS] Test 05: Balanced Fairness Scoring Passed (Health: {sum.health_score}, Grade: {sum.grade})")

    def test_06_efficiency_duel_brevity_fallacy(self):
        """Verify the Code Arena correctly evaluates 5-line recursive vs 10-line iterative Fibonacci."""
        code_5 = """def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)"""

        code_10 = """def fib(n):
    if n <= 0: return 0
    elif n == 1: return 1
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr"""

        duel = DuelComplexityAnalyzer(code_5, code_10, language="python", label_a="5-Line Naive", label_b="10-Line Iterative")
        res = duel.analyze()

        self.assertEqual(res.winner, "B")
        self.assertEqual(res.candidate_a.time_category, "O(2^n)")
        self.assertEqual(res.candidate_b.time_category, "O(n)")
        self.assertEqual(res.candidate_b.space_category, "O(1)")
        self.assertGreater(len(res.simulation_points), 0)

        pt_40 = next(p for p in res.simulation_points if p.n == 40)
        self.assertGreater(pt_40.ops_a, 1000000000)
        self.assertEqual(pt_40.ops_b, 40)
        print(f"[PASS] Test 06: Efficiency Duel Passed (Candidate {res.winner} won; Brevity Fallacy proven at N=40)")

    def test_07_dependency_graph_and_hotspots(self):
        """Verify architectural graph indexing, node connections, and hotspots."""
        review = analyze_file_dict(self.sample_files, "Graph Test")
        graph = review.dependency_graph

        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.edges), 0)
        self.assertIsInstance(graph.hotspot_files, list)
        print(f"[PASS] Test 07: Dependency Graph Passed ({len(graph.nodes)} nodes, {len(graph.edges)} edges)")

    def test_08_pdf_and_markdown_report_generation(self):
        """Verify ReportLab PDF generation and Markdown generation with reusability and strengths."""
        review = analyze_file_dict(self.sample_files, "Report Test")
        
        pdf_bytes = ReportGenerator.to_pdf_bytes(review)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

        md_text = ReportGenerator.to_markdown(review)
        self.assertIn("Automated Code Review & Reusability Audit", md_text)
        self.assertIn("Code Strengths & Commendations", md_text)
        print(f"[PASS] Test 08: Report Generation Passed (PDF: {len(pdf_bytes)} bytes, MD: {len(md_text)} chars)")

    def test_09_zip_archive_upload_simulation(self):
        """Verify ZIP archive processing with directory filtering."""
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as z:
            z.writestr("core/math.py", "def add(a: int, b: int) -> int:\n    return a + b\n")
            z.writestr("core/secrets.py", "API_KEY = 'secret_token_12345'\n")
            z.writestr("node_modules/junk.js", "console.log('ignored');")

        zip_buf.seek(0)
        files_dict = {}
        with zipfile.ZipFile(zip_buf) as z:
            for member in z.namelist():
                if "node_modules" in member:
                    continue
                files_dict[member] = z.read(member).decode("utf-8")

        review = analyze_file_dict(files_dict, "Zip Test")
        self.assertEqual(len(review.files), 2)
        print(f"[PASS] Test 09: ZIP Ingestion Passed ({len(review.files)} files processed, node_modules filtered)")

if __name__ == "__main__":
    unittest.main()
