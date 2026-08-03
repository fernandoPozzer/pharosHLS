from enum import Enum

class Regression(Enum):

    LINEAR = lambda x, a, b: a * x + b
    QUADRATIC = lambda x, a, b, c: a * x * x + b * x + c
    INV_SQUARE = lambda x, a: a / (x * x)

class Metric(Enum):

    DSP = "DSP"
    BRAM = "BRAM_18K"
    FF = "FF"
    LUT = "LUT"
    AVG_TOTAL_CYCLES = "avg_total_cycles"
    EST_CLOCK_PERIOD = "estimated_clock_period"