import numpy as np

def analyze(matrix, groups, routing=None):
    A = np.array(matrix)
    n, m = A.shape
    
    # Triangular schema
    L = np.zeros((m, m), dtype=int)
    for j in range(m):
        for k in range(j + 1, m):
            count = np.sum((A[:, j] == 1) & (A[:, k] == 1))
            L[j, k] = count
            L[k, j] = count
            
    T = np.zeros((m, m), dtype=int)
    for j in range(m):
        for k in range(j + 1, m):
            T[j, k] = L[j, k]
            
    # Part assignment + exceptions
    # Groups mapping: machine string key -> group id
    machine_groups = {int(k): v for k, v in groups.items()}
    
    exceptional_parts = []
    part_assignments = []
    
    for i in range(n):
        group_set = set()
        for j in range(m):
            if A[i, j] == 1:
                group_set.add(machine_groups.get(j, -1))
                
        if len(group_set) == 1:
            part_assignments.append(list(group_set)[0])
        else:
            part_assignments.append(-1) # exceptional
            exceptional_parts.append(i)
            
    # Crossing flows detection if routing provided
    crossing_flows = 0
    if routing:
        for r in routing:
            for idx in range(len(r) - 1):
                m1, m2 = r[idx], r[idx+1]
                if machine_groups.get(m1) != machine_groups.get(m2):
                    crossing_flows += 1
                    
    # Efficiency score (internal operations / total operations)
    total_ops = np.sum(A)
    internal_ops = 0
    for i in range(n):
        for j in range(m):
            if A[i, j] == 1:
                # Part belongs to group, and machine is in the same group
                p_group = part_assignments[i]
                if p_group != -1 and p_group == machine_groups.get(j, -1):
                    internal_ops += 1
                    
    efficiency = internal_ops / total_ops if total_ops > 0 else 0
    
    return {
        "triangular_schema": T.tolist(),
        "part_assignments": part_assignments,
        "exceptional_parts": exceptional_parts,
        "crossing_flows": crossing_flows,
        "efficiency": efficiency
    }
