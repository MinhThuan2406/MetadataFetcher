import pytest
# DEPRECATED: This test uses old modules that no longer exist
# from metadata.installation_parser import extract_installation_commands

def test_extract_installation_commands_various():
    html = """
    <pre>
    pip install mypackage
    docker run myimage
    git clone https://github.com/example/repo.git
    apt install mypackage
    yum install mypackage
    brew install mypackage
    choco install mypackage
    https://example.com/download/mypackage.zip
    </pre>
    """
    info = extract_installation_commands(html)
    assert info.pip == "pip install mypackage"
    assert info.docker == "docker run myimage"
    assert info.from_source == "git clone https://github.com/example/repo.git"
    assert info.other is not None  # Should catch at least one OS package manager or download link 