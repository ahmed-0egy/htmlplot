from setuptools import setup, find_packages

setup(
    name="htmlplot",
    version="0.1.0",
    description="Matplotlib-style API that renders beautiful HTML charts",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
