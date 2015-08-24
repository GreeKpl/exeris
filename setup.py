from setuptools import setup, find_packages
from os import path

setup(
    name='exeris',
    version='0.1',

    description='exeris',
    long_description='',

    url='https://github.com/GreeKpl',

    author='GreeK',
    author_email='grkalk@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='game',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['sqlalchemy', 'flask', 'flask-sqlalchemy', 'geoalchemy2', 'psycopg2', 'shapely', 'pillow',
                      'wtforms'],

    extras_require = {
        'dev': ['check-manifest'],
        'test': ['coverage', 'flask-testing'],
    },
)
