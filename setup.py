from setuptools import setup

with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='freezefrog',
    version='0.4.1',
    url='http://github.com/closeio/freezefrog',
    license='MIT',
    author='Thomas Steinacher',
    author_email='engineering@close.io',
    maintainer='Thomas Steinacher',
    maintainer_email='engineering@close.io',
    description='Datetime mocking in tests',
    long_description=long_description,
    test_suite='tests',
    platforms='any',
    install_requires=[],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
    packages=[
        'freezefrog',
    ],
)
