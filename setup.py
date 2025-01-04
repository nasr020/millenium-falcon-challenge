from setuptools import setup, find_packages

setup(
    name="millennium-falcon-odds",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "give-me-the-odds = src.cli.cli:main",
        ],
    },
)
