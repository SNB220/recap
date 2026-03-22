"""Setup script for Recap CLI tool."""

from setuptools import setup

setup(
    name='recap',
    version='1.0.0',
    description='Save and organize quick reference notes for tools',
    author='SNB',
    py_modules=['main', 'cli', 'db', 'config'],
    entry_points={
        'console_scripts': [
            'recap=main:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
    ],
)
