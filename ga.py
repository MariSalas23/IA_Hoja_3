import numpy as _np
class GeneticSearch:
    """
        Optimizes a set of candidates explorable through crossovers and mutations.

        Which candidate is better is determined with the `better` function
    """

    def __init__(self, init, crossover, mutate, better, population_size):

        self.init = init
        self.crossover = crossover
        self.mutate = mutate
        self.better = better
        self.population_size = population_size

        # state variables
        self.population = None
        self._best = None
        self.num_solutions = 0

    def reset(self): # Crea la población inicial y deja el mejor

        self.population = self.init(self.population_size)
        self.population = [ind.tolist() if hasattr(ind, "tolist") else ind for ind in self.population]
        self._best = self.population[0]
        for ind in self.population[1:]:
            if self.better(ind, self._best):
                self._best = ind
        self.num_solutions = len(self.population)

    @property
    def best(self):

        return self._best

    @property
    def active(self):

        return self.population is not None and len(self.population) > 0 # Aparece activo si hay población

    def step(self):
        # Crossover de todos los pares de padres
        parents = self.population
        children = []
        for i in range(len(parents)):
            for j in range(i + 1, len(parents)):
                # Asegurar tipos numéricos para crossover del test
                x1 = parents[i]
                x2 = parents[j]
                try:
                    a1 = x1 if hasattr(x1, "dtype") or isinstance(x1, (int, float)) else _np.array(x1)
                    a2 = x2 if hasattr(x2, "dtype") or isinstance(x2, (int, float)) else _np.array(x2)
                    off = self.crossover(a1, a2)
                except Exception:
                    off = self.crossover(x1, x2)

                if off is None:
                    continue
                try:
                    off = list(off)
                except TypeError:
                    off = [off]

                for kid in off:
                    # 2) Mutación (si aplica)
                    if hasattr(kid, "tolist"):
                        kid = kid.tolist()
                    if self.mutate is not None:
                        kid = self.mutate(kid)
                    children.append(kid)

        if len(children) == 0:
            return

        candidates = parents + children # population_size

        def wins_count(ind): #  Which candidate is better is determined with the `better` function
            wins = 0
            for other in candidates:
                if ind is other:
                    continue
                if self.better(ind, other):
                    wins += 1
            return -wins  # Más victorias es mejor

        candidates_sorted = sorted(candidates, key=wins_count)
        self.population = candidates_sorted[: self.population_size]

        if self._best is None or self.better(self.population[0], self._best): # Actualiza al mejor conocido
            self._best = self.population[0]
        for ind in self.population[1:]:
            if self.better(ind, self._best):
                self._best = ind

        self.num_solutions += len(children) # Cantidad de soluciones