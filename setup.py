#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目安装脚本
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="disttest",
    version="0.1.0",
    author="DistTest Team",
    author_email="disttest@example.com",
    description="基于Python的分布式自动化测试框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/disttest/disttest",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pytest>=7.0.0",
        "requests>=2.28.0",
        "jinja2>=3.0.0",
        "pyyaml>=6.0.0",
        "marshmallow>=3.0.0",
        "psutil>=5.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "disttest=disttest.cli:main",
        ],
    },
    include_package_data=True,
) 