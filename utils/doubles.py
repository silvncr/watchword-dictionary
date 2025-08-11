from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import typing
from pathlib import Path
from string import ascii_uppercase

from alive_progress import alive_bar

flags: dict[str, list[str]] = json.loads(
    Path('data', 'watchword_flags.json').read_text(),
)
references: dict[str, str | None] = json.loads(
    Path('data', 'watchword_references.json').read_text(),
)
versions: list[str] = json.loads(Path('data', 'watchword_versions.json').read_text())


def _find_reference(version: str) -> str:
    if references[version] is None:
        return version
    return _find_reference(references[version])  # type: ignore


def _utils_doubles(wordlist: set[str]) -> dict[str, int]:
    output = {}
    wordlist_str = '\n'.join(wordlist)
    with alive_bar(len(ascii_uppercase)) as bar:
        for letter in ascii_uppercase:
            output[letter] = wordlist_str.count(letter * 2)
            bar()
    return output


if __name__ == '__main__':
    version = versions[0]
    version_referenced = _find_reference(version)

    wordlist: set[str] = set()
    for wordlist_type in flags:
        if (
            path := Path(
                'data', 'wordlists', f'{version_referenced}_{wordlist_type}.txt',
            )
        ).exists():
            for word in path.read_text().strip().splitlines():
                wordlist.add(word)

    print(f'{version}: {len(wordlist):_}')

    output = _utils_doubles(wordlist=wordlist)

    print(output)

    Path('utils', 'out').mkdir(parents=True, exist_ok=True)
    Path('utils', 'out', f'doubles_{version}.json').write_text(
        json.dumps(output, indent=4) + '\n',
    )
