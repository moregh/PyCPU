from .base import BaseInstruction, validate, set_flags
from ..types import Flags, Registers, Data


class NAX(BaseInstruction):
    """
    AND A & X - ANDs A and X and saves the result in A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] &= reg['X']
        return reg, set_flags(reg['A'])


class NAY(BaseInstruction):
    """
    AND A & Y - ANDs A and Y and saves the result in A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] &= reg['Y']
        return reg, set_flags(reg['A'])


class NXY(BaseInstruction):
    """
    AND X & Y - ANDs X and Y and saves the result in X
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] &= reg['Y']
        return reg, set_flags(reg['X'])


class OAX(BaseInstruction):
    """
    OR A & X - ORs A and X and saves the result in A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] |= reg['X']
        return reg, set_flags(reg['A'])


class OAY(BaseInstruction):
    """
    OR A & Y - ORs A and Y and saves the result in A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] |= reg['Y']
        return reg, set_flags(reg['A'])


class OXY(BaseInstruction):
    """
    OR X & Y - ORs X and Y and saves the result in X
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] |= reg['Y']
        return reg, set_flags(reg['X'])


class XAX(BaseInstruction):
    """
    Xor A and X - XORs A and X and saves the result in A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] ^= reg['X']
        return reg, set_flags(reg['A'])


class XAY(BaseInstruction):
    """
    Xor A and Y - XORs A and Y and saves the result in A
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] ^= reg['Y']
        return reg, set_flags(reg['A'])


class XXY(BaseInstruction):
    """
    Xor X and Y - XORs X and Y and saves the result in X
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] ^= reg['Y']
        return reg, set_flags(reg['X'])


class BLA(BaseInstruction):
    """
    Bit Shift Left A - Bit-shift A register left by 1 (double)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'], flags = validate(reg['A'] << 1)
        return reg, flags


class BLX(BaseInstruction):
    """
    Bit Shift Left X - Bit-shift X register left by 1 (double)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'], flags = validate(reg['X'] << 1)
        return reg, flags


class BLY(BaseInstruction):
    """
    Bit Shift Left Y - Bit-shift Y register left by 1 (double)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'], flags = validate(reg['Y'] << 1)
        return reg, flags


class BRA(BaseInstruction):
    """
    Bit Shift Right A - Bit-shift A register right by 1 (half)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['A'] = reg['A'] >> 1
        return reg, set_flags(reg['A'])


class BRX(BaseInstruction):
    """
    Bit Shift Right X - Bit-shift X register right by 1 (half)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['X'] = reg['X'] >> 1
        return reg, set_flags(reg['X'])


class BRY(BaseInstruction):
    """
    Bit Shift Right Y - Bit-shift Y register right by 1 (half)
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        reg['Y'] = reg['Y'] >> 1
        return reg, set_flags(reg['Y'])