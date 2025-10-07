from setuptools import setup, find_packages

setup(
    name="hyperx-htmx",
    version="2.1.0",
    description="Declarative HTMX/TabX enhancement for Django — HyperX Middleware & Template Tags",
    author="Jeff Panasuik",
    author_email="jeff.panasuik@gmail.com",
    url="https://github.com/faroncoder/hyperx-htmx",
    license="MIT",
    packages=find_packages(include=["hyperx", "hyperx.*"]),
    install_requires=[
        "Django>=4.0",
        "beautifulsoup4>=4.10.0",
        "django-htmx"
    ],
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 5.0",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
