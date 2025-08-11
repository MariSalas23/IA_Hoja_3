import numpy as np
from ac import get_binarized_constraints_for_all_diff

def get_bcn_for_sudoku(sudoku):
    """
    Receives a Sudoku and creates a BCN definition from it, using the binarized All-Diff Constraint

    Args:
        sudoku (np.ndarray): numpy array describing the sudoku

    Returns:
        (domains, constraints): BCN describing the conditions for the given Sudoku
    """
    n = sudoku.shape[0]
    values = list(range(1, n + 1))

    domains = {}
    for r in range(n):
        for c in range(n):
            variable = (r, c)
            value = int(sudoku[r, c])
            if value == 0:
                domains[variable] = values[:]
            else:
                domains[variable] = [value]

    constraints = {} 
    def merge_constraints(dst, src): # Combina constraints

        for k, f in src.items():
            if k in dst:
                g = dst[k]
                dst[k] = (lambda f1, f2: (lambda a: f1(a) and f2(a)))(g, f)
            else:
                dst[k] = f

    for r in range(n):
        row_vars = {(r, c): domains[(r, c)] for c in range(n)}
        cons_row = get_binarized_constraints_for_all_diff(row_vars)
        merge_constraints(constraints, cons_row)

    for c in range(n):
        col_vars = {(r, c): domains[(r, c)] for r in range(n)}
        cons_col = get_binarized_constraints_for_all_diff(col_vars)
        merge_constraints(constraints, cons_col)

    b = int(np.sqrt(n))
    assert b * b == n, "9x9, 16x16"
    for br in range(0, n, b):
        for bc in range(0, n, b):
            block_vars = {}
            for r in range(br, br + b):
                for c in range(bc, bc + b):
                    block_vars[(r, c)] = domains[(r, c)]
            cons_block = get_binarized_constraints_for_all_diff(block_vars)
            merge_constraints(constraints, cons_block)

    return domains, constraints # Returns (domains, constraints): BCN describing the conditions for the given Sudoku