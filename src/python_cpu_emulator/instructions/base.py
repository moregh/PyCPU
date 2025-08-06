from abc import ABC, abstractmethod
from ..utils import set_flags, data_to_memory_location, BLANK_FLAGS, HALT_FLAGS, ZERO_FLAGS
from ..types import Flags, Registers, Data


BYTE_SIZE = 256


def validate(value: int) -> tuple[int, Flags]:
    flags = set_flags(value)
    return value & (BYTE_SIZE - 1), flags


class OpcodeManager:
    """Manages opcode assignment with reserved opcodes and automatic assignment"""
    def __init__(self):
        self.reserved = {}  # opcode -> class_name mapping for reserved opcodes
        self.used_opcodes = set()
        self.next_auto = 0
    
    def reserve(self, opcode: int, class_name: str):
        """Reserve a specific opcode for a class"""
        if opcode in self.used_opcodes:
            raise ValueError(f"Opcode {opcode} already used")
        self.reserved[opcode] = class_name
        self.used_opcodes.add(opcode)
        
    def get_opcode(self, class_name: str) -> int:
        """Get opcode for a class - either reserved or auto-assigned"""
        # Check if this class has a reserved opcode
        for opcode, name in self.reserved.items():
            if name == class_name:
                return opcode
        
        # Auto-assign next available opcode
        while self.next_auto in self.used_opcodes:
            self.next_auto += 1
        
        opcode = self.next_auto
        self.used_opcodes.add(opcode)
        self.next_auto += 1
        return opcode


# Global opcode manager instance
_opcode_manager = OpcodeManager()

# Reserve specific opcodes
_opcode_manager.reserve(0, 'HLT')
_opcode_manager.reserve(1, 'CLR') 
_opcode_manager.reserve(2, 'NOP')


def get_opcode(class_name: str) -> int:
    """Get an opcode for the given class name"""
    return _opcode_manager.get_opcode(class_name)


class BaseInstruction(ABC):
    """Base Instruction

    opcode: int -- the unique opcode for this instruction, range: 0-255
    length: int -- the number of bytes of data the instruction requires to operate, range: 0-255
    """
    opcode: int = -1
    length: int = -1

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in ['BaseInstruction']:
            cls.opcode = get_opcode(cls.__name__)

    @staticmethod
    @abstractmethod
    def run(reg: Registers, flags: Flags, data: Data, ram: Data) -> tuple[Registers, Flags]:
        pass