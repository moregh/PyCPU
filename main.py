#!/usr/bin/env python3
from cpu import CPU
from compiler import parse_file


if __name__ == "__main__":
    cpu = CPU()       # Makes a new CPU, with the default RAM value of 64KiB

    cpu.RAM[0] = 3    # LDA has opcode 3, loads 1 byte into the A register
    cpu.RAM[1] = 100  # The value 100 will be loaded in to the A register
    cpu.tick()        # Run the previous instruction (tick 1)

    cpu.RAM[2] = 4    # LDX has opcode 4, loads 1 byte into the X register
    cpu.RAM[3] = 150  # The value 150 will be loaded into the X register
    cpu.tick()        # Run the previous instruction (tick 2)

    cpu.RAM[4] = 12   # AAX has opcode 12, adds the values of A and X and stores them into A
    cpu.tick()        # Run the previous instruction (tick 3)

    print(cpu)        # Print out the status of the CPU, showing 3 ticks and 250 in the A register

    # now open an example program which increments the registers sequentially
    cpu.reset()
    print(cpu)
    cpu.load_data(parse_file("examples/counters.cpu"))
    while not cpu.halted:
        cpu.tick()
        # if cpu.TICKS % 1000000 == 0:
        print(cpu)

