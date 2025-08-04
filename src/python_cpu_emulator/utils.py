from .types import Flags, Registers, Data


HALT_FLAGS:      Flags = {'Z': False, 'O': False, 'H': True,  'N': False}
BLANK_FLAGS:     Flags = {'Z': False, 'O': False, 'H': False, 'N': False}
ZERO_FLAGS:      Flags = {'Z': True,  'O': False, 'H': False, 'N': False}
OVERFLOW_FLAGS:  Flags = {'Z': False, 'O': True,  'H': False, 'N': False}
NEGATIVE_FLAGS:  Flags = {'Z': False, 'O': False, 'H': False, 'N': True }
OVER_ZERO_FLAGS: Flags = {'Z': True,  'O': True,  'H': False, 'N': False}


def build_readme() -> str:
    """Prints out a sorted list of opcodes ready to be imported into the INSTRUCTIONS.md file"""
    import operator
    from instructions import InstructionSet
    output = "| Name | Opcode | Length | Description | Flags |"
    for instr in (sorted(InstructionSet.values(), key=operator.attrgetter('opcode'))):
        output += f"\n| {str(instr)[21:-2]} | {instr.opcode} | {instr.length} | {instr.__doc__.strip()} | None |" # type: ignore
    return output


def data_to_memory_location(data: Data) -> int:
    """Converts a length 2 list of ints to a single int"""
    return (data[0] << 8) + data[1]


def blank_flags() -> Flags:
    """Returns a blank flag dictionary"""
    return BLANK_FLAGS


def set_flags(value: int) -> Flags:
    """Returns a dict of flags set by the integer value supplied"""
    if value < 0:
        return NEGATIVE_FLAGS
    elif value == 0:
        return ZERO_FLAGS
    elif value > 255:
        if value == 256:
            return OVER_ZERO_FLAGS
        return OVERFLOW_FLAGS
    return BLANK_FLAGS


def next_power_of_two(n):
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    # Check if n is already a power of 2
    if (n & (n - 1)) == 0:
        return n
    # Otherwise, find the next power of 2
    power = 1
    while power < n:
        power <<= 1
    return power