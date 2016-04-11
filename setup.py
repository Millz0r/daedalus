#! /usr/bin/env python2
import os
import subprocess

from setuptools import setup, find_packages
from codecs import open

if os.path.exists("git"):
    version_git = subprocess.check_output(['git', 'describe', '--always'])
else:
    # TODO come up with a version
    version_git = "todo"

requirements = [
    'coverage',
    'cryptography',
    'cyclone',
    'inflection',
    'kombu',
    'mock',
    'nose',
    'numpy',
    'openpyxl',
    'pandas',
    'pylint',
    'pyopenssl',
    'python-etcd',
    'pyyaml',
    'requests',
    'scipy',
    'setuptools-lint',
    'twisted',
    'xlrd',
    'bcrypt',
    'alembic',
    'psycopg2',
    'sqlalchemy',
]

setup(
    name='daedalus',
    version=('%s' % version_git),
    description='The data analytics platform for property pricing algorithms',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7'
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'frontend.service = daedalus.frontend.service:main',
            'scheduler.service = daedalus.scheduler.service:main',
            'transform.service = daedalus.xlstransform.service:main',
            'valuate.service = daedalus.valuation.service:main',
            'tapevalidation.service = daedalus.validation.service:main',
            'xlstransform = daedalus.xlstransform.application:main',
            'tapevalidation = daedalus.validation.application:main',
        ]
    },
    test_suite='tests'
)
