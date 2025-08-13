# Python Software CPU
A simple software CPU written in Python 3, designed to be easy to
understand and modify.

### About

The CPU is 8-bits and uses 16-bit addressing. The following features are available:

- 3 general purpose registers
- Up to 64KiB RAM
- Customisable instruction set
- Status flags

The software is designed to be easily understood and modifiable.

## Quick Start

Simply import the CPU, write some code and get to work!

```python
from cpu import CPU


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
```
**Output:**
```commandline
Ticks: 3 Registers: {'A': 250, 'X': 150, 'Y': 0, 'PC': 5} Flags: {'Z': False, 'O': False, 'H': False, 'N': False}
```

### Example

This will demonstrate how to use the *examples/fibonacci.cpu* program with the CPU.

```python
from cpu import CPU
from compiler import parse_file


# Create a new CPU instance with 256 bytes of RAM
cpu = CPU(ram_size=256) 

# Load the fibonacci.py file into the CPU
cpu.load_data(parse_file("examples/fibonacci.cpu"))

# Run the code until the CPU halts
while not cpu.halted:
    cpu.tick()
    
# Print the current CPU status.
print(cpu)
```

**Output:**
```commandline
Ticks: 94 Registers: {'A': 121, 'X': 1, 'Y': 1, 'PC': 24} Flags: {'Z': False, 'O': False, 'H': True, 'N': False}
```

## CPU Architecture

### Registers

The CPU has three 8-bit general purpose registers, *A*, *X* and *Y*, and a 16-bit program 
counter *PC*. These are stored within a dictionary in the CPU called *REG*.

### Status Flags

The CPU has status flags referring to the state of the CPU following the previous instruction.
These are:
- **O**verflow - set True when the result of the operation was larger than 8-bits (255)
- **Z**ero - set True when the result of the operation was zero
- **N**egative - set True when the result of the operation was a negative number
- **H**alt - set True by the HLT instruction

Overflowing or negative numbers will be wrapped around.

## Instructions

Please see <a href="docs/Instructions.md">INSTRUCTIONS.md</a> for further details.
