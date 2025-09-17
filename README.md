# Python CPU Emulator

A software-based CPU emulator written in Python 3, designed for educational purposes and easy modification. The emulator provides a complete 8-bit processor with comprehensive instruction set and testing framework.

## About

This CPU emulator implements an 8-bit processor with 16-bit addressing capabilities. Key features include:

- 3 general purpose registers (A, X, Y)
- 16-bit program counter (PC)
- Up to 64KB addressable RAM
- Turing-complete instruction set with 80+ instructions
- Status flags (Zero, Overflow, Negative, Halt)
- Optional display output
- Built-in assembler and compiler
- Comprehensive testing framework

The software is designed to be educational, demonstrating CPU architecture concepts while remaining easily modifiable and extensible.

## Quick Start

```python
from python_cpu_emulator import CPU, compile

# Create a CPU instance
cpu = CPU()

# Compile and load assembly code
program = compile("examples/basic/hello.cpu")
cpu.load_data(program)

# Execute until halt
cpu.run()
```

## Example Programs

### Counter Program
```python
from python_cpu_emulator import CPU, compile

# Load the counter example
cpu = CPU()
cpu.load_data(compile("examples/basic/counters.cpu"))
cpu.run()  # Runs for 33,686,017 ticks until overflow
```

### Display Output
```python
from python_cpu_emulator import CPU, compile, Display

# Create CPU with display
cpu = CPU(gpu=Display())
cpu.load_data(compile("examples/intermediate/pattern.cpu"))
cpu.run(report_interval=1000)
```

## CPU Architecture

### Registers
- **A, X, Y**: 8-bit general purpose registers
- **PC**: 16-bit program counter

### Status Flags
- **Z** (Zero): Set when operation result equals zero
- **O** (Overflow): Set when operation result exceeds 8-bit range (>255)
- **N** (Negative): Set when operation result is negative (wrapped to 128-255)
- **H** (Halt): Set by HLT instruction to stop execution

### Memory
- 16-bit address space (64KB maximum)
- Configurable RAM size (4KB to 64KB)
- Memory-mapped GPU support for character display

## Instruction Set

The CPU supports over 80 instructions across multiple categories:

- **Arithmetic**
- **Bitwise**
- **Comparison**
- **Load/Store**
- **Memory**
- **Control**

See the complete instruction reference in the source documentation.

## Assembly Language

The emulator includes an assembler that supports:

- Label-based addressing
- Hexadecimal memory addresses ($FFFF)
- Immediate values and memory operations
- Comments (semicolon prefix)

Example assembly:
```assembly
:START
    LDA 42        ; Load 42 into A register
    LDX 10        ; Load 10 into X register
    AAX           ; Add A and X, store in A
    WMA $0100     ; Write A to memory address $0100
    HLT           ; Halt execution
```

## Testing Framework

The project includes a comprehensive testing system that validates all instructions through actual CPU execution:

```python
from testing import test_instruction
from python_cpu_emulator.instructions.arithmetic import INA

# Test increment instruction
test_instruction(INA, 
                initial={'A': 5}, 
                expected={'A': 6})
```

## Project Structure

```
src/python_cpu_emulator/
├── __init__.py
├── cpu.py              # Main CPU implementation
├── compiler.py         # Assembly compiler
├── display.py          # GPU display support
├── tests.py            # Testing script
├── types.py            # Type definitions
├── utils.py            # Utility functions
└── instructions/       # Instruction implementations
    ├── arithmetic.py
    ├── bitwise.py
    ├── comparison.py
    ├── control.py
    ├── load_store.py
    └── memory.py

examples/
├── basic/              # Simple example programs
└── intermediate/       # More complex examples

scripts/                # Demo scripts
```

## Requirements

- Python 3.8 or higher
- No external dependencies for core functionality

## License

This project is licensed using the [AGPL](LICENSE).