from time import time


class Display:
    def __init__(self, width: int = 80, height: int = 50, fps: int = 120) -> None:
        self.WIDTH: int = width
        self.HEIGHT: int = height
        self.FPS: int = fps
        self.interval: float = 1.0 / fps
        self.last_drawn: float = 0.0

    def draw(self, data: list[int]):
        assert len(data) == len(self), f"GPU Error: received {len(data):,} pixels but require {len(self)}"
        if time() - self.last_drawn < self.interval:
            return
        self.last_drawn = time()
        output = ""
        for h in range(self.HEIGHT):
            for w in range(self.WIDTH):
                output += chr(data[(h * self.WIDTH) + w])
            output += "\n"
        print(output)

    def __len__(self) -> int:
        return self.WIDTH * self.HEIGHT
