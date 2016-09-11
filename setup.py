from setuptools import setup, find_packages

setup(
    name='exeris',
    version='0.1',

    description='exeris',
    long_description='',

    url='https://github.com/alchrabas/exeris',

    author='GreeK',
    author_email='alchrabas@exeris.org',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='game',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['sqlalchemy>=1.1.0b2', 'flask', 'flask-bootstrap', 'flask-bower', 'flask-sqlalchemy',
                      'flask-socketio', 'flask-security==1.7.4', 'flask-login==0.2.11', 'flask_redis',
                      'pycrypto', 'geoalchemy2', 'eventlet', 'bcrypt',
                      'psycopg2', 'shapely', 'pillow', 'markdown', 'wtforms', 'pyslate', 'wrapt', 'redis',
                      "pydiscourse"],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'flask-testing'],
    },
)
