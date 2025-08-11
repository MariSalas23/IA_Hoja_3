from collections import deque
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
    domains, constraints = bcn
    Di = domains[X_i]
    Dj = domains[X_j]

    key = tuple(sorted((X_i, X_j)))
    if key not in constraints:
        return Di[:], False

    cons = constraints[key]
    D_i_prime = []
    for xi in Di:
        # xi solo si existe algún xj en Dj que satisface la constraint
        if any(cons({X_i: xi, X_j: xj}) for xj in Dj):
            D_i_prime.append(xi)

    changed = len(D_i_prime) != len(Di)
    return D_i_prime, changed

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
    # Inicializa cola con ambos sentidos de cada arco binario
    for (a, b) in constraints.keys():
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

# ------------------------
# Helpers para acelerar (no quitan tus comentarios de arriba)
# ------------------------

def _build_neighbors(constraints):
    """Mapa de vecinos: para cada variable, quién comparte constraint con ella."""
    neigh = {}
    for (a, b) in constraints.keys():
        if a not in neigh: neigh[a] = set()
        if b not in neigh: neigh[b] = set()
        neigh[a].add(b)
        neigh[b].add(a)
    return neigh

def ac3_from(bcn, start_vars, neighbors): # Para la clasificación en board
    domains0, constraints = bcn
    domains = {}
    for v, d in domains0.items():
        domains[v] = d[:]  # copia

    queue = deque()
    # Inicializa la cola SOLO con arcos que entran a cada start_var
    for X in start_vars:
        for Y in neighbors.get(X, ()):
            queue.append((Y, X))

    while queue:
        Xi, Xj = queue.popleft()
        D_i_prime, changed = revise((domains, constraints), Xi, Xj)
        if changed:
            domains[Xi] = D_i_prime
            if len(D_i_prime) == 0:
                return (domains, constraints), False  # Inconsistente
            for Xk in neighbors.get(Xi, ()):
                if Xk != Xj:
                    queue.append((Xk, Xi))

    return (domains, constraints), True

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

    if not feasible:
        def _is_final(_): 
            return False
        return PathlessTreeSearch(n0=root_domains, succ=lambda _: [], goal=_is_final), (lambda _: {})

    neighbors = _build_neighbors(constraints)
    def is_final(dom):
        for valores in dom.values():
            if len(valores) != 1:
                return False # Solución parcial
        return True

    def select_var(dom):
        if phi is not None:
            return phi(dom)
        best_var, best_size, best_deg = None, 10**9, -1
        for k, v in dom.items():
            if len(v) > 1:
                sz = len(v)
                deg = len(neighbors.get(k, ()))
                if (sz < best_size) or (sz == best_size and deg > best_deg):
                    best_var, best_size, best_deg = k, sz, deg
        return best_var

    def succ(dom):
        var = select_var(dom)
        if var is None:
            return []
        children = []
        for val in dom[var]:
            new_dom = {k: vals[:] for k, vals in dom.items()}
            new_dom[var] = [val]
            (bcn2, feas2) = ac3_from((new_dom, constraints), start_vars=[var], neighbors=neighbors)
            if feas2:
                children.append(bcn2[0])
        return children

    search = PathlessTreeSearch(n0=root_domains, succ=succ, goal=is_final, better=None, order="bfs") # search is a PathlessTreeSearch object

    def decoder(node): # decoder is a function to decode a node to an assignment
        asignacion = {}
        for var, dominio in node.items():
            asignacion[var] = dominio[0] 
        return asignacion

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