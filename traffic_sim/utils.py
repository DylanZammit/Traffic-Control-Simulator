from typing import Self


class Clock:

    def __init__(self):
        self.time = 0

    def tick(self) -> Self:
        self.time += 1
        return self
