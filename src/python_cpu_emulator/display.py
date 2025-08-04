class Display:
    def __init__(self, width: int = 80, height: int = 50) -> None:
        self.WIDTH: int = width
        self.HEIGHT: int = height

    def draw(self, data: list[int]):
        assert len(data) == len(self), f"GPU Error: received {len(data):,} pixels but require {len(self)}"
        output = ""
        for h in range(self.HEIGHT):
            for w in range(self.WIDTH):
                output += chr(data[(h * self.WIDTH) + w])
            output += "\n"
        print(output)

    def __len__(self) -> int:
        return self.WIDTH * self.HEIGHT
