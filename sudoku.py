

def get_bcn_for_sudoku(sudoku):
    """
        Receives a Sudoku and creates a BCN definition from it, using the binarized All-Diff Constraint

    Args:
        sudoku (np.ndarray): numpy array describing the sudoku

    Returns:
        (domains, constraints): BCN describing the conditions for the given Sudoku
    """
    raise NotImplementedError