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

        return len(self.population) > 0 and self.population is not None # Aparece activo si hay población

    def step(self):
        # Crossover de todos los pares de padres
        parents = self.population
        children = []
        for i in range(len(parents)):
            for j in range(i + 1, len(parents)):
                off = self.crossover(parents[i], parents[j])
                if not off:
                    continue
                for kid in off:
                    # 2) Mutación (si aplica)
                    if self.mutate is not None:
                        kid = self.mutate(kid)
                    children.append(kid)

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