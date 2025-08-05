import inspect
import sys
from .base import BaseInstruction

# Import all instruction modules to register their classes
from . import control
from . import load_store
from . import memory
from . import arithmetic
from . import bitwise
from . import comparison

# Build the instruction mappings
InstructionSet: dict[int, type] = {}
NameToOpcode: dict[str, int] = {}
OpcodeToName: dict[int, str] = {}

# Collect all instruction classes from all modules
def _collect_instructions():
    instruction_modules = [control, load_store, memory, arithmetic, bitwise, comparison]
    
    for module in instruction_modules:
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if (hasattr(cls, "opcode") and 
                cls.opcode > -1 and 
                issubclass(cls, BaseInstruction) and 
                cls != BaseInstruction):
                
                if cls.opcode in InstructionSet:
                    raise ValueError(f"Duplicate opcode {cls.opcode} for classes {InstructionSet[cls.opcode].__name__} and {name}")
                
                InstructionSet[cls.opcode] = cls
                NameToOpcode[name] = cls.opcode
                OpcodeToName[cls.opcode] = name

# Initialize the mappings
_collect_instructions()

# Create the instruction list for quick lookup
InstructionList: list[type] = [InstructionSet.get(i, InstructionSet[0]) for i in range(256)]

# Export the key components
__all__ = ['BaseInstruction', 'InstructionSet', 'NameToOpcode', 'OpcodeToName', 'InstructionList']