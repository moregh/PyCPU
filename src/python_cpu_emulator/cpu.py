from .instructions import BaseInstruction, InstructionList
from .types import Flags, Registers, Data
from .display import Display
from .utils import BLANK_FLAGS, next_power_of_two


MIN_RAM_SIZE = 4       # 4KB ensures enough for 80x50 character display
MAX_RAM_SIZE = 64      # 64KB max for 16-bit address space


class CPU:
    def __init__(self, ram_size: int = MAX_RAM_SIZE, gpu: Display|None = None) -> None:
        """
        Initializes the CPU with a specified RAM size and an optional GPU.
        :param ram_size: RAM size in KB, range: 4 - 64, default: 64
        :param gpu: Optional Display object for GPU functionality.
        """
        self.RAM_SIZE: int = next_power_of_two(min(MAX_RAM_SIZE, max(MIN_RAM_SIZE, ram_size))) * 1024 # Clamp RAM to power of 2 between 4KB-64KB
        self.RAM: Data = [0] * self.RAM_SIZE
        self.GPU: Display|None = gpu
        # General Purpose Registers
        self.REG: Registers = {'A': 0, 'X': 0, 'Y': 0, 'PC': 0}
        # Status Registers
        self.FLAGS: Flags = BLANK_FLAGS
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
        self.REG['PC'] = (self.REG['PC'] + 1) & (self.RAM_SIZE - 1)
        return data

    def decode(self, opcode: int) -> tuple[BaseInstruction, Data]:
        instruction: BaseInstruction = InstructionList[opcode] # type: ignore
        data: Data = [self.fetch() for _ in range(instruction.length)]
        return instruction, data

    def execute(self, instruction: BaseInstruction, data: Data) -> None:
        self.REG, self.FLAGS = instruction.run(self.REG, self.FLAGS, data, self.RAM)

    def reset(self) -> None:
        self.REG: Registers = {'A': 0, 'X': 0, 'Y': 0, 'PC': 0}
        self.FLAGS: Flags = BLANK_FLAGS
        self.RAM: Data = [0] * self.RAM_SIZE

    def load_data(self, data: Data, offset: int = 0) -> None:
        end = offset + len(data)
        if end <= self.RAM_SIZE:
            self.RAM[offset:end] = data
        else:
            raise ValueError(f"Data exceeds RAM size: {end} > {self.RAM_SIZE}")

    def run(self, report_interval: int = 1_000_000) -> None:
        try:
            while not self.halted:
                self.tick()
                if self.TICKS % report_interval == 0:
                    print(self)
        except KeyboardInterrupt:
            print("Execution interrupted by user.")
        finally:
            print("Final CPU State:")
            print(self)

    def __str__(self) -> str:
        return f"Ticks: {self.TICKS:,} Registers: {self.REG} Flags: {self.FLAGS}"