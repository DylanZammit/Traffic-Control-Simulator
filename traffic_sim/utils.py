from typing import Self, Any


class Clock:

    def __init__(self):
        self.time = 0

    def tick(self) -> Self:
        self.time += 1
        return self

    def diff(self, t) -> int:
        return self.time - t


def print_padding(text: Any, pad_char: str = '*', string_len: int = 50):
    n_text = len(str(text))

    padding = pad_char * ((string_len - n_text) // 2 - 2)

    print(f'{padding} {text} {padding}')