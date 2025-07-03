from __future__ import annotations

import hashlib
import json
from pathlib import Path

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


def _utils_coverage(wordlist: set[str], definitions: dict[str, str]) -> str:
    used_definitions: dict[str, str] = {
        key: val
        for key, val in definitions.items()
        if key in wordlist
    }
    return '\n'.join(
        [
            f'words: {len(wordlist):,}',
            f'definitions: {len(used_definitions):,}',
            f'coverage: {len(used_definitions) / len(wordlist) * 100:.2f}%',
        ],
    )


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

    definitions = json.loads(Path('data', 'dictionary_combined.json').read_text())
    definitions_hash = hashlib.sha256(
        json.dumps(definitions, sort_keys=True).encode(),
    ).hexdigest()[:6]
    print(f'{definitions_hash=}')

    output = _utils_coverage(wordlist=wordlist, definitions=definitions)

    print(output)

    Path('utils', 'out').mkdir(parents=True, exist_ok=True)
    Path('utils', 'out', f'coverage_{version}_{definitions_hash}.txt').write_text(
        output + '\n',
    )
