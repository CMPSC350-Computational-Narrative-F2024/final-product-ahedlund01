# Story generation parameters
MIN_WORDS = 30000
MAX_WORDS = 49999
MIN_IMAGES = 30
MAX_IMAGES = 50
TOTAL_CHUNKS = 20

# Predefined scenarios
SCENARIOS = [
    {
        "setting": "Vikings in Ancient China",
        "description": "Norse warriors learning the ways of silk trading and Confucian philosophy"
    },
    {
        "setting": "Sumo Wrestlers at the Winter Olympics",
        "description": "Japanese sumo champions training for figure skating competitions"
    },
    {
        "setting": "Desert Penguins",
        "description": "Antarctic penguins starting a colony in the Sahara Desert"
    },
    {
        "setting": "Space Pirates in the Deep Sea",
        "description": "Intergalactic privateers exploring ocean trenches"
    },
    {
        "setting": "Medieval Knights in Silicon Valley",
        "description": "Arthurian knights starting a tech startup"
    }
]

# PDF generation settings
PDF_STYLES = {
    'title': {
        'fontSize': 24,
        'alignment': 1,  # Center
        'spaceAfter': 30
    },
    'subtitle': {
        'fontSize': 16,
        'alignment': 1,
        'spaceAfter': 20
    },
    'chapter': {
        'fontSize': 18,
        'alignment': 1,
        'spaceAfter': 20
    },
    'body': {
        'fontSize': 12,
        'leading': 14,
        'spaceBefore': 12,
        'spaceAfter': 12
    }
}