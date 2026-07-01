import numpy as np

from .param_generation import generate_param_values
from .params import *

def generate_tensor(shape):
    # np.random.seed(seed)
    return np.random.rand(*shape) - 0.5

def get_template_args_str(param_values, template_args):

    if template_args is None:
        return ""
    
    if not isinstance(template_args, tuple):
        template_args = (template_args, )
    
    template_args_values = []

    for arg in template_args:

        if arg not in param_values:
            raise Exception(f"Template argument '{arg}' not in params dictionary.")
        
        template_args_values.append(param_values[arg])

    args_str = ",".join(str(x) for x in template_args_values)
    return f"<{args_str}>"

def get_bracket_str(arr):

    if arr is not None:
        return ''.join(f'[{x}]' for x in arr)

    return ""

def get_func_args_str(param_values, func_args):

    args_str = ""

    for arg_name, value in func_args.items():

        if not value.input_or_output:
            continue

        if args_str != "":
            args_str += ", "

        if isinstance(value, FunctionVectorParam):
            shape = value.get_param_shape(param_values)
            args_str += f"{value.param_type} {arg_name}{get_bracket_str(shape)}"
        
        else:
            args_str += f"{value.param_type}& {arg_name}"

    return args_str

def tensor_to_str(mat, num_tabs = 0):

    if len(mat.shape) == 1:

        s = "\t" * num_tabs + "{"

        for i in range(mat.shape[0]):
            
            s += f"{mat[i]:.10f}"

            if i < mat.shape[0] - 1:
                s += ", "

        return s + "}"
    
    s = "\t" * num_tabs + "{"

    for i in range(mat.shape[0]):

        s += "\n" + tensor_to_str(mat[i], num_tabs + 1)

        if i < mat.shape[0] - 1:
            s += ",\n"

    s += "\n" + "\t" * num_tabs + "}"
    return s

def create_needed_tensors_code(param_values, func_args):

    code = ""

    for arg_name, value in func_args.items():

        if value.input_or_output:
            continue

        if isinstance(value, CustomVectorParam):

            tensor = value.get_custom_vector(param_values)
            code += f"{value.param_type} {arg_name}{get_bracket_str(tensor.shape)} = {tensor_to_str(tensor)};\n\n"
            
        else:

            shape = value.get_param_shape(param_values)
            tensor = generate_tensor(shape)
            code += f"type_t {arg_name}{get_bracket_str(shape)} = {tensor_to_str(tensor)};\n\n"

    return code

def generate_code(folder_path, generated_values, params, func_name: str, func_args, template_args = None):

    param_values = generate_param_values(params)

    while param_values in generated_values:
        param_values = generate_param_values(params)

    generated_values.append(param_values)

    template_args_str = get_template_args_str(param_values, template_args)
    func_args_str = get_func_args_str(param_values, func_args)

    top_func_header = f"void explore ({func_args_str})"

    explore_h = "#pragma once\n"
    explore_h += "#include <ap_fixed.h>\n"
    explore_h += '#include "implementation.h"\n'

    # ap_fixed = f"ap_fixed<{param_values['quant']}, 0>"
    # explore_h += f"typedef {ap_fixed} type_t;\n\n"

    # explore_h += create_needed_tensors_code(param_values, func_args)
    explore_h += f"\n\n{top_func_header};"

    with open(f"{folder_path}/explore.h", "w") as f:
        f.write(explore_h)

    explore_cpp = '#include "implementation.h"\n'
    explore_cpp += '#include "explore.h"\n\n'
    explore_cpp += create_needed_tensors_code(param_values, func_args)
    explore_cpp += f"\n\n{top_func_header}\n{'{'}\n"
    explore_cpp += f"\t{func_name}{template_args_str}({','.join(key for key in func_args)});\n{'}'}\n"

    with open(f"{folder_path}/explore.cpp", "w") as f:
        f.write(explore_cpp)

    return dict(sorted(param_values.items()))
