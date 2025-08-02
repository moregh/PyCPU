from utils import set_flags, data_to_memory_location, BLANK_FLAGS, HALT_FLAGS
from abc import ABC, abstractmethod
import inspect
import sys
from typ import Flags, Registers, Data


BYTE_SIZE = 256
IOTA = 0


def iota() -> int:
    global IOTA
    IOTA += 1
    return IOTA - 1


def validate(value: int) -> tuple[int, Flags]:
    flags = set_flags(value)
    return value & (BYTE_SIZE - 1), flags


class BaseInstruction(ABC):
    """Base Instruction

    opcode: int -- the unique opcode for this instruction, range: 0-255
    length: int -- the number of bytes of data the instruction requires to operate, range: 0-255
    """
    opcode: int = -1
    length: int = -1

    @staticmethod
    @abstractmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        pass


class HLT(BaseInstruction):
    """
    Halt - stops the processor
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        return reg, HALT_FLAGS


class CLR(BaseInstruction):
    """
    Clear - resets A, X and Y registers to 0
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['X'] = reg['Y'] = 0
        return reg, BLANK_FLAGS


class NOP(BaseInstruction):
    """
    No Operation - does nothing but increase the tick counter
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        return reg, BLANK_FLAGS


class LDA(BaseInstruction):
    """
    Load A - loads A register with a specified value
    """
    opcode: int = iota()
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = data[0]
        return reg, BLANK_FLAGS


class LDX(BaseInstruction):
    """
    Load X - loads X register with a specified value
    """
    opcode: int = iota()
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = data[0]
        return reg, BLANK_FLAGS


class LDY(BaseInstruction):
    """
    Load Y - loads Y register with a specified value
    """
    opcode: int = iota()
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class WMA(BaseInstruction):
    """
    Write Memory A - writes the value of register A to specified memory location
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        ram[location] = reg['A']
        return reg, BLANK_FLAGS


class WMX(BaseInstruction):
    """
    Write Memory X - writes the value of register X to specified memory location
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        ram[location] = reg['X']
        return reg, BLANK_FLAGS


class WMY(BaseInstruction):
    """
    Write Memory Y - writes the value of register Y to specified memory location
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        ram[location] = reg['Y']
        return reg, BLANK_FLAGS


class RMA(BaseInstruction):
    """
    Read Memory A - reads the value of specified memory location to register A
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        reg['A'] = ram[location]
        return reg, BLANK_FLAGS


class RMX(BaseInstruction):
    """
    Read Memory X - reads the value of specified memory location to register X
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        reg['X'] = ram[location]
        return reg, BLANK_FLAGS


class RMY(BaseInstruction):
    """
    Read Memory Y - reads the value of specified memory location to register Y
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        reg['Y'] = ram[location]
        return reg, BLANK_FLAGS


class AAX(BaseInstruction):
    """
    Add A and X - Adds register A to register X and store the value in register A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] + reg['X'])
        return reg, flags


class AAY(BaseInstruction):
    """
    Add A and Y - Adds register A to register Y and store the value in register A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] + reg['Y'])
        return reg, flags


class AXY(BaseInstruction):
    """
    Add X and Y - Adds register X to register Y and store the value in register X
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] + reg['Y'])
        return reg, flags


class SAX(BaseInstruction):
    """
    Subtract A and X - Subtracts register X from register A and store the value in register A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] - reg['X'])
        return reg, flags


class SAY(BaseInstruction):
    """
    Subtract A and Y - Subtracts register Y from register A and store the value in register A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] - reg['Y'])
        return reg, flags


class SXY(BaseInstruction):
    """
    Subtract X and Y - Subtracts register Y from register X and store the value in register X
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] - reg['Y'])
        return reg, flags


class CAX(BaseInstruction):
    """
    Copy A to X - Copies A register into X register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = reg['A']
        return reg, set_flags(reg['X'])


class CAY(BaseInstruction):
    """
    Copy A to Y - Copies A register into Y register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = reg['A']
        return reg, set_flags(reg['Y'])


class CXY(BaseInstruction):
    """
    Copy X to Y - Copies X register into Y register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = reg['X']
        return reg, set_flags(reg['Y'])


class CYX(BaseInstruction):
    """
    Copy Y to X - Copies Y register into X register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = reg['Y']
        return reg, set_flags(reg['X'])


class CXA(BaseInstruction):
    """
    Copy X to A - Copies X register into A register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['X']
        return reg, set_flags(reg['A'])


class CYA(BaseInstruction):
    """
    Copy Y to A - Copies Y register into A register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['Y']
        return reg, set_flags(reg['A'])


class JMP(BaseInstruction):
    """
    Jump - Jump to specified memory location
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JNZ(BaseInstruction):
    """
    Jump Not Zero - Jump to specified memory location if the Zero flag was not set during the last operation
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['Z']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JMZ(BaseInstruction):
    """
    Jump if Zero - Jump to specified memory location if the Zero flag was set during the last operation
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['Z']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JNN(BaseInstruction):
    """
    Jump Not Negative - Jump to specified memory location if the Negative flag was not set during the last operation
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['N']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JMN(BaseInstruction):
    """
    Jump if Negative - Jump to specified memory location if the Negative flag was set during the last operation
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['N']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JNO(BaseInstruction):
    """
    Jump Not Overflow - Jump to specified memory location if the Overflow flag was not set during the last operation
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['O']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JMO(BaseInstruction):
    """
    Jump if Overflow - Jump to specified memory location if the Overflow flag was set during the last operation
    """
    opcode: int = iota()
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['O']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class INA(BaseInstruction):
    """
    Increment A - Adds 1 to value of A register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] + 1)
        return reg, flags


class INX(BaseInstruction):
    """
    Increment X - Adds 1 to value of X register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] + 1)
        return reg, flags


class INY(BaseInstruction):
    """
    Increment Y - Adds 1 to value of Y register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'], flags = validate(reg['Y'] + 1)
        return reg, flags


class DEA(BaseInstruction):
    """
    Decrement A - Subtracts 1 from value of A register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] - 1)
        return reg, flags


class DEX(BaseInstruction):
    """
    Decrement X - Subtracts 1 from value of X register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] - 1)
        return reg, flags


class DEY(BaseInstruction):
    """
    Decrement Y - Subtracts 1 from value of Y register
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'], flags = validate(reg['Y'] - 1)
        return reg, flags


class EAX(BaseInstruction):
    """
    Equal A and X - Compares A and X for equality and sets Zero flag if true
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if reg['A'] != reg['X']:
            return reg, BLANK_FLAGS
        return reg, set_flags(0)


class EAY(BaseInstruction):
    """
    Equal A and Y - Compares A and Y for equality and sets Zero flag if true
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if reg['A'] != reg['Y']:
            return reg, BLANK_FLAGS
        return reg, set_flags(0)


class EXY(BaseInstruction):
    """
    Equal X and Y - Compares X and Y for equality and sets Zero flag if true
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if reg['X'] != reg['Y']:
            return reg, BLANK_FLAGS
        return reg, set_flags(0)


class NAX(BaseInstruction):
    """
    AND A & X - ANDs A and X and saves the result in A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] &= reg['X']
        return reg, set_flags(reg['A'])


class NAY(BaseInstruction):
    """
    AND A & Y - ANDs A and Y and saves the result in A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] &= reg['Y']
        return reg, set_flags(reg['A'])


class NXY(BaseInstruction):
    """
    AND X & Y - ANDs X and Y and saves the result in X
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] &= reg['Y']
        return reg, set_flags(reg['X'])


class OAX(BaseInstruction):
    """
    OR A & X - ORs A and X and saves the result in A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] |= reg['X']
        return reg, set_flags(reg['A'])


class OAY(BaseInstruction):
    """
    OR A & Y - ORs A and Y and saves the result in A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] |= reg['Y']
        return reg, set_flags(reg['A'])


class OXY(BaseInstruction):
    """
    OR X & Y - ORs X and Y and saves the result in X
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] |= reg['Y']
        return reg, set_flags(reg['X'])


class XAX(BaseInstruction):
    """
    Xor A and X - XORs A and X and saves the result in A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] ^= reg['X']
        return reg, set_flags(reg['A'])


class XAY(BaseInstruction):
    """
    Xor A and Y - XORs A and Y and saves the result in A
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] ^= reg['Y']
        return reg, set_flags(reg['A'])


class XXY(BaseInstruction):
    """
    Xor X and Y - XORs X and Y and saves the result in X
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] ^= reg['Y']
        return reg, set_flags(reg['X'])


class BLA(BaseInstruction):
    """
    Bit Shift Left A - Bit-shift A register left by 1 (double)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] << 1)
        return reg, flags


class BLX(BaseInstruction):
    """
    Bit Shift Left X - Bit-shift X register left by 1 (double)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] << 1)
        return reg, flags


class BLY(BaseInstruction):
    """
    Bit Shift Left Y - Bit-shift Y register left by 1 (double)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'], flags = validate(reg['Y'] << 1)
        return reg, flags


class BRA(BaseInstruction):
    """
    Bit Shift Right A - Bit-shift A register right by 1 (half)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['A'] >> 1
        return reg, set_flags(reg['A'])


class BRX(BaseInstruction):
    """
    Bit Shift Right X - Bit-shift X register right by 1 (half)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = reg['X'] >> 1
        return reg, set_flags(reg['X'])


class BRY(BaseInstruction):
    """
    Bit Shift Right Y - Bit-shift Y register right by 1 (half)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = reg['Y'] >> 1
        return reg, set_flags(reg['Y'])


class JFA(BaseInstruction):
    """
    Jump Forward A - sets PC to its current value plus the value of the A register (wraps around memory)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] + reg['A']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JFX(BaseInstruction):
    """
    Jump Forward X - sets PC to its current value plus the value of the X register (wraps around memory)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] + reg['X']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JFY(BaseInstruction):
    """
    Jump Forward Y - sets PC to its current value plus the value of the Y register (wraps around memory)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] + reg['Y']) & (len(ram) - 1)
        return reg, BLANK_FLAGS
    

class JBA(BaseInstruction):
    """
    Jump Backward A - sets PC to its current value minus the value of the A register (wraps around memory)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] - reg['A']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JBX(BaseInstruction):
    """
    Jump Backward X - sets PC to its current value minus the value of the X register (wraps around memory)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] - reg['X']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JBY(BaseInstruction):
    """
    Jump Backward Y - sets PC to its current value minus the value of the Y register (wraps around memory)
    """
    opcode: int = iota()
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] - reg['Y']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


"""
***********************************************************************************************************************
* * * * * * * * * * * * * * * * * * * * * * * * * * * * WARNING * * * * * * * * * * * * * * * * * * * * * * * * * * * *
***********************************************************************************************************************
 
These dictionary definitions MUST appear at the bottom of the file to ensure that all the instructions are imported.
If you use the same opcode for multiple instructions, undefined behaviour may occur. It is recommended you use iota()
to ensure an unused, sequential int is assigned to the opcode.
"""
InstructionSet: dict[int, type] = {}
NameToOpcode: dict[str, int] = {}
OpcodeToName: dict[int, str] = {}

for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    if hasattr(cls, "opcode") and cls.opcode > -1:
        InstructionSet[cls.opcode] = cls
        NameToOpcode[name] = cls.opcode
        OpcodeToName[cls.opcode] = name