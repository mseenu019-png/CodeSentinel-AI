import os
import sys
import io
import zipfile
import shutil
import tempfile
import urllib.request
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from models import (
    ReviewResult, RepositorySummary, FileMetric, IssueItem,
    DuelSnippetRequest, DuelComparisonResponse
)
from engine.ast_analyzer import PythonASTAnalyzer
from engine.polyglot_analyzer import PolyglotAnalyzer
from engine.dependency_indexer import DependencyIndexer
from engine.ranking_engine import RankingAndDeduplicationEngine
from engine.duel_analyzer import DuelComplexityAnalyzer
from engine.report_generator import ReportGenerator
from engine.sample_repos import SAMPLE_REPOSITORIES
from engine.reusability_analyzer import ReusabilityAnalyzer
from engine.optimization_engine import MultiFormOptimizationEngine
from engine.algorithm_detector import AlgorithmDetector

app = FastAPI(
    title="CodeSentinel AI - Enterprise Code Review & Efficiency Platform",
    description="Automated LLM & AST static analysis, Big-O efficiency evaluation, and contextual suggestions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    # Ensure browsers always fetch the latest frontend assets without stale caching
    if request.url.path.endswith((".css", ".js", ".html")) or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

IGNORED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv", "venv",
    "env", ".idea", ".vscode", "dist", "build", "target", ".next", ".nuxt",
    ".cache", "coverage", ".pytest_cache"
}

ALLOWED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".go": "go",
    ".html": "html",
    ".sql": "sql"
}

def analyze_file_dict(files_dict: Dict[str, str], project_name: str) -> ReviewResult:
    all_issues: List[Dict[str, Any]] = []
    file_metrics: List[FileMetric] = []

    for path, content in files_dict.items():
        ext = os.path.splitext(path)[1].lower()
        lang = ALLOWED_EXTENSIONS.get(ext, "unknown")
        filename = os.path.basename(path)

        if lang == "python":
            analyzer = PythonASTAnalyzer(filename=path, source_code=content)
            issues, metrics = analyzer.analyze()
        else:
            analyzer = PolyglotAnalyzer(filename=path, content=content, language=lang)
            issues, metrics = analyzer.analyze()

        all_issues.extend(issues)
        file_metrics.append(FileMetric(
            path=path,
            name=filename,
            language=lang,
            loc=metrics.get("loc", 0),
            blank_lines=metrics.get("blank_lines", 0),
            comment_lines=metrics.get("comment_lines", 0),
            cyclomatic_complexity=metrics.get("cyclomatic_complexity", 1),
            maintainability_index=metrics.get("maintainability_index", 75.0),
            issues_count=metrics.get("issues_count", 0),
            critical_issues=metrics.get("critical_issues", 0),
            risk_level=metrics.get("risk_level", "low"),
            imports=metrics.get("imports", [])
        ))

    # Reusability & Code Strengths Analysis
    reusability_engine = ReusabilityAnalyzer(files_dict)
    reusability_metric, strengths = reusability_engine.analyze()

    # Multi-Form Optimization Pathways
    opt_engine = MultiFormOptimizationEngine(files_dict)
    optimizations = opt_engine.generate_optimizations()

    # Rank and Deduplicate with Fair & Balanced Scoring
    ranker = RankingAndDeduplicationEngine(
        issues=all_issues,
        file_metrics=file_metrics,
        project_name=project_name,
        strengths=strengths,
        reusability_score=reusability_metric.score,
        reusability_rating=reusability_metric.rating
    )
    ranked_issues, summary = ranker.process()

    # Index Dependencies
    indexer = DependencyIndexer(file_metrics)
    dep_graph = indexer.build_graph()

    return ReviewResult(
        summary=summary,
        files=file_metrics,
        issues=ranked_issues,
        dependency_graph=dep_graph,
        analyzed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        file_contents=files_dict,
        optimizations=optimizations,
        reusability_details=reusability_metric
    )

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeSentinel-AI Review Platform",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/review/upload", response_model=ReviewResult)
async def review_uploaded_file(file: UploadFile = File(...)):
    """Accepts a ZIP repository archive or individual code files up to 50MB."""
    content = await file.read()
    filename = file.filename or "project.zip"
    files_dict: Dict[str, str] = {}

    if filename.endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                for member in z.namelist():
                    # Check ignored directories
                    parts = member.replace("\\", "/").split("/")
                    if any(part in IGNORED_DIRS for part in parts) or member.endswith("/"):
                        continue
                    ext = os.path.splitext(member)[1].lower()
                    if ext in ALLOWED_EXTENSIONS:
                        try:
                            file_bytes = z.read(member)
                            files_dict[member] = file_bytes.decode("utf-8", errors="replace")
                        except Exception:
                            continue
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read ZIP archive: {str(e)}")
    else:
        # Single file upload
        ext = os.path.splitext(filename)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            files_dict[filename] = content.decode("utf-8", errors="replace")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file extension '{ext}'")

    if not files_dict:
        raise HTTPException(status_code=400, detail="No readable source code files (.py, .js, .ts, .java, etc.) found in upload.")

    proj_name = os.path.splitext(filename)[0]
    return analyze_file_dict(files_dict, proj_name)

class DirectFilesPayload(BaseModel):
    project_name: str = "Uploaded-Files"
    files: Dict[str, str]

@app.post("/api/review/files", response_model=ReviewResult)
def review_direct_files(payload: DirectFilesPayload):
    if not payload.files:
        raise HTTPException(status_code=400, detail="Files dictionary is empty.")
    return analyze_file_dict(payload.files, payload.project_name)

@app.get("/api/review/sample/{sample_id}", response_model=ReviewResult)
def review_sample_repo(sample_id: str):
    if sample_id not in SAMPLE_REPOSITORIES:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found. Available: {list(SAMPLE_REPOSITORIES.keys())}")
    files = SAMPLE_REPOSITORIES[sample_id]
    names_map = {
        "vulnerable_ecommerce": "E-Commerce FastAPI Backend (Vulnerable)",
        "algorithm_duel_suite": "Algorithm Complexity & Big-O Duel Suite",
        "fullstack_cloud_service": "Cloud Microservice API (Polyglot)"
    }
    proj_name = names_map.get(sample_id, sample_id)
    return analyze_file_dict(files, proj_name)

class GithubClonePayload(BaseModel):
    repo_url: str

@app.post("/api/review/github", response_model=ReviewResult)
def review_github_repo(payload: GithubClonePayload):
    url = payload.repo_url.strip().rstrip("/")
    if "github.com/" not in url:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL. Expected format: https://github.com/owner/repo")

    parts = url.split("github.com/")[1].split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Could not parse repository owner and name.")

    owner, repo_name = parts[0], parts[1].replace(".git", "")
    zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip"

    try:
        req = urllib.request.Request(zip_url, headers={"User-Agent": "CodeSentinel-AI-Reviewer"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                zip_data = resp.read()
        except urllib.error.HTTPError:
            # Fallback to master branch
            zip_url_master = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip"
            req2 = urllib.request.Request(zip_url_master, headers={"User-Agent": "CodeSentinel-AI-Reviewer"})
            with urllib.request.urlopen(req2, timeout=20) as resp2:
                zip_data = resp2.read()

        files_dict = {}
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            for member in z.namelist():
                subparts = member.replace("\\", "/").split("/")
                if any(p in IGNORED_DIRS for p in subparts) or member.endswith("/"):
                    continue
                ext = os.path.splitext(member)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    try:
                        clean_path = "/".join(subparts[1:])  # strip top root folder
                        if clean_path:
                            files_dict[clean_path] = z.read(member).decode("utf-8", errors="replace")
                    except Exception:
                        continue

        if not files_dict:
            raise HTTPException(status_code=400, detail="No supported source code files found in the fetched repository.")

        return analyze_file_dict(files_dict, f"{owner}/{repo_name}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch repository from GitHub: {str(e)}")

# Efficiency Duel API
@app.post("/api/duel/compare", response_model=DuelComparisonResponse)
def compare_snippets(payload: DuelSnippetRequest):
    analyzer = DuelComplexityAnalyzer(
        code_a=payload.code_a,
        code_b=payload.code_b,
        language=payload.language,
        label_a=payload.label_a,
        label_b=payload.label_b
    )
    return analyzer.analyze()

class DetectSnippetRequest(BaseModel):
    code: str
    language: str = "python"

@app.post("/api/duel/detect")
def detect_algorithm_snippet(payload: DetectSnippetRequest):
    return AlgorithmDetector.detect(payload.code, payload.language)

@app.get("/api/duel/presets")
def get_duel_presets():
    return [
        {
            "id": "search",
            "name": "Search Algorithms: 3-Line Linear Search O(N) vs 9-Line Binary Search O(log N)",
            "language": "python",
            "description": "Demonstrates why a 3-line linear search requires up to 1,000,000 checks on large lists, while an 8-to-9 line binary search completes in only 20 comparisons.",
            "code_a": """# Candidate A: 3-Line Linear Search O(N)
def linear_search(arr, target):
    for idx, item in enumerate(arr):
        if item == target:
            return idx
    return -1
""",
            "label_a": "Linear Search (Candidate A)",
            "code_b": """# Candidate B: 9-Line Binary Search O(log N)
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
            "label_b": "Binary Search (Candidate B)"
        },
        {
            "id": "fibonacci",
            "name": "Fibonacci: 5-Line Naive Recursive O(2^N) vs 10-Line Iterative DP O(N)",
            "language": "python",
            "description": "Exposes the classic trap where a 5-line recursive code has catastrophic O(2^N) exponential time and crashes with stack overflow, while a 10-line iterative code runs in O(N) linear time and O(1) space.",
            "code_a": """# Candidate A: 5-Line Naive Recursion
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
""",
            "label_a": "5-Line Recursive (Candidate A)",
            "code_b": """# Candidate B: 10-Line Iterative DP
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr
""",
            "label_b": "10-Line Iterative (Candidate B)"
        },
        {
            "id": "duplicates",
            "name": "Duplicate Search: 4-Line Quadratic Loops O(N^2) vs 7-Line Hash Set O(N)",
            "language": "python",
            "description": "Compares an O(N^2) double-nested iteration against an O(N) Hash Set with O(1) lookup.",
            "code_a": """# Candidate A: 4-Line Nested Loops O(N^2)
def has_duplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]: return True
    return False
""",
            "label_a": "4-Line Nested Scan (Candidate A)",
            "code_b": """# Candidate B: 7-Line Hash Set O(N)
def has_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
""",
            "label_b": "7-Line Hash Set (Candidate B)"
        },
        {
            "id": "sorting",
            "name": "Sorting: 6-Line Bubble Sort O(N^2) vs 12-Line Quick Sort O(N log N)",
            "language": "python",
            "description": "Compares an O(N^2) pairwise adjacent swap against an O(N log N) divide-and-conquer partition.",
            "code_a": """# Candidate A: Bubble Sort O(N^2)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
""",
            "label_a": "Bubble Sort (Candidate A)",
            "code_b": """# Candidate B: Quick Sort O(N log N)
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
""",
            "label_b": "Quick Sort (Candidate B)"
        },
        {
            "id": "string_builder",
            "name": "String Assembly: Inefficient Loop Append vs List Join",
            "language": "python",
            "description": "Reveals quadratic memory copy overhead in s += item versus linear pre-buffered join.",
            "code_a": """# Candidate A: Naive String Concatenation O(N^2 Memory Copy)
def build_report(items):
    res = ""
    for item in items:
        res += str(item) + ","
    return res
""",
            "label_a": "String Re-allocation (Candidate A)",
            "code_b": """# Candidate B: List Join O(N)
def build_report(items):
    buffer = []
    for item in items:
        buffer.append(str(item))
    return ",".join(buffer)
""",
            "label_b": "Buffered List Join (Candidate B)"
        }
    ]

@app.post("/api/report/markdown")
def export_markdown_report(result: ReviewResult):
    md_content = ReportGenerator.to_markdown(result)
    return Response(content=md_content, media_type="text/markdown", headers={
        "Content-Disposition": f"attachment; filename=code_review_{result.summary.project_name.replace(' ', '_')}.md"
    })

@app.post("/api/report/pdf")
def export_pdf_report(result: ReviewResult):
    pdf_bytes = ReportGenerator.to_pdf_bytes(result)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=code_review_{result.summary.project_name.replace(' ', '_')}.pdf"
    })

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
