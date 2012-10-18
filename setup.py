# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '1.0'
description = "A collection of helper methods and functions for use among \
Open Multimedia projects."
long_description = open("README.txt").read() + "\n" + \
                   open(os.path.join("docs", "INSTALL.txt")).read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='openmultimedia.utils',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
#        "Framework :: Plone :: 4.3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Office/Business :: News/Diary",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Hector Velarde',
      author_email='hector.velarde@gmail.com',
      url='https://github.com/OpenMultimedia/openmultimedia.utils',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['openmultimedia', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.CMFPlone>=4.2',
        'five.grok',
        'plone.app.jquery==1.7.2',
        'plone.principalsource',
        ],
      extras_require={
        'test': ['plone.app.testing']
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
