// DOM elements
const section_loading = document.getElementById('loading');
const loading_message = document.getElementById('loading-message');

const section_version = document.getElementById('version');
const version_form = document.getElementById('version-form');
const version_select = document.getElementById('version-select');
const version_button = document.getElementById('version-button');

const section_check_word = document.getElementById('check-word');
const check_word_form = document.getElementById('check-word-form');
const word_input = document.getElementById('word-input');
const check_button = document.getElementById('check-button');
const result_display = document.getElementById('result');

const section_definition = document.getElementById('definition');
const definition_text = document.getElementById('definition-text');

const section_flags = document.getElementById('flags');
const flags_text = document.getElementById('flags-text');

const section_info = document.getElementById('info');
const section_coverage = document.getElementById('coverage');


// Helper functions
async function read_file(file_path) {
    return await (await fetch(file_path)).text();
};

async function read_json(file_path) {
    return await JSON.parse(await (await fetch(file_path)).text());
};

function find_reference(version) {
    if (WATCHWORD_REFERENCES[version] == null) {
        return version;
    }
    return find_reference(WATCHWORD_REFERENCES[version]);
};

function create_version_string(version) {
    const version_referenced = find_reference(version);
    if (version === version_referenced) {
        return version;
    }
    return `${version_referenced} → ${version}`;
};

function find_definition(word) {
    const definition = DICTIONARY_COMBINED[word.toUpperCase()];
    if (definition) {
        return definition;
    }
    return null;
};


// Session management
let _word;
let _word_is_valid;
let _definition;
let selected_version;
let version_referenced;
let version_string;
let current_wordlist = {};


// Load wordlist for the selected version
async function load_wordlist(version) {
    current_wordlist = {};

    // Prepare all file reads in parallel
    const filePromises = Object.entries(WATCHWORD_FLAGS).map(async ([_type, _flags]) => {
        const filePath = `data/wordlists/${version}_${_type}.txt`;
        const content = await read_file(filePath);
        return {
            _type, _flags, words: content.trim().split('\n').map(w => w.toUpperCase())
        };
    });

    const results = await Promise.all(filePromises);

    for (const { _flags, words } of results) {
        for (const word of words) {
            if (!word) {
                continue;
            };
            if (!(word in current_wordlist)) {
                current_wordlist[word] = new Set(_flags);
            } else {
                _flags.forEach(flag => current_wordlist[word].add(flag));
            };
        };
    };

    console.log(`loaded wordlist: ${Object.keys(current_wordlist).length} words`);
};


// Load data files
async function load_data() {
    const DICTIONARY_COMBINED = await read_json('data/dictionary_combined.json');
    console.assert(
        Boolean(DICTIONARY_COMBINED),
        'DICTIONARY_COMBINED is null, undefined, or empty'
    );
    console.log(`loaded dictionary: ${Object.keys(DICTIONARY_COMBINED).length} words`);

    const WATCHWORD_FLAGS = await read_json('data/watchword_flags.json');
    console.assert(
        Boolean(WATCHWORD_FLAGS),
        'WATCHWORD_FLAGS is empty, null, or undefined'
    )
    console.log(`loaded flags: ${Object.keys(WATCHWORD_FLAGS).length} flags`);

    const WATCHWORD_REFERENCES = await read_json('data/watchword_references.json');
    console.assert(
        Boolean(WATCHWORD_REFERENCES),
        'WATCHWORD_REFERENCES is empty, null, or undefined'
    );
    console.log(`loaded references: ${Object.keys(WATCHWORD_REFERENCES).length} references`);

    const WATCHWORD_VERSIONS = await read_json('data/watchword_versions.json');
    console.assert(
        Boolean(WATCHWORD_VERSIONS),
        'WATCHWORD_VERSIONS is empty, null, or undefined'
    );
    console.log(`loaded versions: ${WATCHWORD_VERSIONS.length} versions`);

    globalThis.DICTIONARY_COMBINED = DICTIONARY_COMBINED;
    globalThis.WATCHWORD_FLAGS = WATCHWORD_FLAGS;
    globalThis.WATCHWORD_REFERENCES = WATCHWORD_REFERENCES;
    globalThis.WATCHWORD_VERSIONS = WATCHWORD_VERSIONS;

    console.log('data loaded successfully');
};


// Populate version select dropdown
async function populate_version_select() {
    await load_data();
    let _first = true;
    Object.keys(WATCHWORD_VERSIONS).forEach(version => {
        let option = document.createElement('option');
        option.value = version;
        if (_first) {
            option.selected = true;
            _first = false;
        }
        option.textContent = WATCHWORD_VERSIONS[version];
        version_select.appendChild(option);
    });
};


// Check word validity and display definition
function check_word(word) {
    console.log(`checking word: ${word}`);
    _word_is_valid = Object.keys(current_wordlist).includes(word);
    result_display.innerHTML = _word_is_valid ?
        `<p>${word} is valid in Watchword ${selected_version}</p>` :
        `<p>${word} is not valid in Watchword ${selected_version}</p>`
    ;
    if (!_word_is_valid) {
        section_definition.style.display = 'none';
        definition_text.innerHTML = '';
        section_flags.style.display = 'none';
        flags_text.innerHTML = '';
        return;
    }
    flags_text.textContent = Array.from(current_wordlist[word]).length > 0 ?
        Array.from(current_wordlist[word]).sort().join(', ') :
        '(none)'
        ;
    console.log(`flags: ${Array.from(current_wordlist[word])}`);
    section_flags.style.display = 'unset';

    _definition = find_definition(word);
    if (!_definition) {
        section_definition.style.display = 'none';
        console.log('no definition found')
        return;
    }
    console.log(`definition found: "${_definition}"`);
    definition_text.innerHTML = `<pre>${_definition}</pre>`;
    section_definition.style.display = 'unset';
};


// Various event listeners
version_form.addEventListener('submit', async (event) => {
    event.preventDefault();

    section_loading.style.display = 'unset';
    section_version.style.display = 'none';
    section_check_word.style.display = 'none';
    word_input.value = '';
    check_button.disabled = true;
    result_display.innerHTML = '';
    section_definition.style.display = 'none';
    definition_text.innerHTML = '';
    section_flags.style.display = 'none';
    flags_text.textContent = '';
    section_info.style.display = 'none';
    section_coverage.style.display = 'none';
    
    selected_version = WATCHWORD_VERSIONS[version_select.value];
    version_referenced = find_reference(selected_version);
    version_string = create_version_string(selected_version);

    loading_message.textContent = `Loading data for Watchword ${version_string}`;

    console.log(`selected version: ${selected_version}`)
    console.log(`referenced version: ${version_referenced}`)
    console.log(`version string: "${version_string}"`);

    await load_wordlist(version_referenced);

    section_loading.style.display = 'none';
    section_version.style.display = 'unset';
    section_check_word.style.display = 'unset';
    // section_coverage.style.display = 'unset';
});

word_input.addEventListener('input', async (event) => {
    event.preventDefault();
    const word = word_input.value.trim();
    if (word) {
        check_button.disabled = false;
    } else {
        check_button.disabled = true;
    }
});

check_word_form.addEventListener('submit', (event) => {
    event.preventDefault();
    _word = word_input.value.trim().toUpperCase();
    word_input.value = '';
    if (_word) {
        check_word(_word);
    }
});


// Initialise the application
async function init() {
    await populate_version_select();

    section_loading.style.display = 'none';
    section_version.style.display = 'unset';

    console.log('app initialised');
};

document.addEventListener('DOMContentLoaded', init);
