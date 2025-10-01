"""
🚀 HyperX - HTMX's Sidekick ⚡
Setup configuration for PyPI package
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hyperx-htmx",
    version="1.1.2",
    author="Faron",
    author_email="jpanasuik@gmail.com",
    description="🚀 HyperX - HTMX's Sidekick ⚡ TabX so fast! Lightning-fast HTMX enhancement protocol for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/faroncoder/hyperx-htmx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.0",
        "django-htmx>=1.0",
    ],
    keywords="htmx django tabx hyperx web development ajax",
)
