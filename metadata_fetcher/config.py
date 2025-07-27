import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Custom Search Engine configuration
GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_CSE_URL = 'https://www.googleapis.com/customsearch/v1'

# Tool-specific homepages and docs as fallback
TOOL_FALLBACKS = {
    'blender': {
        'homepage': 'https://www.blender.org/',
        'documentation': 'https://docs.blender.org/manual/en/latest/',
        'support': 'https://www.blender.org/support/',
    },
    'gimp': {
        'homepage': 'https://www.gimp.org/',
        'documentation': 'https://docs.gimp.org/',
        'support': 'https://www.gimp.org/support/',
    },
    'elgato stream deck': {
        'homepage': 'https://www.elgato.com/en/stream-deck',
        'documentation': 'https://help.elgato.com/hc/en-us/categories/360002469133-Stream-Deck',
        'support': 'https://www.elgato.com/en/support',
    },
    'comfyui': {
        'homepage': 'https://github.com/comfyanonymous/ComfyUI',
        'documentation': 'https://github.com/comfyanonymous/ComfyUI/wiki',
        'support': 'https://github.com/comfyanonymous/ComfyUI/discussions',
    },
} 