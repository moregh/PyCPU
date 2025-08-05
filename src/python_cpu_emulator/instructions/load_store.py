from .base import BaseInstruction, BLANK_FLAGS, set_flags
from ..types import Flags, Registers, Data


class LDA(BaseInstruction):
    """
    Load A - loads A register with a specified value
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = data[0]
        return reg, BLANK_FLAGS


class LDX(BaseInstruction):
    """
    Load X - loads X register with a specified value
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = data[0]
        return reg, BLANK_FLAGS


class LDY(BaseInstruction):
    """
    Load Y - loads Y register with a specified value
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class CAX(BaseInstruction):
    """
    Copy A to X - Copies A register into X register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = reg['A']
        return reg, set_flags(reg['X'])


class CAY(BaseInstruction):
    """
    Copy A to Y - Copies A register into Y register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = reg['A']
        return reg, set_flags(reg['Y'])


class CXY(BaseInstruction):
    """
    Copy X to Y - Copies X register into Y register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = reg['X']
        return reg, set_flags(reg['Y'])


class CYX(BaseInstruction):
    """
    Copy Y to X - Copies Y register into X register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = reg['Y']
        return reg, set_flags(reg['X'])


class CXA(BaseInstruction):
    """
    Copy X to A - Copies X register into A register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['X']
        return reg, set_flags(reg['A'])


class CYA(BaseInstruction):
    """
    Copy Y to A - Copies Y register into A register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['Y']
        return reg, set_flags(reg['A'])