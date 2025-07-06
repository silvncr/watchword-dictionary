# utils

> [!WARNING]
> These scripts use your local modified [data](../data) files. That folder's README is required reading, and if processing a new version, you're expected to have followed the instructions under ["Adding support for a new version"](../data/README.md#adding-support-for-a-new-version).
>
> - `<version>_<...>.txt` files must exist under `/data/wordlists/`
> - `watchword_flags.json`, `watchword_references.json`, and `watchword_versions.json` must all be updated accordingly

Your working directory should be `watchword-dictionary`, not `utils`.

## Contents

`./coverage.py`

- Calculates the dictionary coverage (ratio of defined words to total words) of the latest wordlist

  - The latest version is determined by being at the top of `watchword_versions.json`

- Outputs to: `./out/coverage_<version>_<hash>.txt` (one output)
  - `<version>` is a Watchword game version, documented above
  - `<hash>` is a piece of a hash generated from `dictionary_combined.json`, representing the dictionary that was used

`./diff.py`

- Checks for additions and removals between old and new dictionary versions, within individual wordlist types

  - Old list: the topmost original list (`null` value) in `watchword_references.json`
  - New list: the topmost version in `watchword_versions.json`

- Outputs to: `./out/diff_<old>_<new>_<type>_<operation>.txt` (zero or more outputs for `<type>`, x2 for `<operation>`)
  - `<old>` and `<new>` are Watchword game versions, documented above
  - `<type>` is the wordlist type
  - `<operation>` is "additions" or "removals"

`./filter.py`

- Filters the latest wordlist according to arbitrary parameters

  - The latest version is determined by being at the top of `watchword_versions.json`
  - Filter criteria are provided through a `lambda` expression that must return a `bool`

- Outputs to: `./out/filter_<version>_<length>_<hash>.txt` (one output)
  - `<version>` is a Watchword game version, documented above
  - `<length>` is the length of the output
  - `<hash>` is a piece of a hash generated from the `lambda` expression, representing the filter that was used
