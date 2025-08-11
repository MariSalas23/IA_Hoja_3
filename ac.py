from pathless_tree_search import PathlessTreeSearch


def revise(bcn, X_i, X_j):
    """
    Returns a tuple (D_i', changed), where
        - D_i' is the maximal subset of the domain of X_i that is arc consistent with X_j
        - changed is a boolean value that is True if the domain is now smaller than before and False otherwise

    Args:
        bcn ((domains, constraints)): The BCN containting the constraints, in particular the one for X_i and X_j
        X_i (Any): descriptor of the variable X_i
        X_j (Any): descriptor of the variable X_j
    """
    return None, False

def ac3(bcn):
    """
    Reduces the domains in a BCN to make it arc consistent, if possible.

    Args:
        bcn ((domains, constraints)): The BCN to make arc consistent (if possible)

    Returns:
        (bcn', feasible), where
        - bcn' is the maximum subnetwork (in terms of domains) of bcn that is consistent
        - feasible is a boolean that is False if it could be verified that bcn doesn't have a solution and True otherwise
    """
    return None


def get_tree_search_for_bcn(bcn, phi=None):
    """
        Generates a PathlessTreeSearch that can find a solution in the search space described by the BCN.

    Args:
        bcn ((domains, constraints)): The BCN in which we look for a solution.
        phi (func, optional): Function that takes a dictionary of domains (variables are keys) and selects the variable to fix next.

    Returns:
        (search, decoder), where
         - search is a PathlessTreeSearch object
         - decoder is a function to decode a node to an assignment
    """
    raise NotImplementedError

def get_binarized_constraints_for_all_diff(domains):
    """
        Derives all binary constraints that are necessary to make sure that all variables given in `domains` will have different values.

    Args:
        domains (dict): dictionary where keys are variable names and values are lists of possible values for the respective variable.

    Returns:
        dict: dictionary where keys are constraint names (it is recommended to use tuples, with entries in the tuple being the variable names sorted lexicographically) and values are the functions encoding the respective constraint set membership
    """
    raise NotImplementedError
