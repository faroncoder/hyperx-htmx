from setuptools import setup, find_packages



setup(
    name="hyperx-htmx",
    version="3.2.10",
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
        "jq>=1.3.0",
        "django-htmx>=1.9.2",
        "asgiref>=3.6.0",
        "colorama>=0.4.6",
        "python-decouple>=1.0.4",
        "celery>=5.4.0",
        "redis>=4.5.1",
        "flower>=1.0.0",
        "playwright>=1.37.0",
        "python-json-logger>=2.0.7",
        "django-celery-beat",
        "celery[redis]",
        "httpx",
        "requests",
        "rich",
        "platformdirs",
        "responses",
        
    ],
    python_requires=">=3.12",
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
            "hx-find = hyperx.bin.cli.utils.autodiscover:main",
            # "hx-install = hyperx.bin.cli.installer:core_install_hyperx:Command:run",
            "hx = hyperx.bin.cli.hx:main", 
            "hx-env = hyperx.bin.cli.logger.setenv:main",
            # "hx-reactjs = hyperx.bin.cli.commands.reactjs:main",
            # "hx-reactjs-worker = hyperx.bin.cli.commands.celery_worker:main",
            # "hx-reactjs-flower = hyperx.bin.cli.commands.celery_flower:main",
            # "hx-reactjs-beat = hyperx.bin.cli.commands.celery_beat:main"
        ],
    },

    project_urls={
        "Documentation": "https://github.com/faroncoder/hyperx-htmx/wiki",
        "Source": "https://github.com/faroncoder/hyperx-htmx",
        "Tracker": "https://github.com/faroncoder/hyperx-htmx/issues",
    },
)
