from http.server import BaseHTTPRequestHandler
import json

# ─── Pure Python algorithms (no numpy needed) ──────────────────────────────────

def king_method(matrix):
    A = [row[:] for row in matrix]
    n = len(A)
    m = len(A[0]) if A else 0
    row_order = list(range(n))
    col_order = list(range(m))

    for _ in range(100):
        stable = True

        col_weights = []
        for j in range(len(A[0])):
            w = sum(A[i][j] * (2 ** (len(A) - 1 - i)) for i in range(len(A)))
            col_weights.append(w)
        new_col_idx = sorted(range(len(col_weights)), key=lambda j: -col_weights[j])
        if new_col_idx != list(range(len(A[0]))):
            stable = False
        col_order = [col_order[j] for j in new_col_idx]
        A = [[A[i][j] for j in new_col_idx] for i in range(len(A))]

        row_weights = []
        for i in range(len(A)):
            w = sum(A[i][j] * (2 ** (len(A[0]) - 1 - j)) for j in range(len(A[0])))
            row_weights.append(w)
        new_row_idx = sorted(range(len(row_weights)), key=lambda i: -row_weights[i])
        if new_row_idx != list(range(len(A))):
            stable = False
        row_order = [row_order[i] for i in new_row_idx]
        A = [A[i] for i in new_row_idx]

        if stable:
            break

    return A, row_order, col_order


def detect_cells_king(A, row_order, col_order):
    n = len(A)
    m = len(A[0]) if A else 0
    groups = {}
    part_cells = {}
    row_ptr = 0
    col_ptr = 0
    group_id = 0

    while row_ptr < n:
        seed_cols = set(j for j in range(col_ptr, m) if A[row_ptr][j] == 1)

        if not seed_cols:
            groups[row_order[row_ptr]] = group_id
            group_id += 1
            row_ptr += 1
            continue

        block_rows = {row_ptr}
        block_cols = seed_cols

        changed = True
        while changed:
            changed = False
            for i in range(row_ptr, n):
                if i not in block_rows and any(A[i][j] == 1 for j in block_cols):
                    block_rows.add(i)
                    changed = True
            for j in range(col_ptr, m):
                if j not in block_cols and any(A[i][j] == 1 for i in block_rows):
                    block_cols.add(j)
                    changed = True

        sorted_rows = sorted(block_rows)
        contiguous = []
        for idx, r in enumerate(sorted_rows):
            if idx == 0 or r == sorted_rows[idx - 1] + 1:
                contiguous.append(r)
            else:
                break

        final_cols = set(
            j for j in range(col_ptr, m)
            if any(A[i][j] == 1 for i in contiguous)
        )

        for i in contiguous:
            groups[row_order[i]] = group_id
        for j in final_cols:
            part_cells[col_order[j]] = group_id

        col_ptr = max(final_cols) + 1 if final_cols else col_ptr + 1
        row_ptr = max(contiguous) + 1
        group_id += 1

    return groups, part_cells


def chaining_method(matrix):
    n_parts = len(matrix)
    n_machines = len(matrix[0]) if matrix else 0

    L = [[0] * n_machines for _ in range(n_machines)]
    for j in range(n_machines):
        for k in range(j + 1, n_machines):
            shared = sum(1 for i in range(n_parts) if matrix[i][j] == 1 and matrix[i][k] == 1)
            L[j][k] = shared
            L[k][j] = shared

    link_types = {}
    for j in range(n_machines):
        for k in range(n_machines):
            if j == k:
                continue
            v = L[j][k]
            link_types[(j, k)] = "strong" if v >= 2 else "weak" if v == 1 else "none"

    parent = list(range(n_machines))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    for j in range(n_machines):
        for k in range(j + 1, n_machines):
            if link_types.get((j, k)) == "strong":
                union(j, k)
    for j in range(n_machines):
        for k in range(j + 1, n_machines):
            if link_types.get((j, k)) == "weak":
                union(j, k)

    root_map = {}
    gid = 0
    groups = {}
    for j in range(n_machines):
        r = find(j)
        if r not in root_map:
            root_map[r] = gid
            gid += 1
        groups[j] = root_map[r]

    part_cells = {}
    for i in range(n_parts):
        touched = set(groups[j] for j in range(n_machines) if matrix[i][j] == 1)
        if len(touched) == 1:
            part_cells[i] = touched.pop()

    triangular = []
    for j in range(n_machines):
        row = []
        for k in range(n_machines):
            if k > j:
                row.append({"value": L[j][k], "type": link_types.get((j, k), "none")})
            elif k == j:
                row.append({"value": 0, "type": "diagonal"})
            else:
                row.append({"value": 0, "type": "empty"})
        triangular.append(row)

    return groups, part_cells, L, triangular


def analyze(matrix, groups, routing=None):
    n_parts = len(matrix)
    n_machines = len(matrix[0]) if matrix else 0
    int_groups = {int(k): int(v) for k, v in groups.items()}

    exceptional_parts = []
    part_cells = {}
    for i in range(n_parts):
        touched = set(int_groups[j] for j in range(n_machines) if matrix[i][j] == 1 and j in int_groups)
        if len(touched) == 1:
            part_cells[i] = touched.pop()
        elif len(touched) > 1:
            exceptional_parts.append(i)
            counts = {}
            for j in range(n_machines):
                if matrix[i][j] == 1 and j in int_groups:
                    g = int_groups[j]
                    counts[g] = counts.get(g, 0) + 1
            part_cells[i] = max(counts, key=counts.get)
        else:
            part_cells[i] = -1

    crossing_flows = []
    if routing:
        for i, route in enumerate(routing):
            for step in range(len(route) - 1):
                mf, mt = route[step], route[step + 1]
                if mf < n_machines and mt < n_machines:
                    gf = int_groups.get(mf, -1)
                    gt = int_groups.get(mt, -1)
                    if gf != gt and gf != -1 and gt != -1:
                        crossing_flows.append({"part": i, "from_machine": mf, "to_machine": mt, "from_group": gf, "to_group": gt})

    total_ops = sum(matrix[i][j] for i in range(n_parts) for j in range(n_machines))
    internal_ops = sum(
        1 for i in range(n_parts) for j in range(n_machines)
        if matrix[i][j] == 1 and part_cells.get(i, -2) == int_groups.get(j, -1)
    )
    efficiency = round(internal_ops / total_ops, 4) if total_ops > 0 else 0.0

    all_groups = sorted(set(int_groups.values()))
    cells_summary = {
        str(g): {
            "machines": [j for j, grp in int_groups.items() if grp == g],
            "parts": [i for i, grp in part_cells.items() if grp == g],
        }
        for g in all_groups
    }

    return {
        "exceptional_parts": exceptional_parts,
        "part_cells": {str(k): v for k, v in part_cells.items()},
        "crossing_flows": crossing_flows,
        "efficiency": efficiency,
        "internal_ops": internal_ops,
        "total_ops": total_ops,
        "cells_summary": cells_summary,
    }


# ─── Vercel serverless handler ─────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        path = self.path.rstrip("/")

        try:
            if path == "/api/king":
                matrix = body["matrix"]
                reordered, row_order, col_order = king_method(matrix)
                groups, part_cells = detect_cells_king(reordered, row_order, col_order)
                result = {
                    "reordered_matrix": reordered,
                    "row_order": row_order,
                    "col_order": col_order,
                    "groups": {str(k): v for k, v in groups.items()},
                    "part_cells": {str(k): v for k, v in part_cells.items()},
                    **analyze(matrix, groups),
                }

            elif path == "/api/chaining":
                matrix = body["matrix"]
                groups, part_cells, link_matrix, triangular = chaining_method(matrix)
                result = {
                    "groups": {str(k): v for k, v in groups.items()},
                    "part_cells": {str(k): v for k, v in part_cells.items()},
                    "link_matrix": link_matrix,
                    "triangular": triangular,
                    **analyze(matrix, groups),
                }

            elif path == "/api/analyze":
                matrix = body["matrix"]
                groups = {int(k): int(v) for k, v in body["groups"].items()}
                routing = body.get("routing")
                result = analyze(matrix, groups, routing)

            else:
                self._respond(404, {"error": "Not found"})
                return

            self._respond(200, result)

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
