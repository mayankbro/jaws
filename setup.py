"""A setuptools based setup module for jaws.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages, Extension

setup(
    name="jaws",
    version='0.2.1',
    description='Software to convert idiosyncratic ASCII formats to netCDF formats',
    url='https://github.com/jaws/jaws',
    author='Ajay Saini',
    author_email='ajcse1@gmail.com',
    platforms=["any"],
    keywords=['xarray', 'netcdf', 'pandas', 'data', 'science', 'network', 'meteorology', 'climate', 'automated', 'weather', 'stations'],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent"],

    install_requires=['pandas', 'numpy', 'xarray', 'pytz', 'matplotlib', 'netcdf4']
)