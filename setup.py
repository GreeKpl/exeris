from setuptools import setup, find_packages

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

    install_requires=['sqlalchemy', 'flask', 'flask-bootstrap', 'flask-bower', 'flask-sijax', 'flask-sqlalchemy',
                      'flask-security==1.7.4', 'flask-login==0.2.11', 'pycrypto', 'geoalchemy2', 'psycopg2', 'shapely',
                      'pillow', 'markdown', 'wtforms', 'pyslate'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'flask-testing'],
    },
)
