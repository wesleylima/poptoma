import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="poptoma",
    version="0.0.1",
    author="Wesley Lima",
    author_email="wesley@wesleylima.com",
    description="A Python API for Optoma Projectors with web Admin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wesleylima/poptoma",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
