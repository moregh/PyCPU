from .base import BaseInstruction, validate
from ..types import Flags, Registers, Data


class AAX(BaseInstruction):
    """
    Add A and X - Adds register A to register X and store the value in register A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] + reg['X'])
        return reg, flags


class AAY(BaseInstruction):
    """
    Add A and Y - Adds register A to register Y and store the value in register A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] + reg['Y'])
        return reg, flags


class AXY(BaseInstruction):
    """
    Add X and Y - Adds register X to register Y and store the value in register X
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] + reg['Y'])
        return reg, flags


class SAX(BaseInstruction):
    """
    Subtract A and X - Subtracts register X from register A and store the value in register A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] - reg['X'])
        return reg, flags


class SAY(BaseInstruction):
    """
    Subtract A and Y - Subtracts register Y from register A and store the value in register A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] - reg['Y'])
        return reg, flags


class SXY(BaseInstruction):
    """
    Subtract X and Y - Subtracts register Y from register X and store the value in register X
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] - reg['Y'])
        return reg, flags


class INA(BaseInstruction):
    """
    Increment A - Adds 1 to value of A register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] + 1)
        return reg, flags


class INX(BaseInstruction):
    """
    Increment X - Adds 1 to value of X register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] + 1)
        return reg, flags


class INY(BaseInstruction):
    """
    Increment Y - Adds 1 to value of Y register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'], flags = validate(reg['Y'] + 1)
        return reg, flags


class DEA(BaseInstruction):
    """
    Decrement A - Subtracts 1 from value of A register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] - 1)
        return reg, flags


class DEX(BaseInstruction):
    """
    Decrement X - Subtracts 1 from value of X register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] - 1)
        return reg, flags


class DEY(BaseInstruction):
    """
    Decrement Y - Subtracts 1 from value of Y register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'], flags = validate(reg['Y'] - 1)
        return reg, flags