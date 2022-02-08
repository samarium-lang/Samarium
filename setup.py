import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="Samarium",
    version="0.1.0",
    author="trag1c",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Tracker": "https://github.com/trag1c/Samarium/issues",
        "Source": "https://github.com/trag1c/Samarium",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "samarium=samarium:main",
        ]
    }
)
