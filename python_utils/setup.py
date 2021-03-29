import os
import subprocess
import json
from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

version_string='0.0.28'

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='python_utils',
    description=(
        "Python Utils"
    ),
    version=version_string,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=[],
    install_requires=reqs,
    author='Tingdong Chen',
    author_email='tingdong@neva.io',
    url='https://github.com/nevaai/python_utils',
    download_url=(
        'https://github.com/nevaai/titantarball/' + version_string),
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)
