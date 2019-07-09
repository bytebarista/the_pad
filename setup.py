import sys
from setuptools import setup, find_packages
import sdist_upip

setup(name='micropython-the-pad',
      #use_scm_version=True,
      #setup_requires=['setuptools_scm'],
      description='Modules and demos for the pad',
      long_description="Modules and demos for the pad",
      url='https://github.com/bytebarista/the_pad',
      author='ByteBarista',
      license='MIT',
      cmdclass={'sdist': sdist_upip.sdist},
      version="1.0.6",
      py_modules=[]
      #packages=find_packages(),
      #py_modules=['the_pad/boot.py'])
      )