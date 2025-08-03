from instructions import NameToOpcode, OpcodeToName, InstructionSet
from typ import Data


def read_file(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()


def strip_comments_and_whitespace(code: str) -> str:
    lines = code.splitlines()
    stripped_lines = []
    for line in lines:
        line = line.split(";", 1)[0].strip()  # Remove comments and strip whitespace
        if line:  # Only add non-empty lines
            stripped_lines.append(line)
    return "\n".join(stripped_lines)


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


def parse_code(code: str) -> Data:
    code = strip_comments_and_whitespace(code)
    instructions = code.split("\n")
    parsed_instructions: Data = []
    labels = {}

    for instruction in instructions:
        parts = instruction.split()
        if parts[0].startswith(":"):
            label = parts[0][1:]
            if label in labels:
                raise ValueError(f"Duplicate label found: {label}")
            labels[label] = len(parsed_instructions)
            continue
        opcode = NameToOpcode.get(parts[0])
        if opcode is None:
            raise ValueError(f"Unknown opcode: {parts[0]}")
        if len(parts) != InstructionSet[opcode].length + 1:
            if parts[1] not in labels:
                # If the second part is a label, we allow it to be missing
                raise ValueError(f"Incorrect number of arguments for {OpcodeToName[opcode]}: {len(parts) - 1} provided, {InstructionSet[opcode].length} expected")    
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
    return parsed_instructions


def compile(filename: str) -> Data:
    code = read_file(filename)
    return parse_code(code)
