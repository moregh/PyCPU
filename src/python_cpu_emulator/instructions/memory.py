from .base import BaseInstruction, BLANK_FLAGS, ZERO_FLAGS, set_flags, data_to_memory_location
from ..types import Flags, Registers, Data


class WMA(BaseInstruction):
    """
    Write Memory A - writes the value of register A to specified memory location
    """
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
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = data_to_memory_location(data) & (len(ram) - 1)
        reg['Y'] = ram[location]
        return reg, BLANK_FLAGS


class RMI(BaseInstruction):
    """
    Read Memory Indexed - reads memory[X + Y*256] into A register
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = (reg['Y'] * 256 + reg['X']) & (len(ram) - 1)
        reg['A'] = ram[location]
        return reg, set_flags(reg['A'])


class WMI(BaseInstruction):
    """
    Write Memory Indexed - writes A register to memory[X + Y*256]
    """
    length: int = 0

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        location = (reg['Y'] * 256 + reg['X']) & (len(ram) - 1)
        ram[location] = reg['A']
        return reg, BLANK_FLAGS


class RMO(BaseInstruction):
    """
    Read Memory Offset - reads memory[base_addr + X] into A register, base_addr is provided as 2-byte parameter
    """
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        base_addr = data_to_memory_location(data)
        location = (base_addr + reg['X']) & (len(ram) - 1)
        reg['A'] = ram[location]
        return reg, set_flags(reg['A'])


class WMO(BaseInstruction):
    """
    Write Memory Offset - writes A register to memory[base_addr + X], base_addr is provided as 2-byte parameter
    """
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        base_addr = data_to_memory_location(data)
        location = (base_addr + reg['X']) & (len(ram) - 1)
        ram[location] = reg['A']
        return reg, BLANK_FLAGS
    

class FIL(BaseInstruction):
    """
    Fill - Fill A bytes starting at (X,Y) with value from parameter
    """
    length: int = 1

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        start_location = (reg['Y'] * 256 + reg['X']) & (len(ram) - 1)
        fill_value = data[0]
        count = reg['A']
        
        for i in range(count):
            location = (start_location + i) & (len(ram) - 1)
            ram[location] = fill_value
            
        return reg, BLANK_FLAGS
    

class CMP(BaseInstruction):
    """
    Compare Memory - Compare A bytes at (X,Y) with bytes at specified address, set Z flag if equal
    """
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        source_location = (reg['Y'] * 256 + reg['X']) & (len(ram) - 1)
        compare_location = data_to_memory_location(data) & (len(ram) - 1)
        count = reg['A']
        
        for i in range(count):
            source_addr = (source_location + i) & (len(ram) - 1)
            compare_addr = (compare_location + i) & (len(ram) - 1)
            
            if ram[source_addr] != ram[compare_addr]:
                return reg, BLANK_FLAGS  # Not equal, Z flag remains false
        
        # All bytes matched
        return reg, ZERO_FLAGS  # Set Z flag to indicate equality


class CPY(BaseInstruction):
    """
    Copy Memory - Copy A bytes from source (X,Y) to destination address
    """
    length: int = 2

    @staticmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        source_location = (reg['Y'] * 256 + reg['X']) & (len(ram) - 1)
        dest_location = data_to_memory_location(data) & (len(ram) - 1)
        count = reg['A']
        
        for i in range(count):
            source_addr = (source_location + i) & (len(ram) - 1)
            dest_addr = (dest_location + i) & (len(ram) - 1)
            ram[dest_addr] = ram[source_addr]
        
        return reg, BLANK_FLAGS