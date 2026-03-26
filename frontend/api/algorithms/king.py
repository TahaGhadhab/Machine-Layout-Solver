import numpy as np

def king_method(matrix):
    A = np.array(matrix)
    n, m = A.shape
    row_indices = np.arange(n)
    col_indices = np.arange(m)
    
    stable = False
    iterations = 0
    max_iter = 100
    
    while not stable and iterations < max_iter:
        stable = True
        iterations += 1
        
        # Step 1: compute column weights (using Python ints to avoid overflow)
        C = []
        for j in range(m):
            w = 0
            for i in range(n):
                w += int(A[i, j]) * (2 ** (n - 1 - i))
            C.append(w)
            
        # Sort columns descending
        new_col_order = np.argsort(C)[::-1]
        
        if not np.array_equal(new_col_order, np.arange(m)):
            stable = False
            A = A[:, new_col_order]
            col_indices = col_indices[new_col_order]
            
        # Step 3: compute row weights
        L = []
        for i in range(n):
            w = 0
            for j in range(m):
                w += int(A[i, j]) * (2 ** (m - 1 - j))
            L.append(w)
            
        # Sort rows descending
        new_row_order = np.argsort(L)[::-1]
        
        if not np.array_equal(new_row_order, np.arange(n)):
            stable = False
            A = A[new_row_order, :]
            row_indices = row_indices[new_row_order]
            
    return {
        "ordered_matrix": A.tolist(),
        "row_indices": row_indices.tolist(),
        "col_indices": col_indices.tolist(),
        "iterations": iterations
    }
