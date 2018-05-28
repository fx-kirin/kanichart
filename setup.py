#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name="kanichart",
    version="0.1.0",
    url="https://github.com/fx-kirin/kanichart",

    author="Yoshiaki Ono",
    author_email="ono.kirin@gmail.com",

    description="Kan i(簡易) chart. Easy plotting library.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),
    package_data={'kanichart': ['files/*']},

    install_requires=['python-highcharts', 'pandas', 'jinja2'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
