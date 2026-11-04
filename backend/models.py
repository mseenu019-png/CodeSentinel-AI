from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class IssueItem(BaseModel):
    id: str
    file: str
    line: int
    end_line: Optional[int] = None
    column: Optional[int] = 1
    category: str  # 'security', 'bug', 'efficiency', 'style', 'maintainability'
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    title: str
    description: str
    impact: str
    rule_id: str
    original_code: str
    suggested_fix: str
    explanation: str
    diff: Optional[str] = None
    confidence: float = 0.95

class CodeStrength(BaseModel):
    id: str
    file: str
    line: Optional[int] = None
    title: str
    description: str
    category: str  # 'modularity', 'clean_code', 'type_safety', 'defensive_design', 'standards'
    impact: str

class OptimizationPathway(BaseModel):
    form_type: str  # 'speed', 'memory', 'reusability', 'idiomatic'
    title: str
    tagline: str
    code: str
    tradeoffs: str
    best_suited_for: str
    time_complexity: str
    space_complexity: str
    efficiency_boost: str

class FileOptimization(BaseModel):
    file: str
    target_name: str
    original_code: str
    reusability_score: int
    pathways: List[OptimizationPathway]

class ReusabilityMetric(BaseModel):
    score: int  # 0 to 100
    rating: str  # 'Exceptional / Modular Library Ready', 'High Modularity', 'Moderate Coupling', 'Monolithic / High Coupling'
    modularity_index: int
    parameterization_score: int
    pure_functions_ratio: float
    coupling_risk: str  # 'low', 'medium', 'high'
    dry_adherence: int
    reusability_strengths: List[str]
    reusability_recommendations: List[str]

class FileMetric(BaseModel):
    path: str
    name: str
    language: str
    loc: int
    blank_lines: int
    comment_lines: int
    cyclomatic_complexity: int
    maintainability_index: float
    reusability_score: int = 80
    issues_count: int
    critical_issues: int
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    imports: List[str] = []

class DependencyNode(BaseModel):
    id: str
    label: str
    group: str
    issues_count: int
    risk_level: str

class DependencyEdge(BaseModel):
    source: str
    target: str
    weight: int = 1

class DependencyGraph(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    hotspot_files: List[str]
    circular_dependencies: List[List[str]] = []

class RepositorySummary(BaseModel):
    project_name: str
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    health_score: int  # 0 to 100
    grade: str  # A+, A, B, C, D, F
    security_score: int
    efficiency_score: int
    maintainability_score: int
    reliability_score: int
    reusability_score: int = 82
    reusability_rating: str = "High Modularity & Reusability"
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    top_risks: List[str] = []
    positive_achievements: List[str] = []
    strengths: List[CodeStrength] = []
    executive_summary: str
    fairness_statement: str = "Evaluated using SonarQube & ISO-25010 Balanced Quality Rubric, ensuring unbiased and constructive assessment."

class ReviewResult(BaseModel):
    summary: RepositorySummary
    files: List[FileMetric]
    issues: List[IssueItem]
    dependency_graph: DependencyGraph
    analyzed_at: str
    file_contents: Dict[str, str] = {}
    optimizations: List[FileOptimization] = []
    reusability_details: Optional[ReusabilityMetric] = None

# Code Arena / Efficiency Duel Models
class DuelSnippetRequest(BaseModel):
    code_a: str
    code_b: str
    language: str = "python"
    label_a: str = "Candidate A"
    label_b: str = "Candidate B"
    scenario: Optional[str] = "Fibonacci Sequence"

class OperationPoint(BaseModel):
    n: int
    ops_a: float
    ops_b: float
    time_est_a_us: float  # microseconds
    time_est_b_us: float

class ComplexityDetails(BaseModel):
    algorithm_name: str = "Custom Algorithm"
    paradigm: str = "Sequential"
    brief_explanation: str = ""
    scale_label: str = "Input Size N"
    time_big_o: str
    space_big_o: str
    time_category: str  # 'O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)', 'O(2^n)'
    space_category: str
    loc: int
    cyclomatic_complexity: int
    halstead_volume: float
    recursion_depth: str
    memory_profile: str
    safety_score: int  # 0-100
    reusability_index: int = 85
    pros: List[str]
    cons: List[str]
    edge_case_warnings: List[str]

class DuelComparisonResponse(BaseModel):
    winner: str  # 'A', 'B', 'TIE'
    scenario_name: str = "Algorithm Efficiency Duel"
    detected_comparison_type: str = "Algorithm Comparison"
    verdict_title: str
    executive_verdict: str
    key_reasoning: str
    why_brevity_can_fail: str
    candidate_a: ComplexityDetails
    candidate_b: ComplexityDetails
    simulation_points: List[OperationPoint]
    scalability_summary: str
    recommended_hybrid_or_best_code: str
