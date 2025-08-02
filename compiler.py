from instructions import NameToOpcode, OpcodeToName
from typ import Data


def read_file(filename: str) -> list[str]:
    try:
        with open(filename, "r") as f:
            return f.readlines()
    except IOError as e:
        print(f"Could not open file: {e}")
        return []


def parse_line(line: str) -> tuple[int, int, int]:
    parts = [x for x in line.strip().split(" ") if x != ""]
    if ";" in parts:
        parts = parts[:parts.index(";")]
    if parts:
        opcode = parts[0]
    else:
        return -1, -1, -1
    if opcode not in NameToOpcode:
        print(f"Error parsing line: '{opcode}' not in Instruction Set")
        return -1, -1, -1
    if len(parts) == 3:
        mem1, mem2 = parts[1:]
    elif len(parts) == 2:
        mem1, mem2 = parts[1], -1
    else:
        mem1, mem2 = -1, -1
    return NameToOpcode.get(opcode, -1), int(mem1), int(mem2)


def parsed_to_list(data: tuple[int, int, int]) -> Data:
    return [x for x in data if x > -1]


def parse_file(filename: str) -> Data:
    program = []
    lines = read_file(filename)
    for line in lines:
        program.extend(parsed_to_list(parse_line(line)))
    return program
