import requests
from bs4 import BeautifulSoup, Tag
from typing import Dict, Optional
import re
import os
from urllib.parse import urlparse
from metadata_fetcher.config import TOOL_FALLBACKS

# TODO: Add more creative/media tools and improve extraction heuristics

BLENDER_CURATED = {
    'Description': 'Blender is a free and open-source 3D creation suite supporting the entirety of the 3D pipeline: modeling, rigging, animation, simulation, rendering, compositing, motion tracking, video editing, and 2D animation.',
    'Key Features': [
        'Cycles Render Engine',
        'Real-time viewport preview',
        'CPU & GPU rendering',
        'PBR shaders & HDR lighting support',
        'Modeling, Sculpt, UV',
        'Advanced sculpting tools and brushes',
        'Multi-resolution and Dynamic subdivision',
        '3D painting with textured brushes and masking',
        'Python scripting for custom tools and add-ons',
        'VFX: camera and object tracking',
        'Animation & Rigging',
        'Story Art, Drawing 2D in 3D',
        'Customizable interface',
        'Add-on ecosystem',
        'VR rendering support',
    ],
    'Versions': '4.5 LTS (latest), Experimental Builds',
    'Compatibility': 'Windows, macOS, Linux',
}

# Curated values for GIMP
GIMP_CURATED = {
    'License': 'GNU General Public License (GPL)',
    'Programming Language': 'C, Python (for plugins)',
    'Supported File Formats': '.xcf, .psd, .png, .jpg, .jpeg, .bmp, .gif, .tiff, .heif, .raw, .svg, .pdf, .webp, .ico, .emf, .wmf, .mng, .pcx, .tga, .xcfbz2, .xcf.gz',
    'System Requirements': 'Windows 7/8/10/11, macOS 10.12+, Linux; 2GB RAM (4GB recommended); 200MB disk space; 1280x768 display',
}

# Curated values for Elgato Stream Deck
ELGATO_CURATED = {
    'License': 'Proprietary',
    'Programming Language': 'C++, C# (for plugins)',
    'Supported File Formats': 'N/A (uses proprietary plugin format, supports images: .jpg, .png, .gif, audio: .mp3, .wav)',
    'System Requirements': 'Windows 10 (64-bit) or later, macOS 10.15 or later; USB 2.0 port; Internet connection for setup',
}

# Curated values for ComfyUI
COMFYUI_CURATED = {
    'License': 'GNU General Public License (GPL)',
    'Programming Language': 'Python',
    'Supported File Formats': '.ckpt, .safetensors, .json, .png, .webp, .flac',
    'System Requirements': 'Windows, macOS, Linux; NVIDIA GPU recommended for acceleration; Python 3.8+; 8GB RAM (16GB+ recommended)',
}


def fetch_creative_media_metadata(tool_name: str) -> Dict:
    """Fetch metadata for a creative/media tool, using curated fallbacks and heuristics."""
    tool_key = tool_name.strip().lower()
    fallbacks = TOOL_FALLBACKS.get(tool_key, {})
    homepage = fallbacks.get('homepage')
    documentation = fallbacks.get('documentation')
    support = fallbacks.get('support')
    # General Info
    info = {
        'Name': tool_name,
        'Type': 'software',
        'Description': 'N/A',
        'Official Site': homepage or 'N/A',
    }
    # Product Details
    details = {
        'Versions': 'N/A',
        'Compatibility': 'N/A',
    }
    # Key Features
    key_features = 'N/A'
    # Installation & Documentation
    # Unify: Always show labeled Installation and Documentation links for all tools
    installation = (
        f"Installation: {homepage if homepage else 'N/A'}\n"
        f"Documentation: {documentation if documentation else 'N/A'}"
    )
    # Support/Reviews
    support_reviews = support or 'N/A'

    # License and Latest Release Date (new fields)
    license_info = 'N/A'
    latest_release_date = 'N/A'
    # Programming Language, Supported File Formats, System Requirements (new fields)
    programming_language = 'N/A'
    supported_file_formats = 'N/A'
    system_requirements = 'N/A'
    # --- Blender special logic ---
    if tool_key == 'blender':
        # Section 3: Key Features - always use curated list
        key_features = ', '.join(BLENDER_CURATED['Key Features'])
        # Section 2: Versions - try to extract latest stable version only (plain text, no HTML)
        try:
            download_url = 'https://www.blender.org/download/'
            res = requests.get(download_url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Find all text nodes that match 'Blender X.Y LTS' and are not inside <a> or <span> etc.
                version_text = None
                for text in soup.stripped_strings:
                    match = re.match(r'Blender\s*[\d\.]+\s*LTS', text, re.IGNORECASE)
                    if match:
                        version_text = match.group(0).strip()
                        break
                if version_text:
                    details['Versions'] = version_text
        except Exception:
            pass
        # Fallback to curated if still missing
        if info['Description'] == 'N/A':
            info['Description'] = BLENDER_CURATED['Description']
        if not details['Versions'] or details['Versions'] == 'N/A':
            details['Versions'] = BLENDER_CURATED['Versions']
        if details['Compatibility'] == 'N/A':
            details['Compatibility'] = BLENDER_CURATED['Compatibility']
        # Section 4: Installation & Documentation - labeled links (Blender-specific download link)
        installation = (
            f"Installation: https://www.blender.org/download/\n"
            f"Documentation: {BLENDER_CURATED.get('Documentation', 'https://docs.blender.org/manual/en/latest/') if BLENDER_CURATED.get('Documentation') else 'https://docs.blender.org/manual/en/latest/'}"
        )
        # License (curated)
        license_info = 'GNU General Public License (GPL)'
        # Latest Release Date (try to extract from download page)
        try:
            download_url = 'https://www.blender.org/download/'
            res = requests.get(download_url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Look for a date string near the version info
                for text in soup.stripped_strings:
                    if re.match(r'Blender\s*[\d\.]+\s*LTS', text, re.IGNORECASE):
                        # Try to find a date in the next few strings
                        siblings = list(soup.stripped_strings)
                        idx = siblings.index(text)
                        for lookahead in range(1, 5):
                            if idx + lookahead < len(siblings):
                                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', siblings[idx + lookahead])
                                if date_match:
                                    latest_release_date = date_match.group(1)
                                    break
                        break
        except Exception:
            pass
        # Programming Language (curated)
        programming_language = 'C, C++, Python'
        # Supported File Formats (curated)
        supported_file_formats = '.blend, .obj, .fbx, .gltf, .dae, .abc, .usd, .stl, .ply, .3ds, .x3d, .svg, .dxf, .png, .jpg, .tiff, .exr, .mp4, .avi, .mov, .wav, .ogg, .flac, .mp3'
        # System Requirements (curated)
        system_requirements = 'Windows 8.1/10/11, macOS 10.13+, Linux; 8GB RAM (16GB recommended); OpenGL 4.3+ compatible GPU'
    elif tool_key == 'gimp':
        # Programming Language (curated)
        programming_language = GIMP_CURATED['Programming Language']
        # Supported File Formats (curated)
        supported_file_formats = GIMP_CURATED['Supported File Formats']
        # System Requirements (curated)
        system_requirements = GIMP_CURATED['System Requirements']
        # License (curated)
        license_info = GIMP_CURATED['License']
        # Placeholder for future extraction logic (e.g., parse homepage for more info)
        # TODO: Add extraction logic for more fields if needed
    elif tool_key == 'elgato stream deck':
        programming_language = ELGATO_CURATED['Programming Language']
        supported_file_formats = ELGATO_CURATED['Supported File Formats']
        system_requirements = ELGATO_CURATED['System Requirements']
        license_info = ELGATO_CURATED['License']
        # Placeholder for future extraction logic
    elif tool_key == 'comfyui':
        info['Description'] = "ComfyUI is a powerful and modular stable diffusion GUI and backend, designed for flexibility and extensibility."
        # Supplement with YAML-based description if available
        try:
            import yaml
            with open("tool_descriptions.yaml", "r", encoding="utf-8") as f:
                tool_descriptions = yaml.safe_load(f)
            if 'comfyui' in tool_descriptions and tool_descriptions['comfyui'].get('description'):
                info['Description'] = tool_descriptions['comfyui']['description']
        except Exception as e:
            print(f"[WARN] Could not load tool_descriptions.yaml for ComfyUI: {e}")
        info['Official Site'] = "https://github.com/comfyanonymous/ComfyUI"
        details['Versions'] = "See GitHub releases"
        programming_language = COMFYUI_CURATED['Programming Language']
        supported_file_formats = COMFYUI_CURATED['Supported File Formats']
        system_requirements = COMFYUI_CURATED['System Requirements']
        license_info = COMFYUI_CURATED['License']
        # Placeholder for future extraction logic
    else:
        # Try to fetch homepage and parse info (generic logic)
        if homepage:
            try:
                res = requests.get(homepage, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # Description
                    desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    if desc_tag and isinstance(desc_tag, Tag) and desc_tag.has_attr('content'):
                        info['Description'] = str(desc_tag['content'])
                    # Key Features (look for feature sections or lists)
                    features = []
                    for h2 in soup.find_all(['h2', 'h3']):
                        if isinstance(h2, Tag):
                            if 'feature' in h2.get_text(strip=True).lower() or 'everything you need' in h2.get_text(strip=True).lower():
                                ul = h2.find_next('ul')
                                if ul and isinstance(ul, Tag):
                                    features.extend([li.get_text(strip=True) for li in ul.find_all('li')])
                    if features:
                        key_features = ', '.join(sorted(set(features)))
                    # TODO: Parse versions, compatibility, installation, support, etc.
            except Exception:
                pass
    # Fallback: Use known documentation/support links if not found
    if not documentation:
        documentation = fallbacks.get('documentation', 'N/A')
    if not support:
        support = fallbacks.get('support', 'N/A')
    # Compose output
    return {
        'General Information': info,
        'Product Details': details,
        'Key Features': key_features,
        'Installation & Documentation': installation,
        'Support/Reviews': support_reviews,
        'License': license_info,
        'Latest Release Date': latest_release_date,
        'Programming Language': programming_language,
        'Supported File Formats': supported_file_formats,
        'System Requirements': system_requirements,
    }

# For quick testing
if __name__ == '__main__':
    for tool in TOOL_FALLBACKS.keys():
        print(f"\n=== {tool.title()} ===")
        meta = fetch_creative_media_metadata(tool)
        for section, content in meta.items():
            print(f"\n{section}:")
            print(content) 