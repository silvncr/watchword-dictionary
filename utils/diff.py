from __future__ import annotations

import json
from pathlib import Path

from alive_progress import alive_bar

flags: dict[str, list[str]] = json.loads(
    Path('data', 'watchword_flags.json').read_text(),
)
references: dict[str, str | None] = json.loads(
    Path('data', 'watchword_references.json').read_text(),
)
versions: list[str] = json.loads(Path('data', 'watchword_versions.json').read_text())


def _utils_diff(
    version_old: str, version_new: str, wordlist_type: str,
) -> tuple[set[str], set[str]]:
    if not all(
        Path('data', 'wordlists', f'{version}_{wordlist_type}.txt').exists()
        for version in (version_old, version_new)
    ):
        print(f'skipping {wordlist_type}..')
        return set(), set()

    print(f'{version_old}_{wordlist_type}.txt -> {version_new}_{wordlist_type}.txt')

    list_old = set(
        Path('data', 'wordlists', f'{version_old}_{wordlist_type}.txt')
        .read_text()
        .strip()
        .splitlines(),
    )
    list_new = set(
        Path('data', 'wordlists', f'{version_new}_{wordlist_type}.txt')
        .read_text()
        .strip()
        .splitlines(),
    )

    additions: set[str] = set()
    removals: set[str] = set()

    print(f'\t{version_old}: {len(list_old):_}')
    print(f'\t{version_new}: {len(list_new):_}')

    with alive_bar(len(list_new)) as bar:
        for word in list_new:
            if word not in list_old:
                additions.add(word)
            bar()
    with alive_bar(len(list_old)) as bar:
        for word in list_old:
            if word not in list_new:
                removals.add(word)
            bar()

    return additions, removals


if __name__ == '__main__':
    Path('utils', 'out').mkdir(parents=True, exist_ok=True)

    version_old = next(v for v in references if references[v] is None)
    version_new = versions[0]

    for wordlist_type in flags:
        additions, removals = _utils_diff(
            version_old=version_old,
            version_new=version_new,
            wordlist_type=wordlist_type,
        )

        print(f'\tdiff: {len(additions):_} additions, {len(removals):_} removals')

        for operation, output in {
            'additions': additions, 'removals': removals,
        }.items():
            if output:
                Path(
                    'utils',
                    'out',
                    f'diff_{version_old}_{version_new}_{wordlist_type}_{operation}.txt',
                ).write_text(
                    '\n'.join(
                        sorted(
                            output,
                            key=lambda x: (
                                # len(x),
                                x.lower()
                            ),
                        ),
                    )
                    + '\n',
                )
