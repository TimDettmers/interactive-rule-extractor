import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "interactive-rule-extractor",
    version = "0.0.1",
    author = "Tim Dettmers",
    author_email = "tim.dettmers@gmail.com",
    description = ("Use a lucene index to interactively design extraction rules for knowledge graphs."),
    license = "GNU",
    keywords = "bash",
    url = "http://packages.python.org/interactive-rule-extractor",
    packages=['ruleextractor', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Topic :: NLP",
    ],
)

