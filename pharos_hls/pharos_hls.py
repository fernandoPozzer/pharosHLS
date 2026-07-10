import csv
import os
from tabulate import tabulate
import pandas as pd
import json

import seaborn as sns
import matplotlib.pyplot as plt

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

def save_hyperparam_name_definitions(folder, function_name, hyperparams):

    names_dict = {}

    for name, definition in hyperparams.items():
        names_dict[name] = definition.name

    with open(f"{folder}/{function_name}_name_definitions.json", "w", encoding="utf-8") as json_file:
        json.dump(names_dict, json_file, ensure_ascii=False, indent=4)

def get_hyperparam_name_definitions(folder, function_name):

    with open(f"{folder}/{function_name}_name_definitions.json", "r", encoding="utf-8") as json_file:
        hyperparams_names = json.load(json_file)
    
    return hyperparams_names

def get_metric_names(folder):

    with open(f"{folder}/metric_names.json", "r", encoding="utf-8") as json_file:
        metric_names = json.load(json_file)
    
    return metric_names

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

    def get_testbench_results(self, function_name):

        tb_file = Path(self.folder_path) / f"{function_name}_tb_output.json"

        if not Path(tb_file).exists():
            raise Exception(f"Could not find {function_name}'s testbench output file.")
        
        with open(tb_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def get_synth_results(self, function_name, part, remove_const_cols = True):

        csv_file = Path(self.folder_path) / "data" / f"{function_name}_{part}.csv"

        if not Path(csv_file).exists():
            raise Exception(f"Could not find {function_name}'s synthesis .csv file.")
        
        df =  pd.read_csv(csv_file)

        if remove_const_cols:
            for col in df.columns:
                if df[col].nunique(dropna=False) == 1:
                    df = df.drop(columns=[col])
        
        return df
        
    def print_synth_results(self, function_name, part, remove_const_cols = True):
        
        df = self.get_synth_results(function_name, part, remove_const_cols)
        print(tabulate(df, headers="keys", tablefmt="grid", showindex=False, floatfmt=".0f"))

    def define_metric_names(self, metric_names: dict):

        with open(f"{self.folder_path}/metric_names.json", "w", encoding="utf-8") as json_file:
            json.dump(metric_names, json_file, ensure_ascii=False, indent=4)

    def get_correlation_matrix(self, function_name, part, method="kendall"):

        hyperparams_count = len(get_hyperparam_name_definitions(self.folder_path, function_name))
        df = self.get_synth_results(function_name, part, remove_const_cols=True)

        cols_X = df.columns[:hyperparams_count]
        cols_Y = df.columns[hyperparams_count:]
        
        correlations = pd.DataFrame(index=cols_X, columns=cols_Y)

        for col_x in cols_X:
            for col_y in cols_Y:
                correlations.loc[col_x, col_y] = round(df[col_x].corr(df[col_y], method=method), 2)

        return correlations
    
    def generate_correlations_chart(self, function_name: str, part: str, chart_name: str, method="kendall"):

        corr = self.get_correlation_matrix(function_name, part, method)

        hyperparam_names = get_hyperparam_name_definitions(self.folder_path, function_name)
        metric_names = get_metric_names(self.folder_path)

        corr.index = get_correspondent_names(corr.index, hyperparam_names)
        corr.columns = get_correspondent_names(corr.columns, metric_names)

        ax = sns.heatmap(
            corr.astype(float),
            annot=True,
            cmap="coolwarm",
        )

        ax.set_xticklabels(
            ax.get_xticklabels(),
            rotation=45,
            ha="right"
        )

        create_charts_folder(self.folder_path)

        plt.savefig(f"{self.folder_path}/charts/{chart_name}", bbox_inches="tight")
        plt.show()

def create_charts_folder(folder_name):

    path = f"{folder_name}/charts"

    if not os.path.exists(path):
        os.makedirs(path)

def get_correspondent_names(list_of_names, dictionary: dict):

    new_names = []

    for name in list_of_names:
        new_names.append(dictionary.get(name, name))

    return new_names
