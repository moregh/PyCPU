from .base import BaseInstruction, BLANK_FLAGS, HALT_FLAGS, data_to_memory_location
from ..types import Flags, Registers, Data


class HLT(BaseInstruction):
    """
    Halt - stops the processor
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        return reg, HALT_FLAGS


class CLR(BaseInstruction):
    """
    Clear - resets A, X and Y registers to 0
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['X'] = reg['Y'] = 0
        return reg, BLANK_FLAGS


class NOP(BaseInstruction):
    """
    No Operation - does nothing but increase the tick counter
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        return reg, BLANK_FLAGS


class JMP(BaseInstruction):
    """
    Jump - Jump to specified memory location
    """
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JNZ(BaseInstruction):
    """
    Jump Not Zero - Jump to specified memory location if the Zero flag was not set during the last operation
    """
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
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['O']:
            reg['PC'] = data_to_memory_location(data)
        return reg, BLANK_FLAGS


class JFA(BaseInstruction):
    """
    Jump Forward A - sets PC to its current value plus the value of the A register (wraps around memory)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] + reg['A']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JFX(BaseInstruction):
    """
    Jump Forward X - sets PC to its current value plus the value of the X register (wraps around memory)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] + reg['X']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JFY(BaseInstruction):
    """
    Jump Forward Y - sets PC to its current value plus the value of the Y register (wraps around memory)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] + reg['Y']) & (len(ram) - 1)
        return reg, BLANK_FLAGS
    

class JBA(BaseInstruction):
    """
    Jump Backward A - sets PC to its current value minus the value of the A register (wraps around memory)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] - reg['A']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JBX(BaseInstruction):
    """
    Jump Backward X - sets PC to its current value minus the value of the X register (wraps around memory)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] - reg['X']) & (len(ram) - 1)
        return reg, BLANK_FLAGS


class JBY(BaseInstruction):
    """
    Jump Backward Y - sets PC to its current value minus the value of the Y register (wraps around memory)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['PC'] = (reg['PC'] - reg['Y']) & (len(ram) - 1)
        return reg, BLANK_FLAGS