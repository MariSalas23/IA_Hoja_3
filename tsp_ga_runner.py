from ga import GeneticSearch
import numpy as np
import time

def init(locations, random_state, n):
    """
    Creates an initial random population of size n for the TSP problem

    Args:
        locations (list): List of possible locations (just names/indices)
        random_state (np.random.RandomState): random state to control random behavior
        n (int): number of individuals in population

    Returns:
        list: a list of `n` individuals
    """
    if random_state is None:
        random_state = np.random.RandomState()
    locs = list(locations) # locations (list): List of possible locations (just names/indices)
    pop = []
    for _ in range(n):
        p = locs[:]
        random_state.shuffle(p)
        pop.append(p)

    return pop # Returns list: a list of `n` individuals

def crossover(random_state, p1, p2):
    """
    Takes two individuals and combines them into two new routes.

    Args:
        random_state (np.random.RandomState): random state to control random behavior
        p1 (list): parent tour 1 (location indices)
        p2 (list): parent tour 2 (location indices)

    Returns:
        list: A list of size 2 with the offsprings of the parents p1 and p2 as entries, which are also lists themselves
    """
    if random_state is None:
        random_state = np.random.RandomState()

    # 🔧 Asegura listas (si entran como np.ndarray)
    p1 = p1.tolist() if hasattr(p1, "tolist") else list(p1)
    p2 = p2.tolist() if hasattr(p2, "tolist") else list(p2)

    n = len(p1)
    if n < 2:
        return [p1[:], p2[:]]

    for _ in range(3):
        l = random_state.randint(0, n - 1)
        r = random_state.randint(l + 1, n)

        c1 = [None] * n
        c1[l:r] = p1[l:r]
        used1 = set(c1[l:r])
        pos1 = [i for i in range(n) if not (l <= i < r)]
        j = 0
        for x in p2:
            if x not in used1:
                c1[pos1[j]] = x
                j += 1

        c2 = [None] * n
        c2[l:r] = p2[l:r]
        used2 = set(c2[l:r])
        pos2 = [i for i in range(n) if not (l <= i < r)]
        j = 0
        for x in p1:
            if x not in used2:
                c2[pos2[j]] = x
                j += 1

        if c1 != p1 or c2 != p2:
            return [c1, c2]

    return [c1, c2] # Returns list: A list of size 2 with the offsprings of the parents p1 and p2 as entries, which are also lists themselves

def mutate(random_state, i):
    """
    Args:
        random_state (np.random.RandomState): random state to control random behavior
        i (list): tour to be mutated

    Returns:
        list: a mutant copy of the given individual `i`
    """
    if random_state is None:
        random_state = np.random.RandomState()

    seq = i.tolist() if hasattr(i, "tolist") else list(i)
    n = len(seq)
    if n < 2:
        return seq[:]
    a = random_state.randint(0, n)
    b = random_state.randint(0, n)
    while b == a:
        b = random_state.randint(0, n)

    m = seq[:]      
    m[a], m[b] = m[b], m[a]

    return m # Returns list: a mutant copy of the given individual `i`         

def run_genetic_search_for_tsp(tsp, timeout):
    """
    
    Tries to find for (at most) timeout seconds to find a good solution for the TSP given by tsp.

    Args:
        tsp (TSP): The TSP to be solved
        timeout (int): Timeout in seconds after which a solution must have been returned (ideally earlier).

    Returns:
        list: The indices of the locations in the order that described the best tour that could be found.
    """
    start = time.time()
    n = len(tsp.locations)
    locations = list(range(n))
    rs = np.random.RandomState(42)

    init_fn = lambda k: init(locations, rs, k)
    crossover_fn = lambda p1, p2: crossover(rs, p1, p2)
    mutate_fn = lambda ind: mutate(rs, ind)
    better = tsp.is_better_route_than

    pop_size = min(60, max(20, 2 * n))
    ga = GeneticSearch(init=init_fn, crossover=crossover_fn, mutate=mutate_fn,
                       better=better, population_size=pop_size)
    ga.reset()
    the_best = ga.best[:]
    last_improve_t = start
    stagnation = 0

    while True:
        now = time.time()
        if now - start >= timeout:
            break

        ga.step()

        if better(ga.best, the_best):
            the_best = ga.best[:]
            last_improve_t = now
            stagnation = 0
        else:
            stagnation += 1

        stall_limit = min(3.0, max(1.0, timeout * 0.1))
        if (now - last_improve_t > stall_limit) or (stagnation > 25):
            rs = np.random.RandomState(rs.randint(0, 1_000_000))
            init_fn = lambda k: init(locations, rs, k)
            crossover_fn = lambda p1, p2: crossover(rs, p1, p2)
            mutate_fn = lambda ind: mutate(rs, ind)
            ga = GeneticSearch(init=init_fn, crossover=crossover_fn, mutate=mutate_fn,
                               better=better, population_size=pop_size)
            ga.reset()
            ga.population[0] = the_best[:]
            ga._best = ga.population[0]
            for ind in ga.population[1:]:
                if better(ind, ga._best):
                    ga._best = ind
            stagnation = 0
            last_improve_t = time.time()

    if not isinstance(the_best, list) or len(the_best) != n:
        the_best = locations[:]
        rs.shuffle(the_best)

    return the_best # Returns list: The indices of the locations in the order that described the best tour that could be found.