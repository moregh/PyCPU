# Instructions

This is a list of all the pre-defined instructions available on the CPU.

- Name - the mnemonic name for the instruction
- Opcode - unique, non-negative integer value between 0-255 for this instruction
- Length - the non-negative number of bytes of data upon which the instruction operates
- Description - describes the instructions operation
- Flags - which flags may be affected by the operation
    - **Z**ero - set if result of operation is 0
    - **N**egative - set if result of operation is negative
    - **O**verflow - set if result of operation is greater than 255
    - **H**alt - set if the HLT instruction is run

## Instruction Table

| Name | Opcode | Length | Description                                                                                                      | Flags |
|------|--------|--------|------------------------------------------------------------------------------------------------------------------|-------|
| NOP  | 0      | 0      | No Operation - does nothing but increase the tick counter                                                        | -     |
|      |        |        | **Load Registers**                                                                                               |       |
| LDA  | 1      | 1      | Load A - loads A register with a specified value                                                                 | -     |
| LDX  | 2      | 1      | Load X - loads X register with a specified value                                                                 | -     |
| LDY  | 3      | 1      | Load Y - loads Y register with a specified value                                                                 | -     |
|      |        |        | **Write Memory**                                                                                                 |       |
| WMA  | 4      | 2      | Write Memory A - writes the value of register A to specified memory location                                     | -     |
| WMX  | 5      | 2      | Write Memory X - writes the value of register X to specified memory location                                     | -     |
| WMY  | 6      | 2      | Write Memory Y - writes the value of register Y to specified memory location                                     | -     |
|      |        |        | **Read Memory**                                                                                                  |       |
| RMA  | 7      | 2      | Read Memory A - reads the value of specified memory location to register A                                       | -     |
| RMX  | 8      | 2      | Read Memory X - reads the value of specified memory location to register X                                       | -     |
| RMY  | 9      | 2      | Read Memory Y - reads the value of specified memory location to register Y                                       | -     |
|      |        |        | **Add Registers**                                                                                                |       |
| AAX  | 10     | 0      | Add A and X - Adds register A to register X and store the value in register A                                    | O, Z  |
| AAY  | 11     | 0      | Add A and Y - Adds register A to register Y and store the value in register A                                    | O, Z  |
| AXY  | 12     | 0      | Add X and Y - Adds register X to register Y and store the value in register X                                    | O, Z  |
|      |        |        | **Subtract Registers**                                                                                           |       |
| SAX  | 13     | 0      | Subtract A and X - Subtracts register X from register A and store the value in register A                        | N, Z  |
| SAY  | 14     | 0      | Subtract A and Y - Subtracts register Y from register A and store the value in register A                        | N, Z  |
| SXY  | 15     | 0      | Subtract X and Y - Subtracts register Y from register X and store the value in register X                        | N, Z  |
|      |        |        | **Copy Instructions**                                                                                            |       |
| CAX  | 16     | 0      | Copy A to X - Copies A register into X register                                                                  | Z     |
| CAY  | 17     | 0      | Copy A to Y - Copies A register into Y register                                                                  | Z     |
| CXY  | 18     | 0      | Copy X to Y - Copies X register into Y register                                                                  | Z     |
| CYX  | 19     | 0      | Copy Y to X - Copies Y register into X register                                                                  | Z     |
| CXA  | 20     | 0      | Copy X to A - Copies X register into A register                                                                  | Z     |
| CYA  | 21     | 0      | Copy Y to A - Copies Y register into A register                                                                  | Z     |
|      |        |        | **Jump Instructions**                                                                                            |       |
| JMP  | 22     | 2      | Jump - Jump to specified memory location                                                                         | -     |
| JNZ  | 23     | 2      | Jump Not Zero - Jump to specified memory location if the Zero flag was not set during the last operation         | -     |
| JMZ  | 24     | 2      | Jump if Zero - Jump to specified memory location if the Zero flag was set during the last operation              | -     |
| JNN  | 25     | 2      | Jump Not Negative - Jump to specified memory location if the Negative flag was not set during the last operation | -     |
| JMN  | 26     | 2      | Jump if Negative - Jump to specified memory location if the Negative flag was set during the last operation      | -     |
| JNO  | 27     | 2      | Jump Not Overflow - Jump to specified memory location if the Overflow flag was not set during the last operation | -     |
| JMO  | 28     | 2      | Jump if Overflow - Jump to specified memory location if the Overflow flag was set during the last operation      | -     |
|      |        |        | **Increment Registers**                                                                                          |       |
| INA  | 29     | 0      | Increment A - Adds 1 to value of A register                                                                      | O, Z  |
| INX  | 30     | 0      | Increment X - Adds 1 to value of X register                                                                      | O, Z  |
| INY  | 31     | 0      | Increment Y - Adds 1 to value of Y register                                                                      | O, Z  |
|      |        |        | **Decrement Registers**                                                                                          |       |
| DEA  | 32     | 0      | Decrement A - Subtracts 1 from value of A register                                                               | N, Z  |
| DEX  | 33     | 0      | Decrement X - Subtracts 1 from value of X register                                                               | N, Z  |
| DEY  | 34     | 0      | Decrement Y - Subtracts 1 from value of Y register                                                               | N, Z  |
|      |        |        | **Equalities**                                                                                                   |       |
| EAX  | 35     | 0      | Equal A and X - Compares A and X for equality and sets Zero flag if true                                         | Z     |
| EAY  | 36     | 0      | Equal A and Y - Compares A and Y for equality and sets Zero flag if true                                         | Z     |
| EXY  | 37     | 0      | Equal X and Y - Compares X and Y for equality and sets Zero flag if true                                         | Z     |
|      |        |        | **Exclusive Or**                                                                                                 |       |
| XAX  | 38     | 0      | Xor A and X - XORs A and X and saves the result in A                                                             | Z     |
| XAY  | 39     | 0      | Xor A and Y - XORs A and Y and saves the result in A                                                             | Z     |
| XXY  | 40     | 0      | Xor X and Y - XORs X and Y and saves the result in X                                                             | Z     |
|      |        |        | **Bit Shifts**                                                                                                   |       |
| BLA  | 41     | 0      | Bit Shift Left A - Bit-shift A register left by 1 (double)                                                       | O, Z  |
| BLX  | 42     | 0      | Bit Shift Left X - Bit-shift X register left by 1 (double)                                                       | O, Z  |
| BLY  | 43     | 0      | Bit Shift Left Y - Bit-shift Y register left by 1 (double)                                                       | O, Z  |
| BRA  | 44     | 0      | Bit Shift Right A - Bit-shift A register right by 1 (half)                                                       | Z     |
| BRX  | 45     | 0      | Bit Shift Right X - Bit-shift X register right by 1 (half)                                                       | Z     |
| BRY  | 46     | 0      | Bit Shift Right Y - Bit-shift Y register right by 1 (half)                                                       | Z     |
|      |        |        | **Special Instructions**                                                                                         |       |
| CLR  | 254    | 0      | Clear - resets A, X and Y registers to 0                                                                         | -     |
| HLT  | 255    | 0      | Halt - stops the processor                                                                                       | H     |

## Add Instructions

New instructions can be added or existing instructions modified by editing the 
*instructions.py* file. All instructions must have a unique opcode (integer from 0-255)
and a length value (integer >= 0) corresponding to the number of bytes of data upon 
which they operate. It is recommended to use the iota() function to generate a unique integer
and avoid undefined behaviour.

The last entry within the file should be the pre-existing **InstructionSet** dictionary.
Placing instructions below this entry will prevent them from being imported and available
to the CPU for execution. If you are having problems getting custom instructions to
execute, this may be the reason why.

### Overview

Create a new class in the *instructions.py* file and inherit from the base class, 
**BaseInstruction**. Give your instruction a unique opcode and specify the number of bytes
of data upon which it operates (if any).

```python
class MyInstruction(BaseInstruction):
    opcode: int = 200
    length: int = 0
```

Now you must override the run() static method to implement your instruction. The method must
return **reg** and **flags** dicts to the CPU.
```python
    @staticmethod
    def run(reg: dict[str: int], flags: dict[str: int], data: list[int], ram: list[int]) -> tuple[dict, dict]:
        # Your code goes here
        return reg, flags
```

Helper functions are available for modifying flags. If you have changed a value of a register,
use the **set_flags(value: int)** method to create a flags register automatically. If you
haven't changed any values, use the **BLANK_FLAGS** predefined dictionary.

### Example

Below is an example of an instruction that adds up the **X** and **Y** registers then stores
the result in the **A** register. We shall name this instruction **ALL**.

Note how we must manually handle any possible overflow of the values.

```python
class ALL(BaseInstruction):
    """
    Add All - Adds the value of registers X and Y to register A
    """
    opcode: int = iota()
    length: int = 0
    
    @staticmethod
    def run(reg: dict[str: int], flags: dict[str: int], data: list[int], ram: list[int]) -> tuple[dict, dict]:
        reg['A'] += reg['X'] + reg['Y']
        flags = set_flags(reg['A'])
        if flags['O']:  # Check to see if we overflowed
            reg['A'] = reg['A'] % 256  # If we did, mod 256 to get a value in range
        return reg, flags
```