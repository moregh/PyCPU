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
    

# A Register Conditional Loads
class CAZ(BaseInstruction):
    """
    Conditional Load A if Zero - Load A with immediate value if Zero flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['Z']:
            reg['A'] = data[0]
        return reg, BLANK_FLAGS


class NAZ(BaseInstruction):
    """
    Conditional Load A if Not Zero - Load A with immediate value if Zero flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['Z']:
            reg['A'] = data[0]
        return reg, BLANK_FLAGS


class CAO(BaseInstruction):
    """
    Conditional Load A if Overflow - Load A with immediate value if Overflow flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['O']:
            reg['A'] = data[0]
        return reg, BLANK_FLAGS


class NAO(BaseInstruction):
    """
    Conditional Load A if Not Overflow - Load A with immediate value if Overflow flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['O']:
            reg['A'] = data[0]
        return reg, BLANK_FLAGS


class CAN(BaseInstruction):
    """
    Conditional Load A if Negative - Load A with immediate value if Negative flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['N']:
            reg['A'] = data[0]
        return reg, BLANK_FLAGS


class NAN(BaseInstruction):
    """
    Conditional Load A if Not Negative - Load A with immediate value if Negative flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['N']:
            reg['A'] = data[0]
        return reg, BLANK_FLAGS


# X Register Conditional Loads
class CXZ(BaseInstruction):
    """
    Conditional Load X if Zero - Load X with immediate value if Zero flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['Z']:
            reg['X'] = data[0]
        return reg, BLANK_FLAGS


class NXZ(BaseInstruction):
    """
    Conditional Load X if Not Zero - Load X with immediate value if Zero flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['Z']:
            reg['X'] = data[0]
        return reg, BLANK_FLAGS


class CXO(BaseInstruction):
    """
    Conditional Load X if Overflow - Load X with immediate value if Overflow flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['O']:
            reg['X'] = data[0]
        return reg, BLANK_FLAGS


class NXO(BaseInstruction):
    """
    Conditional Load X if Not Overflow - Load X with immediate value if Overflow flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['O']:
            reg['X'] = data[0]
        return reg, BLANK_FLAGS


class CXN(BaseInstruction):
    """
    Conditional Load X if Negative - Load X with immediate value if Negative flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['N']:
            reg['X'] = data[0]
        return reg, BLANK_FLAGS


class NXN(BaseInstruction):
    """
    Conditional Load X if Not Negative - Load X with immediate value if Negative flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['N']:
            reg['X'] = data[0]
        return reg, BLANK_FLAGS


# Y Register Conditional Loads
class CYZ(BaseInstruction):
    """
    Conditional Load Y if Zero - Load Y with immediate value if Zero flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['Z']:
            reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class NYZ(BaseInstruction):
    """
    Conditional Load Y if Not Zero - Load Y with immediate value if Zero flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['Z']:
            reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class CYO(BaseInstruction):
    """
    Conditional Load Y if Overflow - Load Y with immediate value if Overflow flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['O']:
            reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class NYO(BaseInstruction):
    """
    Conditional Load Y if Not Overflow - Load Y with immediate value if Overflow flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['O']:
            reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class CYN(BaseInstruction):
    """
    Conditional Load Y if Negative - Load Y with immediate value if Negative flag is set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if flags['N']:
            reg['Y'] = data[0]
        return reg, BLANK_FLAGS


class NYN(BaseInstruction):
    """
    Conditional Load Y if Not Negative - Load Y with immediate value if Negative flag is not set
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        if not flags['N']:
            reg['Y'] = data[0]
        return reg, BLANK_FLAGS