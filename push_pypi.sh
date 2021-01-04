rm -rf build dist 
python setup.py sdist bdist_wheel
#twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# twine upload dist/*
twine check dist/*
twine upload --repository pypi dist/*
