import os
from setuptools import setup

# distutils/hardlinks workaround:
# http://bugs.python.org/issue8876#msg208792
# https://www.virtualbox.org/ticket/818
if os.path.abspath(__file__).split(os.path.sep)[1] == 'vagrant':
    del os.link


setup(
    name='anires_www',
    version='0.1',
    description='WWW server app for Animal Rescue Poland',
    url='https://github.com/lhaze/anires_www',
    author='lhaze',
    author_email='lhaze@lhaze.name',
    package_dir={'': 'anires'},
)
