from setuptools import setup

setup(
    name='freezefrog',
    version='0.2',
    url='http://github.com/closeio/freezefrog',
    license='MIT',
    author='Thomas Steinacher',
    author_email='engineering@close.io',
    maintainer='Thomas Steinacher',
    maintainer_email='engineering@close.io',
    description='Efficient datetime mocking in tests',
    test_suite='tests',
    tests_require=['mock'],
    platforms='any',
    install_requires=[
        'mock',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=[
        'freezefrog',
    ],
)
