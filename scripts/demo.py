#!/usr/bin/env python3
import sys
sys.path.append('../src')
from python_cpu_emulator.cpu import CPU
from python_cpu_emulator.compiler import compile


if __name__ == "__main__":
    cpu = CPU()       # Makes a new CPU, with the default RAM value of 64KiB and no GPU
    cpu.load_data(compile("../examples/basic/counters.cpu"))  # Load an example program
    while not cpu.halted:
        cpu.tick()
        if cpu.TICKS % 1000000 == 0:
            print(cpu)
    print(cpu) 
    # this should finish after 33,686,017 ticks.
