def dfs(name, params, generated_values):

    if name not in params:
        raise Exception(f"Contraint '{name}' not found in params dictionary.")
    
    if name in generated_values:
        return
    
    if isinstance(params[name], int):
        generated_values[name] = params[name]
        return
    
    if params[name].constraints is None:
        generated_values[name] = params[name].generate()
        return

    for constraint in params[name].constraints:

        if constraint.name not in generated_values:
            dfs(constraint.name, params, generated_values)
        
        constraint.value = generated_values[constraint.name]

    generated_values[name] = params[name].generate()

def generate_param_values(params):

    generated_values = {}

    for name in params.keys():
        dfs(name, params, generated_values)

    return generated_values