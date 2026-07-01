import csv
import os

from .vitis_utils import *
from .backend_utils import copy_backend_to
from .code_generator import generate_code
from .get_synth_info import *

def save_dict_to_csv(data: dict, file_path: str):
    file_exists = os.path.exists(file_path)
    write_header = True

    # Check if file exists and is not empty
    if file_exists and os.path.getsize(file_path) > 0:
        write_header = False

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())

        if write_header:
            writer.writeheader()

        writer.writerow(data)

def copy_to_implementation_header(file_path, folder_path):

    # Check if the source file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read the content of the source file
    with open(file_path, 'r', encoding='utf-8') as src_file:
        content = src_file.read()

    # Define the destination path (same directory)
    dest_path = os.path.join(folder_path, "implementation.h")

    # Write the content to the new file
    with open(dest_path, 'w', encoding='utf-8') as dest_file:
        dest_file.write(content)

class PharosHLS:

    def __init__(self, folder_path: str):

        self.folder_path = folder_path

        if not os.path.exists(folder_path):
            copy_backend_to(folder_path)

        self.has_defined_top_function = False
        self.has_defined_testbench = False
        self.top_function = ""

    def define_function_to_explore(self,
                                   function_name: str,
                                   function_impl_file_path: str,
                                   params,
                                   func_args,
                                   template_args = None):
        
        self.has_defined_top_function = True
        self.top_function = function_name

        copy_to_implementation_header(function_impl_file_path, self.folder_path)

        self.params = params
        self.func_args = func_args
        self.template_args = template_args

    def define_testbench(self, testbench_file_path: str):

        if not os.path.isfile(testbench_file_path):
            raise FileNotFoundError(f"File not found: {testbench_file_path}")

        with open(testbench_file_path, 'r', encoding='utf-8') as src_file:
            content = src_file.read()

        dest_path = os.path.join(self.folder_path, "testbench.cpp")

        with open(dest_path, 'w', encoding='utf-8') as dest_file:
            dest_file.write(content)

        self.has_defined_testbench = True

    def explore_synth(self, frequency_MHz: int, number_of_samples: int, part = "xc7z020clg400-1", simulate_with_testbench = False):

        if not self.has_defined_top_function:
            raise Exception("Top function must be defined before running synthesis.")

        if frequency_MHz <= 0:
            raise Exception("Frequency must be greater than 0.")
        
        if simulate_with_testbench and not self.has_defined_testbench:
            raise Exception("Testbench must be defined before simulating the configurations.")
        
        generated_values = []

        csv_file_name = f"{self.folder_path}/{self.top_function}_{part}.csv"

        for i in range(number_of_samples):
            
            param_values = generate_code(self.folder_path, generated_values, self.params, self.top_function, self.func_args, self.template_args)

            if simulate_with_testbench:

                run_csim(self.folder_path)
                tb_output = get_testbench_output(self.folder_path)
                append_tb_data_to_json(self.folder_path, self.top_function, {"config": param_values, "out": tb_output})

            run_synth(self.folder_path, frequency_MHz, part)

            resource = get_synth_resource_usage(self.folder_path)
            performance = get_synth_performance_estimates(self.folder_path)
            save_dict_to_csv(param_values | resource | performance, csv_file_name)

    def get_tb_output(self, top_function_name):

        tb_file = Path(self.folder_path) / f"{top_function_name}_tb_output.json"

        if not Path(tb_file).exists():
            raise Exception(f"Could not find {top_function_name}'s testbench output file.")
        
        with open(tb_file, "r", encoding="utf-8") as f:
            return json.load(f)