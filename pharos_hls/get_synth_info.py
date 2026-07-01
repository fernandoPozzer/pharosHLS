from pathlib import Path
import xml.etree.ElementTree as ET

def get_synth_resource_usage(folder_path):

    csynth_file = Path(folder_path) / "vitis_proj" / "sol" / "syn" / "report" / "explore_csynth.xml"

    if not csynth_file.is_file():
        print("ERROR: Synth report file does not exist. Try running 'run_synth' before.")
        return

    tree = ET.parse(csynth_file)
    root = tree.getroot()

    area = root.find("AreaEstimates")
    resources = area.find("Resources")

    resource_usage = {
        "BRAM_18K": int(resources.find("BRAM_18K").text),
        "DSP": int(resources.find("DSP").text),
        "FF": int(resources.find("FF").text),
        "LUT": int(resources.find("LUT").text),
        "URAM": int(resources.find("URAM").text),
    }

    return resource_usage
    
def get_synth_performance_estimates(folder_path):

    csynth_file = Path(folder_path) / "vitis_proj" / "sol" / "syn" / "report" / "explore_csynth.xml"

    if not csynth_file.is_file():
        print("ERROR: Synth report file does not exist. Try running 'run_synth' before.")
        return

    tree = ET.parse(csynth_file)
    root = tree.getroot()
    
    performance = root.find("PerformanceEstimates")

    latency = performance.find("SummaryOfOverallLatency")
    timing = performance.find("SummaryOfTimingAnalysis")

    performance_estimates = {
        "avg_total_cycles": int(latency.find("Average-caseLatency").text),
        "estimated_clock_period" : float(timing.find("EstimatedClockPeriod").text)
    }

    return performance_estimates