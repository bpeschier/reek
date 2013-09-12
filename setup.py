from setuptools import setup, find_packages
import os

try:
    from setuptest import test
except ImportError:
    from setuptools.command.test import test

version = __import__('reek').__version__


def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="reek",
    version=version,
    url='http://github.com/bpeschier/reek',
    license='MIT',
    platforms=['OS Independent'],
    description="A set of basic tools for building a content management platform using the Django web framework ",
    long_description=read('README.md'),
    author='Bas Peschier',
    author_email='bas.peschier@gmail.com',
    packages=find_packages(),
    install_requires=(
        'Django>=1.5',
    ),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)