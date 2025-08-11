import numpy as np
import matplotlib.pyplot as plt


class TSP:

    def __init__(self, n, random_state=None, width_x=1, width_y=1):
        if random_state is None:
            random_state = np.random.RandomState()
        self.width_x = width_x
        self.width_y = width_y
        self.locations = []
        for i in range(n):
            self.locations.append(np.array([random_state.random() * width_x, random_state.random() * width_y]))
        self.distances = np.zeros((n, n))
        for i, l1 in enumerate(self.locations):
            for j, l2 in enumerate(self.locations[:i]):
                self.distances[i, j] = self.distances[j, i] = np.linalg.norm(l1 - l2)

    def get_cost_of_route(self, r):
        c = 0
        for i, l in enumerate(r[1:], start=1):
            prev_l = r[i - 1]
            c += self.distances[prev_l, l]
        return c

    def is_better_route_than(self, r1, r2):
        """
        :param r1: list of locations to visit
        :param r2: list of locations to visit
        :return: True if route r1 is better than route r2; otherwise False
        """
        c1 = self.get_cost_of_route(r1)
        c2 = self.get_cost_of_route(r2)
        return c1 < c2

    def visualize(self):
        fig, ax = plt.subplots(figsize=(self.width_x * 2, self.width_y * 2))
        ax.scatter([l[0] for l in self.locations], [l[1] for l in self.locations])
        plt.show()

        fig, ax = plt.subplots()
        ax.imshow(self.distances, cmap="Reds")
        plt.show()

