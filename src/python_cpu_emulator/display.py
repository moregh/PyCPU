from time import time


class Display:
    def __init__(self, width: int = 80, height: int = 50, fps: int = 120) -> None:
        self.WIDTH: int = width
        self.HEIGHT: int = height
        self.FPS: int = fps
        self.interval: float = 1.0 / fps
        self.last_drawn: float = 0.0

    def should_draw(self) -> bool:
        if time() - self.last_drawn < self.interval:
            return False
        return True

    def draw(self, data: list[int]):
        assert len(data) == len(self), f"GPU Error: received {len(data):,} pixels but require {len(self)}"
        self.last_drawn = time()
        lines = []
        for h in range(self.HEIGHT):
            start = h * self.WIDTH
            line = ''.join(chr(data[start + w]) for w in range(self.WIDTH))
            lines.append(line)    
        print('\n'.join(lines))

    def __len__(self) -> int:
        return self.WIDTH * self.HEIGHT
