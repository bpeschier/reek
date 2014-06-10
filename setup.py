from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='reek',
    version='0.1.0a1',
    url='http://github.com/bpeschier/reek',
    author='Bas Peschier',
    author_email='bas.peschier@gmail.com',
    packages=['urlconf', 'admin', 'restructuredfield'],
    license='MIT',
    long_description=long_description,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django>=1.7',
    ],
)

