BLANK_FLAGS = {'Z': False, 'O': False, 'H': False, 'N': False}
ZERO_FLAGS = {'Z': True, 'O': False, 'H': False, 'N': False}
OVERFLOW_FLAGS = {'Z': False, 'O': True, 'H': False, 'N': False}
NEGATIVE_FLAGS = {'Z': False, 'O': False, 'H': False, 'N': True}


def build_readme() -> str:
    """Prints out a sorted list of opcodes ready to be imported into the INSTRUCTIONS.md file"""
    import operator
    from instructions import InstructionSet
    output = "| Name | Opcode | Length | Description | Flags |"
    for instr in (sorted(InstructionSet.values(), key=operator.attrgetter('opcode'))):
        output += f"\n| {str(instr)[21:-2]} | {instr.opcode} | {instr.length} | {instr.__doc__.strip()} | None |" # type: ignore
    return output


def data_to_memory_location(data: list[int]) -> int:
    """Converts a length 2 list of ints to a single int"""
    return (data[0] << 8) + data[1]


def blank_flags() -> dict[str, bool]:
    """Returns a blank flag dictionary"""
    return BLANK_FLAGS


def set_flags(value: int) -> dict[str, bool]:
    """Returns a dict of flags set by the integer value supplied"""
    if value < 0:
        return NEGATIVE_FLAGS
    elif value == 0:
        return ZERO_FLAGS
    elif value > 255:
        return OVERFLOW_FLAGS
    return BLANK_FLAGS
