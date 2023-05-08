python -m pip install -U pip build twine
del ./dist/*.whl ./dist/*.tar.gz
python -m build
python -m twine upload -r pypi ./dist/*