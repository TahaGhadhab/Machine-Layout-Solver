from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Models ────────────────────────────────────────────────────────────

class MatrixRequest(BaseModel):
    matrix: list[list[int]]

class AnalyzeRequest(BaseModel):
    matrix: list[list[int]]
    groups: dict[int, int]           # machine_index → group_id
    routing: Optional[list[list[int]]] = None  # per-part ordered machine list

# ─── King's Method ─────────────────────────────────────────────────────────────

def king_method(matrix: list[list[int]]):
    A = np.array(matrix, dtype=int)
    n, m = A.shape  # n = machines (rows), m = parts (cols)

    row_order = list(range(n))
    col_order = list(range(m))

    for _ in range(100):  # safety cap
        stable = True

        # Step 1 & 2: compute column weights, sort columns descending
        col_weights = []
        for j in range(A.shape[1]):
            w = sum(A[i, j] * (2 ** (A.shape[0] - 1 - i)) for i in range(A.shape[0]))
            col_weights.append(w)
        new_col_order = sorted(range(len(col_weights)), key=lambda j: -col_weights[j])
        if new_col_order != list(range(A.shape[1])):
            stable = False
        col_order = [col_order[j] for j in new_col_order]
        A = A[:, new_col_order]

        # Step 3 & 4: compute row weights, sort rows descending
        row_weights = []
        for i in range(A.shape[0]):
            w = sum(A[i, j] * (2 ** (A.shape[1] - 1 - j)) for j in range(A.shape[1]))
            row_weights.append(w)
        new_row_order = sorted(range(len(row_weights)), key=lambda i: -row_weights[i])
        if new_row_order != list(range(A.shape[0])):
            stable = False
        row_order = [row_order[i] for i in new_row_order]
        A = A[new_row_order, :]

        if stable:
            break

    return A.tolist(), row_order, col_order


def detect_cells_king(matrix: list[list[int]], row_order: list[int], col_order: list[int]):
    """
    Detect block-diagonal cells in the reordered King matrix.
    Scans top-left to bottom-right, greedily expanding each block.
    """
    A = np.array(matrix, dtype=int)
    n, m = A.shape
    groups: dict[int, int] = {}   # machine_original_index → group_id
    part_cells: dict[int, int] = {}  # part_original_index → group_id

    row_ptr = 0
    col_ptr = 0
    group_id = 0

    while row_ptr < n:
        # Start a new block at (row_ptr, col_ptr)
        block_rows = [row_ptr]
        block_cols = set(j for j in range(col_ptr, m) if A[row_ptr, j] == 1)

        if not block_cols:
            # This machine has no parts from col_ptr onward — isolated
            groups[row_order[row_ptr]] = group_id
            group_id += 1
            row_ptr += 1
            continue

        changed = True
        while changed:
            changed = False
            # Expand rows: add any row that touches current block_cols
            for i in range(row_ptr, n):
                if i not in [r - row_ptr + row_ptr for r in block_rows]:
                    pass
            # Simpler: expand until stable
            new_rows = set(block_rows)
            new_cols = set(block_cols)
            for i in range(row_ptr, n):
                if any(A[i, j] == 1 for j in new_cols):
                    if i not in new_rows:
                        new_rows.add(i)
                        changed = True
            for j in range(col_ptr, m):
                if any(A[i, j] == 1 for i in new_rows):
                    if j not in new_cols:
                        new_cols.add(j)
                        changed = True
            block_rows = sorted(new_rows)
            block_cols = new_cols

        for i in block_rows:
            groups[row_order[i]] = group_id
        for j in block_cols:
            part_cells[col_order[j]] = group_id

        col_ptr = max(block_cols) + 1 if block_cols else col_ptr + 1
        row_ptr = max(block_rows) + 1
        group_id += 1

    return groups, part_cells


# ─── Chaining Method ───────────────────────────────────────────────────────────

def chaining_method(matrix: list[list[int]]):
    A = np.array(matrix, dtype=int)
    n_machines = A.shape[1]  # columns = machines
    n_parts    = A.shape[0]  # rows    = parts

    # Step 1: build machine-machine link matrix
    L = np.zeros((n_machines, n_machines), dtype=int)
    for j in range(n_machines):
        for k in range(j + 1, n_machines):
            shared = int(np.sum((A[:, j] == 1) & (A[:, k] == 1)))
            L[j, k] = shared
            L[k, j] = shared

    # Step 2: classify links
    link_types: dict[tuple[int,int], str] = {}
    for j in range(n_machines):
        for k in range(n_machines):
            if j == k:
                continue
            v = L[j, k]
            if v >= 2:
                link_types[(j, k)] = "strong"
            elif v == 1:
                link_types[(j, k)] = "weak"
            else:
                link_types[(j, k)] = "none"

    # Step 3: Union-Find clustering — strong links first
    parent = list(range(n_machines))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    # Merge on strong links
    for j in range(n_machines):
        for k in range(j + 1, n_machines):
            if link_types.get((j, k)) == "strong":
                union(j, k)

    # Merge on weak links if no isolation
    for j in range(n_machines):
        for k in range(j + 1, n_machines):
            if link_types.get((j, k)) == "weak":
                # Only merge if at least one side is already in a group (has strong link)
                union(j, k)

    # Normalize group IDs
    root_map: dict[int, int] = {}
    gid = 0
    groups: dict[int, int] = {}
    for j in range(n_machines):
        r = find(j)
        if r not in root_map:
            root_map[r] = gid
            gid += 1
        groups[j] = root_map[r]

    # Assign parts to groups
    part_cells: dict[int, int] = {}
    for i in range(n_parts):
        touched = set(groups[j] for j in range(n_machines) if A[i, j] == 1)
        if len(touched) == 1:
            part_cells[i] = touched.pop()
        # exceptional parts handled in analyze

    # Build triangular schema
    triangular = []
    for j in range(n_machines):
        row = []
        for k in range(n_machines):
            if k > j:
                row.append({"value": int(L[j, k]), "type": link_types.get((j, k), "none")})
            elif k == j:
                row.append({"value": 0, "type": "diagonal"})
            else:
                row.append({"value": 0, "type": "empty"})
        triangular.append(row)

    return groups, part_cells, L.tolist(), triangular


# ─── Analyze: exceptions + flows + efficiency ──────────────────────────────────

def analyze(matrix: list[list[int]], groups: dict[int, int], routing: Optional[list[list[int]]] = None):
    A = np.array(matrix, dtype=int)
    n_parts, n_machines = A.shape

    int_groups = {int(k): int(v) for k, v in groups.items()}

    # Classify parts
    exceptional_parts: list[int] = []
    part_cells: dict[int, int] = {}
    for i in range(n_parts):
        touched_groups = set(int_groups[j] for j in range(n_machines) if A[i, j] == 1 and j in int_groups)
        if len(touched_groups) == 1:
            part_cells[i] = touched_groups.pop()
        elif len(touched_groups) > 1:
            exceptional_parts.append(i)
            # assign to the group with the most operations for this part
            counts = {}
            for j in range(n_machines):
                if A[i, j] == 1 and j in int_groups:
                    g = int_groups[j]
                    counts[g] = counts.get(g, 0) + 1
            part_cells[i] = max(counts, key=counts.get)
        else:
            part_cells[i] = -1  # unassigned

    # Crossing flows
    crossing_flows: list[dict] = []
    if routing:
        for i, route in enumerate(routing):
            for step in range(len(route) - 1):
                m_from = route[step]
                m_to   = route[step + 1]
                if m_from < n_machines and m_to < n_machines:
                    g_from = int_groups.get(m_from, -1)
                    g_to   = int_groups.get(m_to, -1)
                    if g_from != g_to and g_from != -1 and g_to != -1:
                        crossing_flows.append({
                            "part": i,
                            "from_machine": m_from,
                            "to_machine": m_to,
                            "from_group": g_from,
                            "to_group": g_to,
                        })

    # Efficiency score
    total_ops = int(np.sum(A))
    internal_ops = 0
    for i in range(n_parts):
        for j in range(n_machines):
            if A[i, j] == 1:
                if part_cells.get(i, -2) == int_groups.get(j, -1):
                    internal_ops += 1
    efficiency = round(internal_ops / total_ops, 4) if total_ops > 0 else 0.0

    # Build cells summary
    all_groups = sorted(set(int_groups.values()))
    cells_summary = {}
    for g in all_groups:
        cells_summary[g] = {
            "machines": [j for j, grp in int_groups.items() if grp == g],
            "parts":    [i for i, grp in part_cells.items() if grp == g],
        }

    return {
        "exceptional_parts": exceptional_parts,
        "part_cells": {str(k): v for k, v in part_cells.items()},
        "crossing_flows": crossing_flows,
        "efficiency": efficiency,
        "internal_ops": internal_ops,
        "total_ops": total_ops,
        "cells_summary": {str(k): v for k, v in cells_summary.items()},
    }


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/king")
def king_endpoint(req: MatrixRequest):
    reordered, row_order, col_order = king_method(req.matrix)
    groups, part_cells = detect_cells_king(reordered, row_order, col_order)
    analysis = analyze(req.matrix, groups)

    return {
        "reordered_matrix": reordered,
        "row_order": row_order,
        "col_order": col_order,
        "groups": {str(k): v for k, v in groups.items()},
        "part_cells": {str(k): v for k, v in part_cells.items()},
        **analysis,
    }


@app.post("/api/chaining")
def chaining_endpoint(req: MatrixRequest):
    groups, part_cells, link_matrix, triangular = chaining_method(req.matrix)
    analysis = analyze(req.matrix, groups)

    return {
        "groups": {str(k): v for k, v in groups.items()},
        "part_cells": {str(k): v for k, v in part_cells.items()},
        "link_matrix": link_matrix,
        "triangular": triangular,
        **analysis,
    }


@app.post("/api/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    groups_int = {int(k): int(v) for k, v in req.groups.items()}
    return analyze(req.matrix, groups_int, req.routing)


# ─── Vercel handler ────────────────────────────────────────────────────────────
# Vercel looks for a variable named `app` — FastAPI IS that ASGI app, so nothing extra needed.
