#!/usr/bin/env python3
"""
CPU Instruction Testing Framework

Tests instructions through actual CPU execution with proper handling of PC management,
flag preservation, address encoding, and memory operations.
"""

from typing import Dict, Any, Union, List, Tuple, Callable, Optional
from dataclasses import dataclass, field
import sys
import os

current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..')
sys.path.insert(0, src_dir)
sys.path.insert(0, current_dir)

try:
    from python_cpu_emulator.cpu import CPU
    from python_cpu_emulator.instructions.base import BaseInstruction
    from python_cpu_emulator.instructions import NameToOpcode
    from python_cpu_emulator.types import Flags, Registers, Data
    from python_cpu_emulator.utils import BLANK_FLAGS
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


@dataclass
class TestState:
    """Complete CPU state for testing"""
    registers: Registers = field(default_factory=lambda: {'A': 0, 'X': 0, 'Y': 0, 'PC': 0})
    flags: Flags = field(default_factory=lambda: BLANK_FLAGS.copy())
    ram: Data = field(default_factory=lambda: [0] * 1024)
    data: Data = field(default_factory=list)

    def copy(self) -> 'TestState':
        return TestState(
            registers=self.registers.copy(),
            flags=self.flags.copy(),
            ram=self.ram.copy(),
            data=self.data.copy()
        )


@dataclass
class TestCase:
    """Single test case for an instruction"""
    name: str
    initial: Dict[str, Any] = field(default_factory=dict)
    expected: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


class RAMRange:
    """RAM address range specification"""
    
    def __init__(self, start: int, end: int, value: Optional[Union[int, List[int], Callable[[int], int]]] = None):
        self.start = start
        self.end = end
        self.value = value
        
    def to_dict(self) -> Dict[int, int | None]:
        result = {}
        
        if self.value is None:
            return {addr: None for addr in range(self.start, self.end)}
        elif isinstance(self.value, int):
            return {addr: self.value for addr in range(self.start, self.end)}
        elif isinstance(self.value, list):
            if len(self.value) != (self.end - self.start):
                raise ValueError(f"Value list length {len(self.value)} doesn't match range size {self.end - self.start}")
            return {addr: val for addr, val in zip(range(self.start, self.end), self.value)}
        elif callable(self.value):
            return {addr: self.value(addr) for addr in range(self.start, self.end)}
        else:
            raise ValueError(f"Unsupported value type: {type(self.value)}")


class RAMPattern:
    """Pattern-based RAM verification"""
    
    def __init__(self, addresses: Union[List[int], RAMRange], pattern_check: Callable[[List[int]], bool], description: str = ""):
        if isinstance(addresses, RAMRange):
            self.addresses = list(range(addresses.start, addresses.end))
        else:
            self.addresses = addresses
        self.pattern_check = pattern_check
        self.description = description
    
    def check_pattern(self, ram: Data) -> bool:
        values = [ram[addr] for addr in self.addresses if addr < len(ram)]
        return self.pattern_check(values)


def ram_range(start: int, end: int, value: Optional[Union[int, List[int], Callable[[int], int]]] = None) -> RAMRange:
    return RAMRange(start, end, value)


def ram_pattern(addresses: Union[List[int], RAMRange], pattern_check: Callable[[List[int]], bool], description: str = "") -> RAMPattern:
    return RAMPattern(addresses, pattern_check, description)


def create_cpu_state(**kwargs) -> TestState:
    """Create test state with specified values"""
    state = TestState()
    
    if 'registers' in kwargs:
        state.registers.update(kwargs.pop('registers'))
    if 'flags' in kwargs:
        state.flags.update(kwargs.pop('flags'))
    if 'ram' in kwargs:
        ram_data = kwargs.pop('ram')
        if isinstance(ram_data, RAMRange):
            range_dict = ram_data.to_dict()
            for addr, value in range_dict.items():
                if addr < len(state.ram) and value is not None:
                    state.ram[addr] = value
        elif isinstance(ram_data, list):
            if len(ram_data) > len(state.ram):
                state.ram = ram_data.copy()
            else:
                state.ram[:len(ram_data)] = ram_data
        elif isinstance(ram_data, dict):
            for addr, value in ram_data.items():
                if addr < len(state.ram):
                    state.ram[addr] = value
    if 'data' in kwargs:
        state.data = kwargs.pop('data').copy()
    
    for reg in ['A', 'X', 'Y', 'PC']:
        if reg in kwargs:
            state.registers[reg] = kwargs.pop(reg)
    
    for flag in ['Z', 'O', 'H', 'N']:
        if flag in kwargs:
            state.flags[flag] = kwargs.pop(flag)
    
    if kwargs:
        raise ValueError(f"Unknown arguments: {list(kwargs.keys())}")
    
    return state


def apply_expected_changes(state: TestState, expected: Dict[str, Any], instruction_bytes: List[int], pc_location: int) -> TestState:
    """Apply expected changes to a test state, preserving instruction bytes in RAM"""
    result = state.copy()
    
    for reg in ['A', 'X', 'Y', 'PC']:
        if reg in expected:
            result.registers[reg] = expected[reg]
    
    for flag in ['Z', 'O', 'H', 'N']:
        if flag in expected:
            result.flags[flag] = expected[flag]
    
    # Always preserve instruction bytes in expected RAM
    for i, byte_val in enumerate(instruction_bytes):
        if pc_location + i < len(result.ram):
            result.ram[pc_location + i] = byte_val
    
    if 'ram' in expected:
        ram_changes = expected['ram']
        if isinstance(ram_changes, RAMRange):
            range_dict = ram_changes.to_dict()
            for addr, value in range_dict.items():
                if addr < len(result.ram) and value is not None:
                    result.ram[addr] = value
        elif isinstance(ram_changes, dict):
            for pos, value in ram_changes.items():
                if pos < len(result.ram):
                    result.ram[pos] = value
        elif isinstance(ram_changes, list):
            if len(ram_changes) > len(result.ram):
                result.ram = ram_changes.copy()
                # Re-apply instruction bytes after full replacement
                for i, byte_val in enumerate(instruction_bytes):
                    if pc_location + i < len(result.ram):
                        result.ram[pc_location + i] = byte_val
            else:
                result.ram[:len(ram_changes)] = ram_changes
                # Re-apply instruction bytes after partial replacement
                for i, byte_val in enumerate(instruction_bytes):
                    if pc_location + i < len(ram_changes):
                        result.ram[pc_location + i] = byte_val
    
    return result


def check_ram_patterns(state: TestState, patterns: List[RAMPattern]) -> Tuple[bool, List[str]]:
    """Check RAM patterns against the given state"""
    failed_patterns = []
    
    for pattern in patterns:
        if not pattern.check_pattern(state.ram):
            desc = pattern.description or f"Pattern check on {len(pattern.addresses)} addresses"
            failed_patterns.append(desc)
    
    return len(failed_patterns) == 0, failed_patterns


def states_equal(state1: TestState, state2: TestState, ignore_pc: bool = False, 
                ram_addresses: Optional[List[int]] = None, ram_patterns: Optional[List[RAMPattern]] = None) -> Tuple[bool, List[str]]:
    """Compare two test states for equality"""
    errors = []
    
    for reg, value in state1.registers.items():
        if ignore_pc and reg == 'PC':
            continue
        if value != state2.registers[reg]:
            errors.append(f"Register {reg}: expected {value}, got {state2.registers[reg]}")
    
    for flag, value in state1.flags.items():
        if value != state2.flags[flag]:
            errors.append(f"Flag {flag}: expected {value}, got {state2.flags[flag]}")
    
    if ram_patterns:
        patterns_pass, failed_patterns = check_ram_patterns(state2, ram_patterns)
        if not patterns_pass:
            errors.extend([f"RAM pattern failed: {desc}" for desc in failed_patterns])
    elif ram_addresses is not None:
        for addr in ram_addresses:
            if addr < len(state1.ram) and addr < len(state2.ram):
                if state1.ram[addr] != state2.ram[addr]:
                    errors.append(f"RAM[{addr}]: expected {state1.ram[addr]}, got {state2.ram[addr]}")
            elif addr >= len(state1.ram) or addr >= len(state2.ram):
                errors.append(f"RAM[{addr}]: address out of bounds")
    else:
        if state1.ram != state2.ram:
            diffs = []
            for i, (val1, val2) in enumerate(zip(state1.ram, state2.ram)):
                if val1 != val2:
                    diffs.append(f"RAM[{i}]: expected {val1}, got {val2}")
                    if len(diffs) >= 5:
                        break
            errors.extend(diffs)
            if len(diffs) >= 5:
                total_diffs = sum(1 for v1, v2 in zip(state1.ram, state2.ram) if v1 != v2)
                if total_diffs > 5:
                    errors.append(f"... and {total_diffs - 5} more RAM differences")
    
    return len(errors) == 0, errors


def extract_cpu_state(cpu: CPU) -> TestState:
    """Extract current state from CPU instance"""
    return TestState(
        registers=cpu.REG.copy(),
        flags=cpu.FLAGS.copy(),
        ram=cpu.RAM.copy(),
        data=[]
    )


def setup_cpu_for_instruction(instruction_class: type[BaseInstruction], initial_state: TestState, 
                             ram_size_kb: int = 4) -> CPU:
    """Set up CPU with instruction and initial state"""
    cpu = CPU(ram_size=ram_size_kb)
    
    # Get instruction opcode
    instruction_name = instruction_class.__name__
    if instruction_name not in NameToOpcode:
        raise ValueError(f"Instruction {instruction_name} not found in NameToOpcode mapping")
    
    opcode = NameToOpcode[instruction_name]
    
    # Build instruction bytes: [opcode, data...]
    instruction_bytes = [opcode] + initial_state.data
    
    # Load instruction at PC location (default 0)
    pc_location = initial_state.registers.get('PC', 0)
    cpu.load_data(instruction_bytes, offset=pc_location)
    
    # Set up initial CPU state
    cpu.REG = initial_state.registers.copy()
    cpu.FLAGS = initial_state.flags.copy()
    
    # Apply initial RAM state (preserve instruction bytes)
    for i, value in enumerate(initial_state.ram):
        # Don't overwrite the instruction we just loaded
        if i < pc_location or i >= pc_location + len(instruction_bytes):
            cpu.RAM[i] = value
    
    return cpu


def address_to_bytes(addr: int) -> List[int]:
    """Convert 16-bit address to [high_byte, low_byte] format for CPU"""
    return [(addr >> 8) & 0xFF, addr & 0xFF]


def test_instruction(
    instruction_class: type[BaseInstruction],
    initial: Optional[Dict[str, Any]] = None,
    expected: Optional[Dict[str, Any]] = None,
    test_cases: Optional[List[TestCase]] = None,
    ignore_pc: bool = True,
    ram_addresses: Optional[List[int]] = None,
    ram_patterns: Optional[List[RAMPattern]] = None,
    ram_size_kb: int = 4,
    verbose: bool = False
) -> bool:
    """
    Test an instruction through actual CPU execution.
    
    Args:
        instruction_class: Instruction class to test
        initial: Initial state values
        expected: Expected changes after execution
        test_cases: Multiple test scenarios
        ignore_pc: Ignore PC register changes (default True)
        ram_addresses: Only verify specific RAM addresses
        ram_patterns: Use pattern-based RAM verification
        ram_size_kb: CPU RAM size in KB
        verbose: Print detailed execution info
        
    Returns:
        True if all tests pass
    """
    if not issubclass(instruction_class, BaseInstruction):
        raise ValueError(f"{instruction_class} is not a subclass of BaseInstruction")
    
    if test_cases is None:
        if initial is None:
            initial = {}
        if expected is None:
            expected = {}
        test_cases = [TestCase("single_test", initial, expected)]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases):
        try:
            initial_state = create_cpu_state(**test_case.initial)
            
            # Set up CPU and get instruction info
            cpu = setup_cpu_for_instruction(instruction_class, initial_state, ram_size_kb)
            
            # Get instruction bytes for expected state calculation
            instruction_name = instruction_class.__name__
            opcode = NameToOpcode[instruction_name]
            instruction_bytes = [opcode] + initial_state.data
            pc_location = initial_state.registers.get('PC', 0)
            
            expected_state = apply_expected_changes(initial_state, test_case.expected, instruction_bytes, pc_location)
            
            # Execute one tick
            cpu.tick()
            
            # Extract final state
            actual_state = extract_cpu_state(cpu)
            
            # Compare states
            states_match, errors = states_equal(expected_state, actual_state, ignore_pc, ram_addresses, ram_patterns)
            
            if states_match:
                if verbose:
                    print(f"✓ Test case {i+1} '{test_case.name}' passed")
                    if test_case.description:
                        print(f"  Description: {test_case.description}")
            else:
                print(f"✗ Test case {i+1} '{test_case.name}' failed")
                if test_case.description:
                    print(f"  Description: {test_case.description}")
                for error in errors:
                    print(f"  {error}")
                all_passed = False
                
        except Exception as e:
            print(f"✗ Test case {i+1} '{test_case.name}' failed with exception: {e}")
            if test_case.description:
                print(f"  Description: {test_case.description}")
            all_passed = False
    
    return all_passed


def quick_test(instruction_class: type[BaseInstruction], **kwargs) -> bool:
    """Quick test with initial_/expected_ parameter naming"""
    initial = {}
    expected = {}
    test_params = {}
    
    for key, value in kwargs.items():
        if key.startswith('initial_'):
            param = key[8:]
            initial[param] = value
        elif key.startswith('expected_'):
            param = key[9:]
            expected[param] = value
        elif key in ['ram_addresses', 'ram_patterns', 'verbose', 'ignore_pc', 'ram_size_kb']:
            test_params[key] = value
        else:
            raise ValueError(f"Parameter {key} should start with 'initial_' or 'expected_', or be a test parameter")
    
    return test_instruction(instruction_class, initial, expected, **test_params)


def main():
    """Test all available CPU instructions with corrected expectations"""
    print("Comprehensive CPU Instruction Test Suite")
    print("=" * 50)
    
    # Import all instruction modules
    from python_cpu_emulator.instructions import arithmetic, bitwise, comparison, control, load_store, memory
    
    passed = 0
    failed = 0
    
    def run_test(name, test_func):
        nonlocal passed, failed
        try:
            if test_func():
                print(f"✓ {name}")
                passed += 1
            else:
                print(f"✗ {name}")
                failed += 1
        except Exception as e:
            print(f"✗ {name} - Exception: {e}")
            failed += 1
    
    # Arithmetic Instructions
    print("\n--- Arithmetic Instructions ---")
    run_test("INA", lambda: test_instruction(arithmetic.INA, {'A': 5}, {'A': 6}))
    run_test("INX", lambda: test_instruction(arithmetic.INX, {'X': 10}, {'X': 11}))
    run_test("INY overflow", lambda: test_instruction(arithmetic.INY, {'Y': 255}, {'Y': 0, 'O': True, 'Z': True}))
    run_test("DEA zero", lambda: test_instruction(arithmetic.DEA, {'A': 1}, {'A': 0, 'Z': True}))
    run_test("DEX underflow", lambda: test_instruction(arithmetic.DEX, {'X': 0}, {'X': 255, 'N': True}))
    run_test("DEY", lambda: test_instruction(arithmetic.DEY, {'Y': 100}, {'Y': 99}))
    run_test("AAX", lambda: test_instruction(arithmetic.AAX, {'A': 10, 'X': 20}, {'A': 30}))
    run_test("AAY overflow", lambda: test_instruction(arithmetic.AAY, {'A': 100, 'Y': 200}, {'A': 44, 'O': True}))
    run_test("AXY", lambda: test_instruction(arithmetic.AXY, {'X': 15, 'Y': 25}, {'X': 40}))
    run_test("SAX", lambda: test_instruction(arithmetic.SAX, {'A': 50, 'X': 20}, {'A': 30}))
    run_test("SAY underflow", lambda: test_instruction(arithmetic.SAY, {'A': 10, 'Y': 20}, {'A': 246, 'N': True}))
    run_test("SXY", lambda: test_instruction(arithmetic.SXY, {'X': 100, 'Y': 50}, {'X': 50}))
    
    # Bitwise Instructions
    print("\n--- Bitwise Instructions ---")
    run_test("NAX", lambda: test_instruction(bitwise.NAX, {'A': 0b11110000, 'X': 0b10101010}, {'A': 0b10100000}))
    run_test("NAY", lambda: test_instruction(bitwise.NAY, {'A': 0xFF, 'Y': 0x0F}, {'A': 0x0F}))
    run_test("NXY", lambda: test_instruction(bitwise.NXY, {'X': 0b11001100, 'Y': 0b10101010}, {'X': 0b10001000}))
    run_test("OAX", lambda: test_instruction(bitwise.OAX, {'A': 0b11110000, 'X': 0b00001111}, {'A': 0b11111111}))
    run_test("OAY", lambda: test_instruction(bitwise.OAY, {'A': 0x0F, 'Y': 0xF0}, {'A': 0xFF}))
    run_test("OXY", lambda: test_instruction(bitwise.OXY, {'X': 0b10101010, 'Y': 0b01010101}, {'X': 0b11111111}))
    run_test("XAX", lambda: test_instruction(bitwise.XAX, {'A': 0b11110000, 'X': 0b10101010}, {'A': 0b01011010}))
    run_test("XAY zero", lambda: test_instruction(bitwise.XAY, {'A': 0xFF, 'Y': 0xFF}, {'A': 0, 'Z': True}))
    run_test("XXY", lambda: test_instruction(bitwise.XXY, {'X': 0b11001100, 'Y': 0b10101010}, {'X': 0b01100110}))
    run_test("BLA", lambda: test_instruction(bitwise.BLA, {'A': 0b01010101}, {'A': 0b10101010}))
    run_test("BLX overflow", lambda: test_instruction(bitwise.BLX, {'X': 128}, {'X': 0, 'O': True, 'Z': True}))
    run_test("BLY", lambda: test_instruction(bitwise.BLY, {'Y': 0b00000001}, {'Y': 0b00000010}))
    run_test("BRA", lambda: test_instruction(bitwise.BRA, {'A': 0b10101010}, {'A': 0b01010101}))
    run_test("BRX zero", lambda: test_instruction(bitwise.BRX, {'X': 1}, {'X': 0, 'Z': True}))
    run_test("BRY", lambda: test_instruction(bitwise.BRY, {'Y': 0b11111111}, {'Y': 0b01111111}))
    
    # Comparison Instructions
    print("\n--- Comparison Instructions ---")
    run_test("EAX equal", lambda: test_instruction(comparison.EAX, {'A': 42, 'X': 42}, {'Z': True}))
    run_test("EAY not equal", lambda: test_instruction(comparison.EAY, {'A': 10, 'Y': 20}, {}))
    run_test("EXY equal", lambda: test_instruction(comparison.EXY, {'X': 100, 'Y': 100}, {'Z': True}))
    
    # Load/Store Instructions
    print("\n--- Load/Store Instructions ---")
    run_test("LDA", lambda: test_instruction(load_store.LDA, {'data': [42]}, {'A': 42}))
    run_test("LDX", lambda: test_instruction(load_store.LDX, {'data': [255]}, {'X': 255}))
    run_test("LDY", lambda: test_instruction(load_store.LDY, {'data': [0]}, {'Y': 0}))
    run_test("CAX", lambda: test_instruction(load_store.CAX, {'A': 123}, {'X': 123}))
    run_test("CAY zero", lambda: test_instruction(load_store.CAY, {'A': 0}, {'Y': 0, 'Z': True}))
    run_test("CXY", lambda: test_instruction(load_store.CXY, {'X': 200}, {'Y': 200}))
    run_test("CYX", lambda: test_instruction(load_store.CYX, {'Y': 50}, {'X': 50}))
    run_test("CXA", lambda: test_instruction(load_store.CXA, {'X': 99}, {'A': 99}))
    run_test("CYA", lambda: test_instruction(load_store.CYA, {'Y': 77}, {'A': 77}))
    
    # Conditional loads (flags cleared after execution)
    run_test("CAZ true", lambda: test_instruction(load_store.CAZ, {'Z': True, 'data': [88]}, {'A': 88, 'Z': False}))
    run_test("CAZ false", lambda: test_instruction(load_store.CAZ, {'Z': False, 'data': [88]}, {'A': 0}))
    run_test("NAZ true", lambda: test_instruction(load_store.NAZ, {'Z': True, 'data': [99]}, {'A': 0, 'Z': False}))
    run_test("NAZ false", lambda: test_instruction(load_store.NAZ, {'Z': False, 'data': [99]}, {'A': 99}))
    run_test("CAO true", lambda: test_instruction(load_store.CAO, {'O': True, 'data': [111]}, {'A': 111, 'O': False}))
    run_test("CAO false", lambda: test_instruction(load_store.CAO, {'O': False, 'data': [111]}, {'A': 0}))
    run_test("NAO true", lambda: test_instruction(load_store.NAO, {'O': True, 'data': [222]}, {'A': 0, 'O': False}))
    run_test("NAO false", lambda: test_instruction(load_store.NAO, {'O': False, 'data': [222]}, {'A': 222}))
    
    # Memory Instructions
    print("\n--- Memory Instructions ---")
    run_test("WMA", lambda: test_instruction(memory.WMA, {'A': 42, 'data': address_to_bytes(256)}, {'ram': {256: 42}}))
    run_test("WMX", lambda: test_instruction(memory.WMX, {'X': 99, 'data': address_to_bytes(512)}, {'ram': {512: 99}}))
    run_test("WMY", lambda: test_instruction(memory.WMY, {'Y': 200, 'data': address_to_bytes(768)}, {'ram': {768: 200}}))
    run_test("RMA", lambda: test_instruction(memory.RMA, {'ram': {100: 55}, 'data': address_to_bytes(100)}, {'A': 55}))
    run_test("RMX", lambda: test_instruction(memory.RMX, {'ram': {200: 77}, 'data': address_to_bytes(200)}, {'X': 77}))
    run_test("RMY", lambda: test_instruction(memory.RMY, {'ram': {300: 88}, 'data': address_to_bytes(300)}, {'Y': 88}))
    run_test("WMI", lambda: test_instruction(memory.WMI, {'A': 123, 'X': 50, 'Y': 1}, {'ram': {306: 123}}))
    run_test("RMI", lambda: test_instruction(memory.RMI, {'X': 100, 'Y': 0, 'ram': {100: 66}}, {'A': 66}))
    run_test("FIL", lambda: test_instruction(memory.FIL, {'A': 3, 'X': 500, 'Y': 1, 'data': [42]}, {'ram': ram_range(756, 759, 42)}))
    
    # Control Instructions (flags cleared after execution)
    print("\n--- Control Instructions ---")
    run_test("CLR", lambda: test_instruction(control.CLR, {'A': 100, 'X': 200, 'Y': 50}, {'A': 0, 'X': 0, 'Y': 0}))
    run_test("NOP", lambda: test_instruction(control.NOP, {'A': 42}, {'A': 42}))
    run_test("JMP", lambda: test_instruction(control.JMP, {'data': address_to_bytes(512)}, {'PC': 512}, ignore_pc=False))
    run_test("JNZ false", lambda: test_instruction(control.JNZ, {'Z': False, 'data': address_to_bytes(256)}, {'PC': 256}, ignore_pc=False))
    run_test("JNZ true", lambda: test_instruction(control.JNZ, {'Z': True, 'data': address_to_bytes(256)}, {'PC': 3, 'Z': False}, ignore_pc=False))
    run_test("JMZ true", lambda: test_instruction(control.JMZ, {'Z': True, 'data': address_to_bytes(768)}, {'PC': 768, 'Z': False}, ignore_pc=False))
    run_test("JMZ false", lambda: test_instruction(control.JMZ, {'Z': False, 'data': address_to_bytes(768)}, {'PC': 3}, ignore_pc=False))
    run_test("JNN false", lambda: test_instruction(control.JNN, {'N': False, 'data': address_to_bytes(100)}, {'PC': 100}, ignore_pc=False))
    run_test("JNN true", lambda: test_instruction(control.JNN, {'N': True, 'data': address_to_bytes(100)}, {'PC': 3, 'N': False}, ignore_pc=False))
    run_test("JMN true", lambda: test_instruction(control.JMN, {'N': True, 'data': address_to_bytes(200)}, {'PC': 200, 'N': False}, ignore_pc=False))
    run_test("JMN false", lambda: test_instruction(control.JMN, {'N': False, 'data': address_to_bytes(200)}, {'PC': 3}, ignore_pc=False))
    run_test("JNO false", lambda: test_instruction(control.JNO, {'O': False, 'data': address_to_bytes(306)}, {'PC': 306}, ignore_pc=False))
    run_test("JNO true", lambda: test_instruction(control.JNO, {'O': True, 'data': address_to_bytes(306)}, {'PC': 3, 'O': False}, ignore_pc=False))
    run_test("JMO true", lambda: test_instruction(control.JMO, {'O': True, 'data': address_to_bytes(512)}, {'PC': 512, 'O': False}, ignore_pc=False))
    run_test("JMO false", lambda: test_instruction(control.JMO, {'O': False, 'data': address_to_bytes(512)}, {'PC': 3}, ignore_pc=False))
    
    # Relative jumps
    run_test("JFA", lambda: test_instruction(control.JFA, {'A': 10, 'PC': 100}, {'PC': 111, 'A': 10}, ignore_pc=False))
    run_test("JFX", lambda: test_instruction(control.JFX, {'X': 50, 'PC': 200}, {'PC': 251, 'X': 50}, ignore_pc=False))
    run_test("JFY", lambda: test_instruction(control.JFY, {'Y': 5, 'PC': 1000}, {'PC': 1006, 'Y': 5}, ignore_pc=False))
    run_test("JBA", lambda: test_instruction(control.JBA, {'A': 20, 'PC': 100}, {'PC': 81, 'A': 20}, ignore_pc=False))
    run_test("JBX", lambda: test_instruction(control.JBX, {'X': 30, 'PC': 500}, {'PC': 471, 'X': 30}, ignore_pc=False))
    run_test("JBY", lambda: test_instruction(control.JBY, {'Y': 10, 'PC': 1000}, {'PC': 991, 'Y': 10}, ignore_pc=False))
    
    print(f"\n--- Test Results ---")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed + failed) > 0 else "No tests run")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)