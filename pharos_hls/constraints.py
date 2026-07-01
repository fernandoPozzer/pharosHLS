from .random_var import RandomVar

class Contraint:

    def __init__(self, param_name: str):
        self.name = param_name
        self.value = -1

    def apply(self, random_var: RandomVar):
        raise Exception("Constraint's 'apply' method not implemented.")

class LessThan(Contraint):

    def __init__(self, param_name: str):
        super().__init__(param_name)

    def apply(self, random_var: RandomVar):
        
        random_var.limit_max_value(self.value - 1)

class LessOrEqualTo(Contraint):

    def __init__(self, param_name: str):
        super().__init__(param_name)

    def apply(self, random_var: RandomVar):
        
        random_var.limit_max_value(self.value)

class DivisorOf(Contraint):

    def __init__(self, param_name: str):
        super().__init__(param_name)

    def apply(self, random_var: RandomVar):
        
        random_var.define_constraint(lambda x : self.value % x == 0)