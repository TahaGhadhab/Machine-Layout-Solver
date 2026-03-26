import numpy as np

def chaining_method(matrix):
    A = np.array(matrix)
    n, m = A.shape # n parts (rows), m machines (cols)
    
    # Step 1: compute link matrix L
    L = np.zeros((m, m), dtype=int)
    for j in range(m):
        for k in range(j + 1, m):
            count = np.sum((A[:, j] == 1) & (A[:, k] == 1))
            L[j, k] = count
            L[k, j] = count
            
    # Step 3: build clusters
    groups = {j: j for j in range(m)}
    
    # Merge strong links (>= 2)
    for j in range(m):
        for k in range(j + 1, m):
            if L[j, k] >= 2:
                gj = groups[j]
                gk = groups[k]
                if gj != gk:
                    for m_idx, g_id in groups.items():
                        if g_id == gk:
                            groups[m_idx] = gj
                            
    # Iterative assignment based on strongest connections
    stable = False
    iterations = 0
    while not stable and iterations < 100:
        stable = True
        iterations += 1
        for j in range(m):
            group_strengths = {}
            for k in range(m):
                if j != k and L[j, k] > 0:
                    gk = groups[k]
                    group_strengths[gk] = group_strengths.get(gk, 0) + L[j, k]
            
            if group_strengths:
                best_group = max(group_strengths.items(), key=lambda x: x[1])[0]
                current_strength = group_strengths.get(groups[j], 0)
                if group_strengths[best_group] > current_strength:
                    groups[j] = best_group
                    stable = False
                    
    # Normalize group IDs (0, 1, 2...)
    unique_groups = sorted(list(set(groups.values())))
    group_map = {old: new for new, old in enumerate(unique_groups)}
    final_groups = {str(m_idx): group_map[g_id] for m_idx, g_id in groups.items()}
    
    return {
        "groups": final_groups,
        "link_matrix": L.tolist()
    }
