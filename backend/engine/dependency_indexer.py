import os
from typing import Dict, List, Any, Set
from models import DependencyGraph, DependencyNode, DependencyEdge, FileMetric

class DependencyIndexer:
    def __init__(self, file_metrics: List[FileMetric]):
        self.file_metrics = file_metrics
        self.file_map = {f.name: f for f in file_metrics}
        # Also map without extension for Python imports
        self.stem_map = {os.path.splitext(f.name)[0]: f for f in file_metrics}

    def build_graph(self) -> DependencyGraph:
        nodes: List[DependencyNode] = []
        edges: List[DependencyEdge] = []
        inbound_degrees: Dict[str, int] = {f.path: 0 for f in self.file_metrics}
        adj_list: Dict[str, List[str]] = {f.path: [] for f in self.file_metrics}

        for f in self.file_metrics:
            group = f.language if f.language else "general"
            nodes.append(DependencyNode(
                id=f.path,
                label=f.name,
                group=group,
                issues_count=f.issues_count,
                risk_level=f.risk_level
            ))

            for imp in f.imports:
                # Normalize import
                target_file = None
                # Check direct filename
                if imp in self.file_map:
                    target_file = self.file_map[imp]
                elif imp in self.stem_map:
                    target_file = self.stem_map[imp]
                else:
                    # Check if relative path or module part (e.g. models or utils.db)
                    parts = imp.split(".")
                    for part in parts:
                        if part in self.stem_map:
                            target_file = self.stem_map[part]
                            break

                if target_file and target_file.path != f.path:
                    # Avoid duplicate edge
                    if not any(e.source == f.path and e.target == target_file.path for e in edges):
                        edges.append(DependencyEdge(
                            source=f.path,
                            target=target_file.path,
                            weight=1
                        ))
                        inbound_degrees[target_file.path] = inbound_degrees.get(target_file.path, 0) + 1
                        adj_list[f.path].append(target_file.path)

        # Detect hotspot files: high inbound dependencies or high critical issues
        hotspots = []
        for path, deg in inbound_degrees.items():
            f_metric = next((x for x in self.file_metrics if x.path == path), None)
            if deg >= 2 or (f_metric and f_metric.critical_issues > 0 and deg >= 1):
                hotspots.append(f_metric.name if f_metric else path)

        # Detect simple circular dependencies
        circular = self._find_cycles(adj_list)

        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            hotspot_files=hotspots,
            circular_dependencies=circular
        )

    def _find_cycles(self, adj: Dict[str, List[str]]) -> List[List[str]]:
        visited = set()
        stack = []
        cycles = []

        def dfs(node: str):
            visited.add(node)
            stack.append(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in stack:
                    # Found cycle
                    idx = stack.index(neighbor)
                    cycle_nodes = [os.path.basename(p) for p in stack[idx:]] + [os.path.basename(neighbor)]
                    cycles.append(cycle_nodes)

            stack.pop()

        for node in list(adj.keys()):
            if node not in visited:
                dfs(node)

        return cycles[:5]  # limit to 5 cycles
