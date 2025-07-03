from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import typing
from pathlib import Path

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


def _utils_filter(wordlist: set[str], check: typing.Callable) -> set[str]:
    output = set()
    with alive_bar(len(wordlist)) as bar:
        for word in wordlist:
            with contextlib.suppress(IndexError):
                if check(word):
                    # print(f'word: {word} not in reference')
                    output.add(word)
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

    print(f'{version}: {len(wordlist)}')

    output = _utils_filter(
        wordlist=wordlist,
        check=(
            check := lambda word: all(
                [
                    'HC' in word,
                    # len(word) == 4,
                    # word[1] == 'S',
                    # word[3] == 'N',
                ],
            )
        ),
    )
    check_hash = hashlib.sha256(
        str(inspect.getsourcelines(check)[0])
            .replace("['", "")
            .replace("\\n']", "")
            .replace('  ', ' ')
            .replace('  ', ' ')
            .split("=")[1]
            .strip()
            .encode('utf-8'),
    ).hexdigest()[:6]
    print(f'{check_hash=}')

    print(f'number of words in output: {len(output)}')

    if output:
        Path('utils', 'out').mkdir(parents=True, exist_ok=True)
        Path(
            'utils', 'out', f'filter_{version}_{len(output)}_{check_hash}',
        ).write_text(
            '\n'.join(
                sorted(
                    output,
                    key=lambda x: (
                        # len(x),
                        x.lower(),
                    ),
                ),
            )
            + '\n',
        )
