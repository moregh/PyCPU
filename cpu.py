from instructions import BaseInstruction, InstructionSet
from display import Display
from typ import Flags, Registers


MIN_RAM_SIZE = 4096       # 4KB ensures enough for 80x50 character display
MAX_RAM_SIZE = 64 * 1024  # 64KB for 16-bit address space



class CPU:
    def __init__(self, ram_size: int = MAX_RAM_SIZE, gpu: Display|None = None) -> None:
        self.RAM_SIZE: int = min(MAX_RAM_SIZE, max(MIN_RAM_SIZE, ram_size))  # Clamp RAM size to 64KB for 16-bit address space
        self.RAM: list[int] = [0 for _ in range(self.RAM_SIZE)]
        self.GPU: Display|None = gpu
        # General Purpose Registers
        self.REG: Registers = {'A': 0, 'X': 0, 'Y': 0, 'PC': 0}
        # Status Registers
        self.FLAGS: Flags = {'Z': False, 'O': False, 'H': False, 'N': False}
        # Tick Counter
        self.TICKS: int = 0
        # GPU Setup
        self.GPU_SIZE: int = len(self.GPU) if self.GPU else -1
        self.GPU_OFFSET: int = self.RAM_SIZE - self.GPU_SIZE if self.GPU else -1

    @property
    def halted(self) -> bool:
        return self.FLAGS['H']

    def tick(self) -> None:
        if self.halted:
            return
        # Fetch
        opcode = self.fetch()
        # Decode
        instruction, data = self.decode(opcode)
        # Execute
        self.execute(instruction, data)
        # Increment counter
        self.TICKS += 1
        # Handle GPU if required
        if self.GPU:
            self.GPU.draw(self.RAM[self.GPU_OFFSET:])

    def fetch(self) -> int:
        data = self.RAM[self.REG['PC']]
        self.REG['PC'] = (self.REG['PC'] + 1) % self.RAM_SIZE  # Modulo length of RAM to wrap when required
        return data

    def decode(self, opcode: int) -> tuple[BaseInstruction, list[int]]:
        try:
            instruction: BaseInstruction = InstructionSet[opcode] # type: ignore
        except KeyError:
            instruction: BaseInstruction = InstructionSet[0]  # type: ignore # Default to HLT instruction if invalid data is found
        data: list[int] = [self.fetch() for _ in range(instruction.length)]
        return instruction, data

    def execute(self, instruction: BaseInstruction, data: list[int]) -> None:
        self.REG, self.FLAGS = instruction.run(self.REG, self.FLAGS, data, self.RAM)

    def reset(self) -> None:
        self.REG: dict[str, int] = {'A': 0, 'X': 0, 'Y': 0, 'PC': 0}
        self.FLAGS: dict[str, bool] = {'Z': False, 'O': False, 'H': False, 'N': False}
        self.RAM = [0 for _ in range(self.RAM_SIZE)]

    def load_data(self, data: list[int], offset: int = 0) -> None:
        for i, d in enumerate(data):
            self.RAM[(i + offset) % self.RAM_SIZE] = d  # Mod by length of RAM to wrap round if required

    def __str__(self) -> str:
        return f"Ticks: {self.TICKS:,} Registers: {self.REG} Flags: {self.FLAGS}"
