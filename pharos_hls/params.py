from .random_var import RandomVar

class HyperParam:
    
    def __init__(self, name: str, range: tuple, constraints: list = []):

        if len(range) != 2:
            raise Exception("Range must be a sized 2 tuple.")
        
        self.name = name
        self.range = range
        self.constraints = constraints
        
    def generate(self):

        random_var = RandomVar(self.range[0], self.range[1])

        for constraint in self.constraints:            
            constraint.apply(random_var)

        return random_var.get_value()
    
class CustomVectorParam:
    
    def __init__(self, param_type, func_params, func):

        self.param_type = param_type

        if not isinstance(func_params, tuple):
            self.func_params = (func_params,)
        
        self.func = func
        self.input_or_output = False

    def get_custom_vector(self, param_values):
        args = []

        for param in self.func_params:

            if not param in param_values:
                raise Exception(f"Param {param} not in generated values dictionary")
            
            args.append(param_values[param])

        return self.func(*args) 
    
class FunctionParam:

    def __init__(self, param_type: str, input_or_output = False):

        self.input_or_output = input_or_output
        self.param_type = param_type

class FunctionVectorParam:

    def __init__(self, calculate_shape_func_params, calculate_shape_func, param_type: str, input_or_output = False):

        if not isinstance(calculate_shape_func_params, tuple):
            calculate_shape_func_params = (calculate_shape_func_params, )

        self.calculate_shape_func_params = calculate_shape_func_params
        self.calculate_shape_func = calculate_shape_func
        self.input_or_output = input_or_output
        self.param_type = param_type

    def get_param_shape(self, param_values):

        input_values = []

        for param in self.calculate_shape_func_params:

            if param not in param_values:
                raise Exception(f"Calculate shape parameter '{param}' not in params dictionary.")
            
            input_values.append(param_values[param])

        shape = self.calculate_shape_func(*input_values)

        if not isinstance(shape, tuple):
            shape = (shape, )

        return shape