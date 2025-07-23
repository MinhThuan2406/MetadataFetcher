import re
from metadata_fetcher.schema import InstallationInfo
from typing import Optional
from bs4 import BeautifulSoup

def extract_installation_commands(raw_html: Optional[str]) -> InstallationInfo:
    """
    Extract installation commands from raw HTML or plain text.
    Looks for pip, docker, git clone, OS package managers, and download links.
    Returns an InstallationInfo object.
    """
    if not raw_html:
        return InstallationInfo()
    soup = BeautifulSoup(raw_html, 'html.parser')
    text = soup.get_text(separator='\n')
    pip_cmd = None
    docker_cmd = None
    from_source_cmd = None
    other_cmd = None
    # Regex patterns
    pip_pattern = re.compile(r'pip install[^\n\r]*', re.IGNORECASE)
    docker_pattern = re.compile(r'docker run[^\n\r]*', re.IGNORECASE)
    git_pattern = re.compile(r'git clone[^\n\r]*', re.IGNORECASE)
    apt_pattern = re.compile(r'apt(-get)? install[^\n\r]*', re.IGNORECASE)
    yum_pattern = re.compile(r'yum install[^\n\r]*', re.IGNORECASE)
    brew_pattern = re.compile(r'brew install[^\n\r]*', re.IGNORECASE)
    choco_pattern = re.compile(r'choco install[^\n\r]*', re.IGNORECASE)
    # Download link pattern (simple)
    download_pattern = re.compile(r'https?://[^\s]+\.(zip|tar\.gz|exe|msi|deb|rpm)', re.IGNORECASE)
    # Search for commands
    pip_match = pip_pattern.search(text)
    if pip_match:
        pip_cmd = pip_match.group().strip()
    docker_match = docker_pattern.search(text)
    if docker_match:
        docker_cmd = docker_match.group().strip()
    git_match = git_pattern.search(text)
    if git_match:
        from_source_cmd = git_match.group().strip()
    # OS package managers
    for pattern in [apt_pattern, yum_pattern, brew_pattern, choco_pattern]:
        match = pattern.search(text)
        if match:
            other_cmd = match.group().strip()
            break
    # Download links
    download_match = download_pattern.search(text)
    if download_match:
        other_cmd = download_match.group().strip()
    # Fallback: look for any shell command block
    code_blocks = re.findall(r'\$\s*([\w\-]+ .+)', text)
    if not (pip_cmd or docker_cmd or from_source_cmd or other_cmd) and code_blocks:
        other_cmd = code_blocks[0].strip()
    return InstallationInfo(
        pip=pip_cmd,
        docker=docker_cmd,
        from_source=from_source_cmd,
        other=other_cmd
    ) 