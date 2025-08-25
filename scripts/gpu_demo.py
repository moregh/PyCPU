#!/usr/bin/env python3
import sys
sys.path.append('../src')
from python_cpu_emulator.cpu import CPU
from python_cpu_emulator.compiler import compile
from python_cpu_emulator.display import Display


if __name__ == "__main__":
    cpu = CPU(gpu=Display())       # Makes a new CPU, with the default RAM value of 64KiB
    cpu.load_data(compile("../examples/intermediate/pattern.cpu"))
    cpu.run(report_interval=1000)
    # This will finish after 38,052 ticks
