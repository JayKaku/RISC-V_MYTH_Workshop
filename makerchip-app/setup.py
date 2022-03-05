#!/usr/bin/env python3

import os

import setuptools
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="makerchip-app",
    version="1.1.5",
    author="Redwood EDA",
    author_email="makerchip-app@redwoodeda.com",
    description="Makerchip desktop app",
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url="https://gitlab.com/rweda/makerchip-app",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers = [
        "Topic :: Text Editors :: Integrated Development Environments (IDE)",
        "License :: OSI Approved :: MIT License",
    ],
    package_data={
        'makerchip': ['asset/default.tlv']
    },
    entry_points={'console_scripts': ['makerchip=makerchip:run']},
    install_requires=['requests', 'click', 'sseclient-py'],
    python_requires='>=3.6'
)
