from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Optional

app = FastAPI(title="Machine Layout Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatrixInput(BaseModel):
    matrix: List[List[int]]
    machine_names: Optional[List[str]] = None
    part_names: Optional[List[str]] = None
    routing: Optional[List[List[int]]] = None  # routing[i] = ordered list of machine indices for part i


@app.get("/api")
@app.get("/api/")
def health():
    return {"status": "ok", "message": "Machine Layout Solver API"}


# ---------------------------------------------------------------------------
# KING METHOD
# ---------------------------------------------------------------------------

def king_method(matrix: List[List[int]]):
    A = np.array(matrix, dtype=float)
    n, m = A.shape
    row_order = list(range(n))
    col_order = list(range(m))

    for _ in range(200):  # max iterations
        stable = True

        # Step 1: compute column weights
        col_weights = []
        for j in range(m):
            w = sum(A[i, j] * (2 ** (n - i)) for i in range(n))
            col_weights.append(w)

        new_col_order_indices = sorted(range(m), key=lambda j: -col_weights[j])
        new_col_perm = [col_order[j] for j in new_col_order_indices]
        if new_col_perm != col_order:
            stable = False
        col_order = new_col_perm
        A = A[:, new_col_order_indices]

        # Step 2: compute row weights
        row_weights = []
        for i in range(n):
            w = sum(A[i, j] * (2 ** (m - j)) for j in range(m))
            row_weights.append(w)

        new_row_order_indices = sorted(range(n), key=lambda i: -row_weights[i])
        new_row_perm = [row_order[i] for i in new_row_order_indices]
        if new_row_perm != row_order:
            stable = False
        row_order = new_row_perm
        A = A[new_row_order_indices, :]

        if stable:
            break

    return A.astype(int).tolist(), row_order, col_order


def detect_clusters_king(reordered_matrix, row_order, col_order, machine_names, part_names):
    """Detect block-diagonal clusters in the reordered matrix using a sweep approach."""
    A = np.array(reordered_matrix)
    n, m = A.shape

    # Find row ranges where machines group together
    # Use union-find on (row, col) pairs
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(n):
        for j in range(m):
            if A[i, j] == 1:
                union(('r', i), ('c', j))

    # Group rows into clusters by their root
    from collections import defaultdict
    clusters = defaultdict(lambda: {"machines": [], "parts": []})
    for i in range(n):
        root = find(('r', i))
        clusters[root]["machines"].append(i)
    for j in range(m):
        root = find(('c', j))
        clusters[root]["parts"].append(j)

    # Merge: assign parts to machine clusters
    machine_root_map = {}
    for i in range(n):
        machine_root_map[i] = find(('r', i))

    part_to_cluster = {}
    for j in range(m):
        part_root = find(('c', j))
        part_to_cluster[j] = part_root

    # Consolidate
    result_clusters = []
    seen_roots = []
    for root, data in clusters.items():
        if data["machines"]:
            seen_roots.append(root)
            result_clusters.append({
                "machines": [row_order[i] for i in sorted(data["machines"])],
                "machine_indices_reordered": sorted(data["machines"]),
                "parts": [col_order[j] for j in sorted(data["parts"])],
                "part_indices_reordered": sorted(data["parts"]),
                "machine_names": [machine_names[row_order[i]] for i in sorted(data["machines"])],
                "part_names": [part_names[col_order[j]] for j in sorted(data["parts"])],
            })

    return result_clusters


def find_exceptional_elements(original_matrix, clusters, row_order, col_order):
    """Parts that belong to more than one cluster (hors trame)."""
    A = np.array(original_matrix)
    n, m = A.shape

    # map original machine index -> cluster index
    machine_to_cluster = {}
    for ci, c in enumerate(clusters):
        for mi in c["machines"]:
            machine_to_cluster[mi] = ci

    exceptional_parts = []
    exceptional_machines = []

    for orig_j in range(m):
        cluster_set = set()
        for orig_i in range(n):
            if A[orig_i, orig_j] == 1:
                ci = machine_to_cluster.get(orig_i)
                if ci is not None:
                    cluster_set.add(ci)
        if len(cluster_set) > 1:
            exceptional_parts.append(orig_j)

    part_to_cluster = {}
    for ci, c in enumerate(clusters):
        for pj in c["parts"]:
            part_to_cluster[pj] = ci

    for orig_i in range(n):
        cluster_set = set()
        for orig_j in range(m):
            if A[orig_i, orig_j] == 1:
                ci = part_to_cluster.get(orig_j)
                if ci is not None:
                    cluster_set.add(ci)
        if len(cluster_set) > 1:
            exceptional_machines.append(orig_i)

    return exceptional_parts, exceptional_machines


def compute_efficiency(original_matrix, clusters):
    """Compute grouping efficiency = internal_operations / total_operations."""
    A = np.array(original_matrix)
    total_ones = int(np.sum(A))
    if total_ones == 0:
        return 0.0

    internal = 0
    for c in clusters:
        machines = c["machines"]
        parts = c["parts"]
        for mi in machines:
            for pj in parts:
                if A[mi, pj] == 1:
                    internal += 1

    return round(internal / total_ones, 4)


@app.post("/api/king")
async def king_endpoint(data: MatrixInput):
    matrix = data.matrix
    n = len(matrix)
    m = len(matrix[0]) if n > 0 else 0

    machine_names = data.machine_names or [f"M{i+1}" for i in range(n)]
    part_names = data.part_names or [f"P{j+1}" for j in range(m)]

    reordered, row_order, col_order = king_method(matrix)

    clusters = detect_clusters_king(reordered, row_order, col_order, machine_names, part_names)

    exc_parts, exc_machines = find_exceptional_elements(matrix, clusters, row_order, col_order)
    efficiency = compute_efficiency(matrix, clusters)

    crossing_flows = []
    if data.routing:
        machine_to_cluster = {}
        for ci, c in enumerate(clusters):
            for mi in c["machines"]:
                machine_to_cluster[mi] = ci
        for pi, route in enumerate(data.routing):
            for k in range(len(route) - 1):
                m_from = route[k]
                m_to = route[k + 1]
                c_from = machine_to_cluster.get(m_from)
                c_to = machine_to_cluster.get(m_to)
                if c_from is not None and c_to is not None and c_from != c_to:
                    crossing_flows.append({
                        "part": pi,
                        "part_name": part_names[pi] if pi < len(part_names) else f"P{pi+1}",
                        "from_machine": m_from,
                        "to_machine": m_to,
                        "from_cluster": c_from,
                        "to_cluster": c_to,
                    })

    return {
        "method": "king",
        "original_matrix": matrix,
        "reordered_matrix": reordered,
        "row_order": row_order,
        "col_order": col_order,
        "machine_names_reordered": [machine_names[i] for i in row_order],
        "part_names_reordered": [part_names[j] for j in col_order],
        "clusters": clusters,
        "exceptional_parts": [part_names[j] if j < len(part_names) else f"P{j+1}" for j in exc_parts],
        "exceptional_machines": [machine_names[i] if i < len(machine_names) else f"M{i+1}" for i in exc_machines],
        "exceptional_part_indices": exc_parts,
        "exceptional_machine_indices": exc_machines,
        "crossing_flows": crossing_flows,
        "efficiency": efficiency,
    }


# ---------------------------------------------------------------------------
# CHAINING (LINK-BASED) METHOD
# ---------------------------------------------------------------------------

def chaining_method(matrix: List[List[int]]):
    A = np.array(matrix)
    n, m = A.shape  # n = machines (rows), m = parts (cols)

    # Step 1: compute machine–machine link matrix
    L = np.zeros((n, n), dtype=int)
    for i in range(n):
        for k in range(i + 1, n):
            shared = int(np.sum((A[i, :] == 1) & (A[k, :] == 1)))
            L[i, k] = shared
            L[k, i] = shared

    # Step 2: classify links
    link_types = {}  # (i,k) -> "strong"|"weak"|"none"
    for i in range(n):
        for k in range(i + 1, n):
            v = L[i, k]
            if v >= 2:
                link_types[(i, k)] = "strong"
            elif v == 1:
                link_types[(i, k)] = "weak"
            else:
                link_types[(i, k)] = "none"

    # Step 3: build clusters via union-find (strong links first)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    # Merge on strong links
    for (i, k), t in link_types.items():
        if t == "strong":
            union(i, k)

    # Iteratively absorb weak links
    changed = True
    while changed:
        changed = False
        for (i, k), t in link_types.items():
            if t == "weak":
                if find(i) != find(k):
                    # Check if merging is beneficial (at least one strong link in each group to this pair)
                    union(i, k)
                    changed = True

    # Build groups
    from collections import defaultdict
    groups_map = defaultdict(list)
    for i in range(n):
        groups_map[find(i)].append(i)
    groups = [sorted(v) for v in groups_map.values()]

    return L.tolist(), link_types, groups


def build_triangular_schema(link_matrix, n):
    """Return upper-triangular representation."""
    T = []
    for i in range(n):
        row = []
        for k in range(n):
            if k > i:
                row.append(link_matrix[i][k])
            else:
                row.append(None)
        T.append(row)
    return T


@app.post("/api/chaining")
async def chaining_endpoint(data: MatrixInput):
    matrix = data.matrix
    n = len(matrix)
    m = len(matrix[0]) if n > 0 else 0

    machine_names = data.machine_names or [f"M{i+1}" for i in range(n)]
    part_names = data.part_names or [f"P{j+1}" for j in range(m)]

    L, link_types, groups = chaining_method(matrix)

    # Assign parts to clusters
    clusters = []
    for gi, g in enumerate(groups):
        cluster_parts = []
        cluster_parts_names = []
        for j in range(m):
            machine_set = set()
            for i in range(n):
                if matrix[i][j] == 1:
                    machine_set.add(i)
            group_set = set(g)
            if machine_set & group_set:  # at least one machine in this group uses this part
                if machine_set.issubset(group_set):  # fully internal
                    cluster_parts.append(j)
                    cluster_parts_names.append(part_names[j])
        clusters.append({
            "machines": g,
            "machine_names": [machine_names[i] for i in g],
            "parts": cluster_parts,
            "part_names": cluster_parts_names,
        })

    # Exceptional parts (used by machines in multiple clusters)
    machine_to_cluster = {}
    for ci, c in enumerate(clusters):
        for mi in c["machines"]:
            machine_to_cluster[mi] = ci

    exc_parts = []
    for j in range(m):
        cluster_set = set()
        for i in range(n):
            if matrix[i][j] == 1:
                ci = machine_to_cluster.get(i)
                if ci is not None:
                    cluster_set.add(ci)
        if len(cluster_set) > 1:
            exc_parts.append(j)

    efficiency = compute_efficiency(matrix, clusters)

    # Serialise link_types
    link_types_serialized = {f"{i},{k}": v for (i, k), v in link_types.items()}

    triangular = build_triangular_schema(L, n)

    # Graph edges
    edges = []
    for i in range(n):
        for k in range(i + 1, n):
            if L[i][k] > 0:
                edges.append({
                    "source": i,
                    "target": k,
                    "source_name": machine_names[i],
                    "target_name": machine_names[k],
                    "weight": L[i][k],
                    "type": link_types.get((i, k), "none"),
                })

    crossing_flows = []
    if data.routing:
        for pi, route in enumerate(data.routing):
            for k in range(len(route) - 1):
                m_from = route[k]
                m_to = route[k + 1]
                c_from = machine_to_cluster.get(m_from)
                c_to = machine_to_cluster.get(m_to)
                if c_from is not None and c_to is not None and c_from != c_to:
                    crossing_flows.append({
                        "part": pi,
                        "part_name": part_names[pi] if pi < len(part_names) else f"P{pi+1}",
                        "from_machine": m_from,
                        "to_machine": m_to,
                        "from_cluster": c_from,
                        "to_cluster": c_to,
                    })

    return {
        "method": "chaining",
        "link_matrix": L,
        "link_types": link_types_serialized,
        "triangular_schema": triangular,
        "groups": groups,
        "clusters": clusters,
        "graph_edges": edges,
        "machine_names": machine_names,
        "part_names": part_names,
        "exceptional_parts": [part_names[j] if j < len(part_names) else f"P{j+1}" for j in exc_parts],
        "exceptional_part_indices": exc_parts,
        "crossing_flows": crossing_flows,
        "efficiency": efficiency,
    }


# ---------------------------------------------------------------------------
# ANALYZE (run both methods)
# ---------------------------------------------------------------------------

@app.post("/api/analyze")
async def analyze_endpoint(data: MatrixInput):
    king_result = await king_endpoint(data)
    chaining_result = await chaining_endpoint(data)
    return {
        "king": king_result,
        "chaining": chaining_result,
    }
