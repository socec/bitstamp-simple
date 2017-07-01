from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='bitstamp-simple',
    version='1.0',
    description='A simple Bitstamp API client',
    long_description=readme,
    url='https://github.com/socec/bitstamp-simple',
    author='Igor Socec',
    author_email='igorsocec@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=['pycrypto'],
    entry_points={
            'console_scripts': [
                'bitstamp-simple=cli.bitstamp_simple:execute',
            ],
        },
)
