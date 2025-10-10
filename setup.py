from setuptools import setup, find_packages



setup(
    name="hyperx-htmx",
    version="3.2.9",
    author="Jeff Panasuik",
    author_email="jeff.panasuik@gmail.com",
    description="Declarative HTMX + Elementy framework for Django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/faroncoder/hyperx-htmx",
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,  # important for static/templates
    install_requires=[
        "Django>=4.2",
        "beautifulsoup4>=4.12",
        "django-bootstrap5>=23.0",
        "daphne",
        
    ],
    python_requires=">=3.10",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        # ✅ Modern Django app autodiscovery (no default_app_config needed)
        "console_scripts": [
            "hx-find = hyperx.bin.autodiscover:Command.run",
            "hx-install = hyperx.bin.cli.commands.install:main",
            "hyperx = hyperx.bin.hx_cli:main",   # ← unified CLI (this replaces hx-cli)
            "hx = hyperx.bin.cli.main:main",       # ← optional short alias
        ],
    },

    project_urls={
        "Documentation": "https://github.com/faroncoder/hyperx-htmx/wiki",
        "Source": "https://github.com/faroncoder/hyperx-htmx",
        "Tracker": "https://github.com/faroncoder/hyperx-htmx/issues",
    },
)
