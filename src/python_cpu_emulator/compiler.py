from .instructions import NameToOpcode, InstructionSet
from .types import Data


def read_file(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()


def strip_comments_and_whitespace(code: str) -> list[str]:
    lines = code.splitlines()
    stripped_lines = []
    for line in lines:
        line = line.split(";", 1)[0].strip()  # Remove comments and strip whitespace
        if line:  # Only add non-empty lines
            stripped_lines.append(line)
    return stripped_lines


def addr_to_ints(addr: str) -> tuple[int, int]:
    if not addr.startswith("$"):
        raise ValueError(f"Invalid address format: {addr}")
    try:
        int_addr = int(addr[1:], 16)
    except ValueError:
        raise ValueError(f"Invalid address: {addr}")
    if int_addr < 0 or int_addr > 0xFFFF:
        raise ValueError(f"Address out of range: {addr}")
    return (int_addr >> 8) & 0xFF, int_addr & 0X00FF


def int_to_addr(value: int) -> tuple[int, int]:
    return (value >> 8) & 0xFF, value & 0x00FF


def two_pass(code: str, verbose=False) -> Data:
    # First pass: parse the code and collect labels
    instructions = [x for x in strip_comments_and_whitespace(code) if x]
    parsed_instructions = []
    labels = {}
    idx = 0
    for instruction in instructions:
        parts = instruction.split()
        assert 0 < len(parts) < 4, f"Invalid instruction format: {parts}"
        if parts[0].startswith(":"):
            label = parts[0][1:]
            if label in labels:
                raise ValueError(f"Duplicate label found: {label}")
            labels[label] = idx
            continue
        opcode = NameToOpcode.get(parts[0])
        if opcode is None:
            raise ValueError(f"Unknown opcode: {parts[0]}")
        idx += InstructionSet[opcode].length + 1
    # second pass
    for instruction in instructions:
        parts = instruction.split()
        if parts[0].startswith(":"):
            continue
        opcode = NameToOpcode.get(parts[0])
        if opcode is None:
            raise ValueError(f"Unknown opcode: {parts[0]}")
        parsed_instructions.append(opcode)
        for arg in parts[1:]:
            if arg.startswith("$"):
                high, low = addr_to_ints(arg)
                parsed_instructions.append(high)
                parsed_instructions.append(low)
            elif arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
                parsed_instructions.append(int(arg))
            elif arg in labels:
                high, low = int_to_addr(labels[arg])
                parsed_instructions.append(high)
                parsed_instructions.append(low)
            else:
                raise ValueError(f"Invalid argument: {arg}")
    if verbose:
        print(f"Parsed {len(parsed_instructions)} bytes of instructions from {len(instructions)} lines.")
        print(f"Labels found: {labels}")
    return parsed_instructions


def compile(filename: str, verbose=False) -> Data:
    code = read_file(filename)
    return two_pass(code, verbose)
