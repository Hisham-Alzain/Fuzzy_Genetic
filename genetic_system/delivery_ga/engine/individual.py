"""Genome container used by the delivery GA."""


class Individual:
    __slots__ = ("assign", "order", "fitness", "makespan", "lengths", "credit")

    def __init__(self, assign, order):
        self.assign = assign
        self.order = order
        self.fitness = None
        self.makespan = None
        self.lengths = None
        self.credit = 0.0

    def copy(self):
        clone = Individual(self.assign.copy(), self.order.copy())
        clone.fitness = self.fitness
        clone.makespan = self.makespan
        clone.lengths = self.lengths
        clone.credit = self.credit
        return clone

