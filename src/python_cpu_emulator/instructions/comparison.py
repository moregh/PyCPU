from .base import BaseInstruction, BLANK_FLAGS, set_flags
from ..types import Flags, Registers, Data


class EAX(BaseInstruction):
    """
    Equal A and X - Compares A and X for equality and sets Zero flag if true
    """
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
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if reg['X'] != reg['Y']:
            return reg, BLANK_FLAGS
        return reg, set_flags(0)