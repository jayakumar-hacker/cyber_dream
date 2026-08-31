"""
Minimal packaging setup for CyberDreamer.

Installs the project in editable mode:

    pip install -e .

so that `import src.pipeline...`, `import src.core...`, etc. resolve
correctly from anywhere (including tests/) without path hacks.

Dependencies are intentionally NOT duplicated here; install them via
`pip install -r requirements.txt` first (or alongside).
"""

from setuptools import find_packages, setup

setup(
    name="cyberdreamer",
    version="0.1.0",
    description="Graph-RSSM World Model for Predictive Cyber Defense (research prototype).",
    author="CyberDreamer Team",
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.10",
    include_package_data=True,
)
