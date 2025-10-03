"""Setup configuration for TradingSuite package"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tradingsuite",
    version="1.0.0",
    author="TradingSuite Development Team",
    description="A comprehensive trading analysis package with TradingView data integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/TradingSuite",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.19.0",
        "plotly>=5.0.0",
        "requests>=2.26.0",
        "cloudscraper>=1.2.58",
        "pandas-ta>=0.3.14b0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)
