from setuptools import setup, find_packages
from codecs import open
from os import path
import ukbcohort

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
def load_readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='ukbcohort',
    version=ukbcohort.__version__,
    description='Tool to curate UKBB data',
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    url='https://github.ibm.com/isabeki/ukbcohort',
    download_url='https://github.ibm.com/isabeki/ukbcohort/tarball/' + ukbcohort.__version__,
    license='unlicense',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7.6',
        'Natural Language :: English',
        'Intended Audience :: Science/Research'
    ],
    scripts=['bin/ukbcohort'],
    entry_points={
        'console_scripts': [
            'ukbcohort_alt = ukbcohort.main:main',
        ],
    },
    keywords='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    author='Isabell Kiral',
    install_requires=[
        'sphinx >= 3.0.3',
        'sphinx_rtd_theme >= 0.4.3',
        'nose >= 1.3.7',
        'coverage >= 5.1',
        'pypi-publisher >= 0.0.4',
        'selenium >= 3.141.0',
        'pandas >= 1.0.3',
        'requests >= 2.23.0',
        'webdriver_manager >= 3.2.1'
    ],
    author_email='isa.kiral@gmail.com'
)
