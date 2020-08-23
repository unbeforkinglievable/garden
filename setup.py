#!/usr/bin/env python3
'''
    Garden backend
'''
import os
from setuptools import setup

HERE = os.path.dirname(__file__)
PACKAGE = 'garden_backend'

ABOUT = {}
with open(os.path.join(HERE, PACKAGE, '__about__.py')) as f:
    exec(f.read(), ABOUT)

REQS = []
with open(os.path.join(HERE, 'requirements.txt')) as f:
    for line in f:
        line = line.strip()
        if not line.startswith('#') and not line.startswith('--'):
            REQS.append(line.strip())

setup(
    name=PACKAGE,
    packages=[PACKAGE],
    install_requires=REQS,
    entry_points={
        'console_scripts': [
            'hydrometer = %s.hydrometer.main' % PACKAGE
        ]
    },
    version=ABOUT['__version__'],
    author=ABOUT['__author__'],
    maintainer=ABOUT['__maintainer__'],
    description=ABOUT['__description__'],
    include_package_data=True,
    url=ABOUT['__url__']
)
