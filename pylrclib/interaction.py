from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Sequence, TypeVar

T = TypeVar('T')


class Interaction:
    def __init__(self, *, interactive: bool, assume_yes: bool) -> None:
        self.interactive = interactive
        self.assume_yes = assume_yes

    def confirm(self, prompt: str, default: bool = False) -> bool:
        if self.assume_yes:
            return True
        if not self.interactive:
            return default
        suffix = '[Y/n]' if default else '[y/N]'
        answer = input(f'{prompt} {suffix}: ').strip().lower()
        if not answer:
            return default
        return answer in {'y', 'yes'}

    def choose_index(self, title: str, options: Sequence[T], labeler: Callable[[T], str] = str) -> Optional[int]:
        if not options:
            return None
        if len(options) == 1:
            return 0
        if not self.interactive or self.assume_yes:
            return 0
        print(title)
        for index, option in enumerate(options, 1):
            print(f'  {index}) {labeler(option)}')
        while True:
            answer = input(f'Choose 1-{len(options)} (or Enter to skip): ').strip()
            if not answer:
                return None
            if answer.isdigit():
                selected = int(answer)
                if 1 <= selected <= len(options):
                    return selected - 1
            print('Invalid input, try again.')

    def choose_value(self, title: str, options: Sequence[T], labeler: Callable[[T], str] = str) -> Optional[T]:
        index = self.choose_index(title, options, labeler)
        if index is None:
            return None
        return options[index]

    def missing_lyrics_action(self) -> str:
        if self.assume_yes or not self.interactive:
            return 'skip'
        while True:
            answer = input('No local lyrics found. Choose [s]kip / [p]lain-file / [y]synced-file / [i]nstrumental / [q]uit: ').strip().lower()
            if answer in {'s', 'p', 'y', 'i', 'q'}:
                return {'s': 'skip', 'p': 'plain', 'y': 'synced', 'i': 'instrumental', 'q': 'quit'}[answer]
            print('Invalid input, try again.')

    def manual_path(self, *, expected: str) -> Optional[Path]:
        if not self.interactive:
            return None
        raw = input(f'Enter {expected} file path: ').strip().strip('"').strip("'")
        if not raw:
            return None
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        path = path.resolve()
        if not path.exists() or not path.is_file():
            print(f'Invalid file: {path}')
            return None
        return path
