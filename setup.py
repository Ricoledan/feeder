"""Setup configuration for the Feeder package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="feeder",
    version="1.0.0",
    author="Ricardo Ledan",
    author_email="your.email@example.com",
    description="A command-line tool to extract articles from Feedly feeds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ricoledan/feeder",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "feeder=feedly_extractor.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)