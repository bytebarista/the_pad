from setuptools import setup, find_packages
import sdist_upip

setup(
    name="micropython-the-pad",
    version="0.1",
    packages=find_packages(),
    cmdclass={'sdist': sdist_upip.sdist}
)