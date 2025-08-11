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

    def reset(self):
        raise NotImplementedError

    @property
    def best(self):
        return self._best

    @property
    def active(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError
