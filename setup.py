#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import io
import versioneer

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(os.path.join(here, filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='esigen',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url='https://github.com/insilichem/esigen',
    author='Jaime Rodríguez-Guerra',
    author_email='jaime.rogue@gmail.com',
    description="Generate automated reports for computational chemistry calculations",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    install_requires=['cclib', 'Flask', 'flask-sslify', 'markdown', 'requests'],
    entry_points='''
        [console_scripts]
        esigen=esigen.cli:main
        esixyz=esigen.cli:esixyz
        esigenweb=esigen.web:main
        '''
)
