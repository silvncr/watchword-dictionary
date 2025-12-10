from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from string import ascii_uppercase

import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands

load_dotenv()


TOKEN = os.environ['DISCORD_TOKEN']

VERSION = '0.5.2'


WATCHWORD_REFERENCES: dict[str, str | None] = json.loads(
    Path('data', 'watchword_references.json').read_text(),
)
WATCHWORD_VERSIONS: list[str] = json.loads(
    Path('data', 'watchword_versions.json').read_text(),
)


class VERSIONS:
    # main
    bot = VERSION
    watchword = WATCHWORD_VERSIONS[0]

    # wordlist
    qrs = '3.0.0'
    listpatches = '1.0'
    wordlist_cleaner = '0.2'
    cleanlist = '0.1.0-pre'


def find_reference(version: str) -> str:
    'Find the reference for a given version.'
    if WATCHWORD_REFERENCES[version] is None:
        return version
    return find_reference(WATCHWORD_REFERENCES[version])  # type: ignore


def create_version_string(version: str) -> str:
    'Create a game version string with reference.'
    version_referenced = find_reference(version)
    if version == version_referenced:
        return version
    return f'{version_referenced} → {version}'


OPTIONS = {
    'version': nextcord.SlashOption(
        name='version',
        description='Watchword game version to check against',
        required=False,
        choices=[*WATCHWORD_VERSIONS],
        default=WATCHWORD_VERSIONS[0],
        verify=True,
    ),
    'word': nextcord.SlashOption(
        name='word',
        description='Word to check against the Watchword dictionary',
        required=True,
        min_length=2,
        max_length=40,
        verify=True,
    ),
}


client = commands.Bot(
    description=f'Watchword Dictionary v{VERSION}', intents=nextcord.Intents.default(),
)


def embed(title: str, description: str, color: int = 0xFFFFFF) -> nextcord.Embed:
    'Create a simple embed.'
    return (
        nextcord.Embed(title=title, description=description, color=color)
        # .set_author(
        #     name='Watchword Dictionary',
        #     icon_url='https://cdn.discordapp.com/avatars/1376949038061981860/79b29fe28db10cc2438b601201461a8a.webp',
        # )
        .set_footer(text=f'v{VERSION}')
    )


def find_definition(word: str) -> str | None:
    'Find the definition of a word in the wordlist.'
    return definitions.get(word)


@client.event
async def on_ready() -> None:
    'Event triggered when the bot is ready.'
    print(f'Logged in as {client.user} ({client.user.id})')  # type: ignore
    await client.change_presence(
        activity=nextcord.Activity(
            type=nextcord.ActivityType.watching,
            name=f'Watching for {len(wordlist_full):,} words',
        ),
        status=nextcord.Status.online,
    )


@client.slash_command(
    name='check', description='Check against the Watchword dictionary',
)
async def check(
    interaction: nextcord.Interaction,
    word: str = OPTIONS['word'],
    version: str = OPTIONS['version'],
) -> None:
    'Check a word against the Watchword dictionary.'
    print(f'Check requested by {interaction.user} ({interaction.user.id}) - "{word}"')  # type: ignore
    word = word.upper().strip()
    word = ''.join(c for c in word if c in ascii_uppercase)
    print(f'\tProcessed: "{word}"')
    for _error_condition, _error_message in [
        (not word, 'Word is empty!'),
        (not 2 <= len(word) <= 40, 'Words must be between 2 and 40 characters long!'),
        (any(c not in ascii_uppercase for c in word), 'Words must have letters only!'),
        (version not in WATCHWORD_VERSIONS, 'Version is not tracked!'),
        (version not in WATCHWORD_REFERENCES, 'Reference for version not found!'),
    ]:
        if _error_condition:
            await interaction.response.defer(ephemeral=True)
            print(f'\tInvalid input: "{_error_message}"')
            try:
                _version_string = create_version_string(version)
            except IndexError:
                _version_string = '(could not be parsed)'
            _processed_input = '\n'.join(
                [
                    f'word: {word or '(could not be parsed)'}',
                    f'version: {_version_string}',
                ],
            )
            await interaction.followup.send(
                embed=embed(
                    title=':warning: An error was caught!',
                    description=f'Processed input:\n```\n{_processed_input}\n```',
                    color=0xFFFF00,
                ).add_field(name='Reason', value=f'> {_error_message}', inline=False),
            )
            return
    await interaction.response.defer()
    version_referenced = find_reference(version)
    version_string = create_version_string(version)
    if word in wordlists[version_referenced]:
        print('\tValid word')
        _embed = embed(
            title=f':white_check_mark: {word}',
            description=f'This is a valid word in Watchword {version_string}',
            color=0x00FF00,
        )
        if _definition := find_definition(word):
            print(f'\tDefinition found: "{_definition}"')
            _embed = _embed.add_field(
                name='Definition', value=f'```\n{_definition}\n```', inline=False,
            )
        else:
            print('\tNo definition found')
        print(f'\tFlags: {(_flags := wordlists[version_referenced][word])}')
        _embed.add_field(
            name='Flags',
            value=f'{', '.join(sorted(_flags))}' if _flags else '(none)',
            inline=False,
        )
        await interaction.followup.send(embed=_embed)
    else:
        print('\tInvalid word')
        await interaction.followup.send(
            embed=embed(
                title=f':x: {word}',
                description=(f'This is not a valid word in Watchword {version_string}'),
                color=0xFF0000,
            ),
        )


@client.slash_command(
    name='coverage', description='Get the coverage of word definitions',
)
async def coverage(
    interaction: nextcord.Interaction, version: str = OPTIONS['version'],
) -> None:
    'Get the coverage of word definitions in the Watchword dictionary.'
    await interaction.response.defer(ephemeral=True)
    version_ref = find_reference(version)
    version_s = create_version_string(version)
    _words = len(wordlists[version_ref])
    _definitions = len({word for word in definitions if word in wordlists[version_ref]})
    await interaction.followup.send(
        embed=embed(
            title=':bar_chart: Coverage',
            description=f'Watchword {version_s}```\n{
                '\n'.join(
                    [
                        f'words: {_words:,}',
                        f'definitions: {_definitions:,}',
                        f'coverage: {_definitions / _words * 100:.2f}%',
                    ]
                )
            }\n```',
        ),
    )
    print(f'Coverage requested by {interaction.user} ({interaction.user.id})')  # type: ignore


@client.slash_command(
    name='host',
    description='Pull information about the host machine (for debugging purposes)',
)
async def host(interaction: nextcord.Interaction) -> None:
    'Host command to check host machine info'
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(
        embed=embed(
            title=':desktop: Host machine',
            description=f'```\n{
                '\n'.join(
                    [
                        f'os: {
                            ' '.join(
                                [
                                    *platform.system_alias(
                                        system=platform.system(),
                                        release=platform.release(),
                                        version=platform.version()
                                    )[:-1],
                                    platform.machine()
                                ]
                            )
                        } ',
                        (
                            'python:'
                            f' {platform.python_implementation()}'
                            f' {platform.python_version()}'
                        ),
                    ]
                )
            }\n```',
        ),
    )


@client.slash_command(
    name='info', description='See information about Watchword and this bot',
)
async def info(interaction: nextcord.Interaction) -> None:
    'Info command to give information on Watchword and this bot'
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(
        embed=embed(
            title=f':eyes: Watchword Dictionary v{VERSION}',
            description='<https://github.com/silvncr/watchword-dictionary>',
        )
        .add_field(
            name='What is Watchword?',
            value=(
                '[**Watchword**](https://store.steampowered.com/app/2906730/Watchword/)'
                ' is a word-based roguelike deckbuilder, developed and published'
                ' by **Big Quail Games**.'
            ),
            inline=False,
        )
        .add_field(
            name='What is Watchword Dictionary?',
            value=(
                'This bot is a helper tool for Watchword. Its main purpose is'
                ' letting you check if a word is legal to play, but it\'s since'
                ' expanded to track various data across game versions.'
            ),
            inline=False,
        )
        .add_field(
            name='What is your affiliation?',
            value=(
                'This bot was made and continues to exists with permission from,'
                ' but not affiliation with, the game\'s creator. This bot exists as a'
                ' separate tool, with its code and datasets hosted online,'
                ' open-sourced and free to view on GitHub (linked above).'
            ),
            inline=False,
        ),
    )


@client.slash_command(name='ping', description='Measure the current bot latency')
async def ping(interaction: nextcord.Interaction) -> None:
    'Ping command to check bot latency.'
    await interaction.response.defer(ephemeral=True)
    _latency: float = round(client.latency * 100, 2)
    await interaction.followup.send(
        embed=embed(title=':ping_pong: Pong!', description=f'```\n{_latency} ms\n```'),
    )
    print(
        f'Ping requested by {interaction.user} ({interaction.user.id})',
        f'- {_latency} ms',
    )


@client.slash_command(
    name='versions',
    description='Fetch the versions of apps and tools the bot depends on',
)
async def versions(interaction: nextcord.Interaction) -> None:
    'Versions command to check various app and tool versions'
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(
        embed=embed(
            title=':clipboard: Versions',
            description='\n'.join(
                [
                    '```',
                    '  main',
                    f'bot: {VERSIONS.bot}',
                    f'watchword: {VERSIONS.watchword}',
                    '',
                    '  wordlist',
                    f'qrs: {VERSIONS.qrs}',
                    f'listpatches: {VERSIONS.listpatches}',
                    f'wordlist-cleaner: {VERSIONS.wordlist_cleaner}',
                    f'cleanlist: {VERSIONS.cleanlist}',
                    '```',
                ],
            ),
        ),
    )
    print(f'Info requested by {interaction.user} ({interaction.user.id})')


if __name__ == '__main__':
    print(f'\n\tWatchword Dictionary v{VERSION}\n')
    wordlists: dict[str, dict[str, set[str]]] = {}
    wordlist_full: set[str] = set()
    for _version in WATCHWORD_VERSIONS:
        if _version != find_reference(_version):
            continue
        print(f'Loading wordlist for version {_version}..')
        wordlists[_version] = {}
        for _type, _flags in json.loads(
            Path('data', 'watchword_flags.json').read_text(),
        ).items():
            if (_path := Path('data', 'wordlists', f'{_version}_{_type}.txt')).exists():
                wordlists[_version] |= {
                    word.strip().upper(): wordlists[_version].get(
                        word.strip().upper(), set(),
                    )
                    | set(_flags)
                    for word in _path.read_text().strip().splitlines()
                }
        wordlist_full.update(wordlists[_version].keys())
        if not wordlists[_version]:
            print('\tNo words found')
            continue
        print(
            f'\tLoaded {len(wordlists[_version]):_} words',
            f'({len(wordlist_full):_} total)',
        )

    print(f'Loaded {len(wordlist_full):_} total words')

    _definitions_temp: dict[str, str] = json.loads(
        Path('data', 'dictionary_combined.json').read_text(),
    )
    definitions: dict[str, str] = {
        key: val for key, val in _definitions_temp.items() if key in wordlist_full
    }
    print(
        f'Loaded the required {len(definitions) / len(_definitions_temp) * 100:.2f}% '
        f'of definitions ({len(definitions):_} of {len(_definitions_temp):_})',
    )
    del _definitions_temp

    client.run(TOKEN)
