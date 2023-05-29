"""Publishes the package on PyPI."""
__license__ = 'MIT'

from subprocess import run
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent

if 'test' in sys.argv:
    process = run(['flit', 'publish', '--format', 'wheel', '--repository', 'testpypi'], cwd=root)
else:
    process = run(['flit', 'publish', '--format', 'wheel'], cwd=root)

if process.returncode:
    raise RuntimeError('Error while publishing on PyPI.')
