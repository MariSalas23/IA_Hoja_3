from pathless_tree_search import PathlessTreeSearch
from collections import deque
import copy

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
    domains, constraints = bcn # bcn ((domains, constraints))
    Di = domains[X_i]
    Dj = domains[X_j]

    k = tuple(sorted((X_i, X_j)))
    if k not in constraints:
        return Di[:], False

    cons = constraints[k]
    D_i_prime = []
    for xi in Di: # Busca valor valido para la pareja (xi, xj)
        if any(cons({X_i: xi, X_j: xj}) for xj in Dj):
            D_i_prime.append(xi)

    changed = len(D_i_prime) != len(Di) # Boolean value that is True if the domain is now smaller than before and False otherwise

    return D_i_prime, changed # Returns a tuple (D_i', changed)

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
    domains0, constraints = bcn
    domains = {} # Copia de los dominios
    for v, d in domains0.items():
        domains[v] = d[:] 

    queue = deque() # Cola
    for (a, b) in constraints.keys(): # Inicializa cola con ambos sentidos de cada arco binario
        queue.append((a, b))
        queue.append((b, a))

    while queue:
        Xi, Xj = queue.popleft()
        D_i_prime, changed = revise((domains, constraints), Xi, Xj)
        if changed:
            domains[Xi] = D_i_prime
            if len(D_i_prime) == 0:
                return (domains, constraints), False  # Inconsistente

            for (a, b) in constraints.keys():
                if a == Xi and b != Xj:
                    queue.append((b, Xi))
                elif b == Xi and a != Xj:
                    queue.append((a, Xi))

    return (domains, constraints), True # Returns (bcn', feasible)

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
    (domains0, constraints) = bcn
    (bcn_root, feasible) = ac3((domains0, constraints))
    root_domains = bcn_root[0]

    def is_final(dom):
        for valores in dom.values():
            if len(valores) != 1: # Solucuión parcial
                return False
        return True # Si ninguno falla todas las variables están fijadas a un único valor

    if not feasible:   
        return PathlessTreeSearch(n0=root_domains, succ=lambda _: [], goal=is_final), (lambda _: {}) # Sin solución

    def select_variable(dom):
        if phi is not None:
            return phi(dom)
        best_variable, best_size = None, 10**9
        for k, v in dom.items():
            if 1 < len(v) < best_size:
                best_variable, best_size = k, len(v)
        return best_variable

    def succ(dom):
        var = select_variable(dom)
        if var is None:
            return []
        children = []
        for val in dom[var]:
            new_dom = {k: vals[:] for k, vals in dom.items()}
            new_dom[var] = [val]
            (bcn2, feas2) = ac3((new_dom, constraints))
            if feas2:
                children.append(bcn2[0])
        return children

    search = PathlessTreeSearch(n0=root_domains, succ=succ, goal=is_final, better=None, order="bfs") # search is a PathlessTreeSearch object
    decoder = lambda node: {k: v[0] for k, v in node.items()} # decoder is a function to decode a node to an assignment

    return search, decoder # Returns (search, decoder)

def get_binarized_constraints_for_all_diff(domains):
    """
        Derives all binary constraints that are necessary to make sure that all variables given in `domains` will have different values.

    Args:
        domains (dict): dictionary where keys are variable names and values are lists of possible values for the respective variable.

    Returns:
        dict: dictionary where keys are constraint names (it is recommended to use tuples, with entries in the tuple being the variable names sorted lexicographically) and values are the functions encoding the respective constraint set membership
    """
    variables = sorted(domains.keys())
    constraints = {} # dictionary where keys are constraint names (it is recommended to use tuples, with entries in the tuple being the variable names sorted lexicographically) and values are the functions encoding the respective constraint set membership

    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            a, b = variables[i], variables[j]

            def make_neq(x, y):
                def _neq(assign):
                    if x in assign and y in assign:
                        return assign[x] != assign[y]
                    return True  # Asignación parcial
                return _neq

            constraints[(a, b)] = make_neq(a, b)

    return constraints # Returns dict
