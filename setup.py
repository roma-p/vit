# -*- coding: utf-8 -*-

import os
import re
import codecs
from setuptools import setup, find_packages

NAME="vit"
PACKAGES = find_packages(where="vit")
META_PATH = os.path.join("vit", "__init__.py")
HERE = os.path.abspath(os.path.dirname(__file__))

def find_meta(meta):
    meta_match = re.search(
        rf"^__{meta}__ = ['\"]([^'\"]*)['\"]", META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError(f"Unable to find __{meta}__ string.")

def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

META_FILE = read(META_PATH)

setup(
    name=find_meta("title"),
    version=find_meta("version"),
    description=find_meta("description"),
    author=find_meta("author"),
    url=find_meta("url"),
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
)
