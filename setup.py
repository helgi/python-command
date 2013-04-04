#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import join, dirname


def read(fname):
    return open(join(dirname(__file__), fname)).read()

PKG = 'Command'
VERSION = '0.1.0'

setup(
    name=PKG,
    version=VERSION,
    description="Command runner with debug capabilities",
    long_description=read('README.rst'),
    author="Helgi Þorbjörnsson",
    author_email="helgi@php.net",
    url="http://github.com/helgi/python-command",
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    platforms=['any'],
    install_requires=['setuptools'],
    license="MIT License",
    keywords="subprocess,command",
    zip_safe=True,
    test_suite="tests",
    tests_require=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ]
)
