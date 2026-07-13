import subprocess
import os
from pathlib import Path
import json

def get_testbench_output(folder_path):

    output_file_path = Path(folder_path) / "vitis_proj" / "sol" / "csim" / "build" / "output.txt"

    with open(output_file_path, "r", encoding="utf-8") as f:
        output = [float(linha.strip()) for linha in f]
    
    return output

def append_tb_data_to_json(folder_path, top_function_name, config_output_item):

    file_name = Path(folder_path) / f"{top_function_name}_tb_output.json"

    if Path(file_name).exists():

        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(config_output_item)

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_vitis_project(folder_path):

    proj_path = Path(folder_path) / "vitis_proj"

    if os.path.exists(proj_path):
        return
    
    print("Creating Vitis Project...\n")

    subprocess.run(["vitis_hls", "0_create_project.tcl", "vitis_proj"], cwd = folder_path)

def run_csim(folder_path):

    create_vitis_project(folder_path)
    subprocess.run(["vitis_hls", "1_csim.tcl", "vitis_proj", "sol"], cwd = folder_path)

def run_synth(folder_path, frequency_MHz: int, part = "xc7z020clg400-1"):

    clk_period_ns = 1000 / frequency_MHz

    create_vitis_project(folder_path)
    subprocess.run(["vitis_hls", "2_synth.tcl", "vitis_proj", "sol", str(clk_period_ns), part], cwd = folder_path)