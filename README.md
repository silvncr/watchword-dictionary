<!-- omit in toc -->
# Watchword Dictionary

This repository contains the data files for the Watchword game dictionary, which are used by the following tools:

- Interactive webapp: <https://silvncr.github.io/watchword-dictionary/>
- Discord bot (uptime is not guaranteed): <https://discord.com/oauth2/authorize?client_id=1376949038061981860>

---

## Structure

Components to be documented:

- [x] Dictionary data: see [data](data)
- [x] Wordlist utilities: see [utils](utils)
- [ ] Webapp
- [ ] Discord bot

---

## Changelog

> [!NOTE]
> Development occurs on the Discord bot first, then the webapp is updated for parity. As such, only the Discord bot is version-tracked.

0.4.x

- Removed `/coverage` command for simplicity
  - From this point, the application should only contain functionality relating to the Watchword game
  - Any miscellaneous functionality (such as the former `/coverage`) will be moved to [utils](utils)

<!--
0.4.x - abandoned; converted to utils

- Added `/diff` command to track wordlist changes across versions
- Added `/filter` command to interactively search the wordlist
-->

0.3.x

- Added flags system
  - Multiple wordlists are compiled on load to closer reflect in-game behaviour
  - Flag names are arbitrary; it's up to the user to discern what they mean

0.2.x

- Added dictionary functionality
  - Definitions appear under `/check` result
  - Added `/coverage` command to see an overview of dictionary data per version
- Added support for multiple game versions
  - `/check` and `/coverage` now have a `version:` parameter
  - The newest version is selected by default

0.1.x

- Added `/check` command; check if a word is valid or invalid
- Added basic `/ping` command

---
