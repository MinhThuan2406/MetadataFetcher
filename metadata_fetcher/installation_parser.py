import re
from metadata_fetcher.schema import InstallationInfo
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup

def explain_when_to_use(cmd: str, method: str = "") -> Optional[str]:
    c = cmd.lower()
    if method == "pip":
        if "milvus-lite" in c:
            return "Use for the lightweight version of Milvus."
        if "bulk_writer" in c:
            return "Use when you need bulk writing support."
        if "-u" in c or "--upgrade" in c:
            return "Use to upgrade to the latest version."
        if "pymilvus" in c:
            return "Use for the main Milvus Python client."
        if c == "pip install":
            return None
        return "General pip install command."
    if method == "docker_compose":
        if "up -d" in c:
            return "Use to start all services in detached mode."
        if "down" in c:
            return "Use to stop and remove containers."
        if "invoke-webrequest" in c or "wget" in c:
            return "Use to download the official Docker Compose file."
        return None
    if method == "docker":
        if "run" in c:
            return "Use to run a container directly."
        if ".bat" in c:
            return "Use for Windows batch script installation."
        if ".sh" in c:
            return "Use for Linux/macOS shell script installation."
        return None
    return None

def explain_command(cmd: str, method: str = "") -> Tuple[str, str]:
    c = cmd.lower()
    # Python
    if c.startswith("pip install"):
        return "Install a Python package using pip.", "Run in your terminal or command prompt."
    if c.startswith("conda install"):
        return "Install a Python package using conda.", "Run in your terminal or Anaconda prompt."
    # Node.js
    if c.startswith("npm install"):
        return "Install a Node.js package using npm.", "Run in your terminal."
    if c.startswith("yarn add"):
        return "Install a Node.js package using yarn.", "Run in your terminal."
    # Java
    if "mvn install" in c or "mvn package" in c:
        return "Build or install a Java project using Maven.", "Run in your terminal."
    if "gradle build" in c or "gradle install" in c:
        return "Build or install a Java project using Gradle.", "Run in your terminal."
    # Ruby
    if c.startswith("gem install"):
        return "Install a Ruby gem.", "Run in your terminal."
    if c.startswith("bundle install"):
        return "Install Ruby dependencies using Bundler.", "Run in your terminal."
    # Go
    if c.startswith("go get") or c.startswith("go install"):
        return "Install a Go package.", "Run in your terminal."
    # Rust
    if c.startswith("cargo install"):
        return "Install a Rust package using Cargo.", "Run in your terminal."
    # System package managers
    if c.startswith("apt install") or c.startswith("apt-get install"):
        return "Install a package using apt (Debian/Ubuntu).", "Run in your Linux terminal."
    if c.startswith("yum install"):
        return "Install a package using yum (RHEL/CentOS).", "Run in your Linux terminal."
    if c.startswith("dnf install"):
        return "Install a package using dnf (Fedora).", "Run in your Linux terminal."
    if c.startswith("pacman -s"):
        return "Install a package using pacman (Arch Linux).", "Run in your Linux terminal."
    if c.startswith("zypper install"):
        return "Install a package using zypper (openSUSE).", "Run in your Linux terminal."
    if c.startswith("brew install"):
        return "Install a package using Homebrew (macOS/Linux).", "Run in your terminal."
    if c.startswith("choco install"):
        return "Install a package using Chocolatey (Windows).", "Run in Windows Command Prompt or PowerShell as administrator."
    if c.startswith("scoop install"):
        return "Install a package using Scoop (Windows).", "Run in PowerShell."
    if c.startswith("winget install"):
        return "Install a package using Winget (Windows).", "Run in Windows Command Prompt or PowerShell."
    # Docker & containers
    if c.startswith("docker run"):
        return "Run a container using Docker.", "Run in your terminal with Docker installed."
    if c.startswith("docker compose") or c.startswith("docker-compose"):
        return "Start services using Docker Compose.", "Run in your terminal with Docker Compose installed."
    if c.startswith("podman run"):
        return "Run a container using Podman.", "Run in your terminal with Podman installed."
    # Kubernetes
    if c.startswith("kubectl apply"):
        return "Apply a Kubernetes manifest.", "Run in your terminal with kubectl configured."
    if c.startswith("helm install"):
        return "Install a Helm chart on Kubernetes.", "Run in your terminal with Helm installed."
    # Source builds
    if c.startswith("git clone"):
        return "Clone a repository using git.", "Run in your terminal."
    if c.startswith("make"):
        return "Build or install using make.", "Run in your terminal."
    if c.startswith("cmake"):
        return "Configure/build using CMake.", "Run in your terminal."
    if c.startswith("python setup.py install"):
        return "Install a Python package from source.", "Run in your terminal."
    if c.endswith(".sh"):
        return "Run a shell script.", "Run in your Linux/macOS terminal. You may need to make it executable with 'chmod +x'."
    if c.endswith(".bat"):
        return "Run a batch script.", "Run in Windows Command Prompt."
    if c.endswith(".ps1"):
        return "Run a PowerShell script.", "Run in Windows PowerShell."
    # Download links
    if c.startswith("http") and (".zip" in c or ".tar.gz" in c or ".exe" in c or ".msi" in c or ".dmg" in c):
        return "Direct download link for an installer or archive.", "Download and follow platform-specific install instructions."
    # Fallback
    return "Installation command.", "Check the documentation for details or run in your terminal."

def filter_and_structure(cmds: List[str], method: str) -> List[dict]:
    seen = set()
    result = []
    for cmd in cmds:
        c = cmd.strip()
        # Filter out incomplete or generic commands
        if not c or c.lower() in ["pip install", "docker", "docker-compose", "docker compose", "docker compose", "docker-compose", "docker compose up", "docker-compose up", "docker compose down", "docker-compose down", "docker compose up -d", "docker-compose up -d", "docker compose down -v", "docker-compose down -v", "docker compose", "docker-compose", "Docker Compose"]:
            continue
        norm = c.replace(' ', '').replace('\n', '').lower()
        if norm in seen:
            continue
        seen.add(norm)
        explanation, note = explain_command(c, method)
        when_to_use = explain_when_to_use(c, method)
        entry = {"command": c, "explanation": explanation, "note": note}
        if when_to_use:
            entry["when_to_use"] = when_to_use
        result.append(entry)
    return result

def group_and_clean_docker_commands(cmds: List[dict], method: str) -> List[dict]:
    # Group by platform/use-case and deduplicate by normalized command
    unique = {}
    for entry in cmds:
        cmd = entry["command"].strip()
        # Heuristic: label platform
        if "standalone.bat" in cmd or "Invoke-WebRequest" in cmd:
            platform = "windows"
        elif "curl" in cmd or "bash standalone_embed.sh" in cmd or "$" in cmd:
            platform = "linux/macOS/WSL2"
        elif "wget" in cmd:
            platform = "linux/macOS/WSL2"
        else:
            platform = "any"
        norm = cmd.replace(' ', '').replace('\n', '').lower()
        if norm not in unique:
            entry["platform"] = platform
            unique[norm] = entry
    # Prioritize: Windows first, then Linux/macOS/WSL2, then any
    ordered = sorted(unique.values(), key=lambda x: (x["platform"] != "windows", x["platform"] != "linux/macOS/WSL2", x["platform"]))
    return ordered

def extract_multiline_install_blocks(soup: BeautifulSoup) -> dict:
    """
    Extract multi-line/script-based Docker and Docker Compose install instructions from code/pre blocks.
    Returns a dict with keys: 'docker', 'docker_compose', each a list of command dicts.
    """
    docker_cmds = []
    docker_compose_cmds = []
    # Look for code/pre blocks
    for tag in soup.find_all(['code', 'pre']):
        block = tag.get_text(separator='\n').strip()
        # Heuristics for Docker Compose blocks
        if ("docker compose" in block or "docker-compose" in block) and ("up" in block or "down" in block):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) > 1:
                # Group as a multi-step install (as a list)
                docker_compose_cmds.append({
                    "commands": lines,
                    "explanation": "Multi-step Docker Compose installation (download + up/down).",
                    "note": "Run these commands in order in your terminal or PowerShell. Make sure Docker Compose is installed.",
                    "when_to_use": "Use to set up Milvus with Docker Compose."
                })
            else:
                # Single command
                docker_compose_cmds.append({
                    "command": lines[0],
                    "explanation": "Docker Compose command.",
                    "note": "Run in your terminal with Docker Compose installed.",
                    "when_to_use": None
                })
        # Heuristics for Docker script-based blocks
        elif ("standalone.bat" in block or "standalone_embed.sh" in block or "docker run" in block):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) > 1:
                docker_cmds.append({
                    "commands": lines,
                    "explanation": "Multi-step Docker installation (script-based).",
                    "note": "Run these commands in order in your terminal or PowerShell. Make sure Docker is installed.",
                    "when_to_use": "Use to set up Milvus with Docker scripts."
                })
            else:
                docker_cmds.append({
                    "command": lines[0],
                    "explanation": "Docker command.",
                    "note": "Run in your terminal with Docker installed.",
                    "when_to_use": None
                })
    return {"docker": docker_cmds, "docker_compose": docker_compose_cmds}

def extract_installation_commands(raw_htmls: List[Optional[str]]) -> InstallationInfo:
    pip_pattern = re.compile(r'pip install[^\n\r]*', re.IGNORECASE)
    docker_run_pattern = re.compile(r'docker run[^\n\r]*', re.IGNORECASE)
    docker_pull_pattern = re.compile(r'docker pull[^\n\r]*', re.IGNORECASE)
    docker_compose_pattern = re.compile(r'(docker compose|docker-compose)[^\n\r]*', re.IGNORECASE)
    docker_block_pattern = re.compile(r'(docker[\s\S]*?)(?:\n\n|$)', re.IGNORECASE)
    git_pattern = re.compile(r'git clone[^\n\r]*', re.IGNORECASE)
    apt_pattern = re.compile(r'apt(-get)? install[^\n\r]*', re.IGNORECASE)
    yum_pattern = re.compile(r'yum install[^\n\r]*', re.IGNORECASE)
    brew_pattern = re.compile(r'brew install[^\n\r]*', re.IGNORECASE)
    choco_pattern = re.compile(r'choco install[^\n\r]*', re.IGNORECASE)
    download_pattern = re.compile(r'https?://[^\s]+\.(zip|tar\.gz|exe|msi|deb|rpm)', re.IGNORECASE)

    pip_cmds = []
    docker_cmds = []
    docker_compose_cmds = []
    from_source_cmds = []
    other_cmds = []
    platforms = {"linux": [], "macos": [], "windows": []}

    def extract_from_code_blocks(soup):
        code_texts = []
        for tag in soup.find_all(['code', 'pre']):
            code_texts.append(tag.get_text(separator='\n'))
        md_blocks = re.findall(r'```([\s\S]*?)```', soup.get_text(separator='\n'))
        code_texts.extend(md_blocks)
        return '\n'.join(code_texts)

    for raw_html in raw_htmls:
        if not raw_html:
            continue
        soup = BeautifulSoup(raw_html, 'html.parser')
        # Multi-line/script-based Docker & Compose extraction
        multi = extract_multiline_install_blocks(soup)
        docker_cmds.extend([d for d in multi["docker"]])
        docker_compose_cmds.extend([d for d in multi["docker_compose"]])
        code_text = extract_from_code_blocks(soup)
        for text in [code_text, soup.get_text(separator='\n')]:
            if not text:
                continue
            pip_cmds += pip_pattern.findall(text)
            docker_cmds += [{"command": c} for c in docker_run_pattern.findall(text) + docker_pull_pattern.findall(text)]
            docker_compose_cmds += [{"command": c} for c in docker_compose_pattern.findall(text)]
            from_source_cmds += [{"command": c} for c in git_pattern.findall(text)]
            platforms["linux"] += [m.group().strip() for m in apt_pattern.finditer(text)]
            platforms["linux"] += [m.group().strip() for m in yum_pattern.finditer(text)]
            platforms["macos"] += [m.group().strip() for m in brew_pattern.finditer(text)]
            platforms["windows"] += [m.group().strip() for m in choco_pattern.finditer(text)]
            for pattern in [apt_pattern, yum_pattern, brew_pattern, choco_pattern]:
                other_cmds += [m.group().strip() for m in pattern.finditer(text)]
            other_cmds += [m.group().strip() for m in download_pattern.finditer(text)]

    # Structure and filter
    platforms = {k: filter_and_structure(v, k) for k, v in platforms.items() if v}
    # Clean and group Docker/Docker Compose commands
    docker_cmds_clean = group_and_clean_docker_commands(docker_cmds, "docker")
    docker_compose_cmds_clean = group_and_clean_docker_commands(docker_compose_cmds, "docker_compose")
    return InstallationInfo(
        pip=filter_and_structure(pip_cmds, "pip"),
        docker=docker_cmds_clean,
        docker_compose=docker_compose_cmds_clean,
        from_source=filter_and_structure([d["command"] if isinstance(d, dict) else d for d in from_source_cmds], "from_source"),
        other=filter_and_structure(other_cmds, "other"),
        platforms=platforms if platforms else None
    ) 