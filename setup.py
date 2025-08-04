from setuptools import setup, find_packages

setup(
    name="EcuCalSrecA2L",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'a2lparser',
        'hexformat',
        'pandas>=2.0.0',
        'openpyxl>=3.0.0',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python utility for ECU calibration using SREC and A2L files",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/EcuCalSrecA2L",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)