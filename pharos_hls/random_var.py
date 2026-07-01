import random

class RandomVar:

    def __init__(self, min_value, max_value):

        self.possible_values = list(range(min_value, max_value + 1))

    def limit_max_value(self, max_value):

        self.possible_values = [x for x in self.possible_values if x <= max_value]

    def limit_min_value(self, min_value):

        self.possible_values = [x for x in self.possible_values if x >= min_value]

    def define_constraint(self, constraint):

        self.possible_values = [x for x in self.possible_values if constraint(x)]

    def get_value(self):

        return random.choice(self.possible_values)