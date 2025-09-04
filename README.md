<!-- omit in toc -->
# Watchword Dictionary

This repository contains the data files for the Watchword game dictionary, which are used by the following tools:

- Interactive webapp: <https://silvncr.github.io/watchword-dictionary/>
- Discord bot (uptime is not guaranteed): <https://discord.com/oauth2/authorize?client_id=1376949038061981860>

The game is available on [Steam](watchword-steam). I am not affiliated. See [Legal](#legal).

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

# Legal

This repository is licensed under the [BSD 3-Clause License](LICENSE).

This repository contains copyrighted material which is not owned by me. All intellectual property rights for [*Watchword*](watchword) belong to [Big Quail Games](bigquailgames). This repository is for educational purposes only and is not intended for commercial gain.

This repository and the project/s it contains are created and maintained with permission from the copyright holder/s.

---

[bigquailgames]: https://bigquailgames.com/
[watchword]: https://watchwordgame.com/
[watchword-steam]: https://store.steampowered.com/app/2906730/Watchword/
