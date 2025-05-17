from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="file-converter",
    version="1.0.0",
    author="Abdullah Khidr",
    author_email="abdullahkhidr.wrk@gmail.com",
    description="A powerful file conversion tool with modern macOS GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abdullahkhidr/file-converter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pillow>=9.0.0",
        "pdf2docx>=0.5.6",
        "markdown>=3.4.0",
        "weasyprint>=58.0",
        "pdfkit>=1.0.0",
        "PyQt6>=6.3.0",
        "python-docx>=0.8.11",
        "lxml>=4.9.0",
        "pygments>=2.13.0",
    ],
    entry_points={
        "console_scripts": [
            "file-converter=project.main:main",
        ],
    },
) 