import inspect
import importlib
import pkgutil
from .base import BaseInstruction

# Build the instruction mappings
InstructionSet: dict[int, type] = {}
NameToOpcode: dict[str, int] = {}
OpcodeToName: dict[int, str] = {}

def _collect_instructions():
    """Automatically discover and import all instruction modules in this package"""
    
    # Get the current package path
    package_path = __path__[0]  # type: ignore
    package_name = __name__
    
    # Discover all modules in the instructions package
    for importer, modname, ispkg in pkgutil.iter_modules([package_path]):
        # Skip the base module as it doesn't contain instruction classes
        if modname == 'base':
            continue
            
        # Import the module dynamically
        full_module_name = f"{package_name}.{modname}"
        try:
            module = importlib.import_module(full_module_name)
            
            # Scan the module for instruction classes
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
                    
        except ImportError as e:
            print(f"Warning: Could not import instruction module {full_module_name}: {e}")

# Initialize the mappings
_collect_instructions()

# Create the instruction list for quick lookup
InstructionList: list[type] = [InstructionSet.get(i, InstructionSet[0]) for i in range(256)]

# Export the key components
__all__ = ['BaseInstruction', 'InstructionSet', 'NameToOpcode', 'OpcodeToName', 'InstructionList']