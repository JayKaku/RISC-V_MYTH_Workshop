# Instructions for PyPI

These instructions are based on these [lengthy instructions](https://packaging.python.org/guides/distributing-packages-using-setuptools/) and undoubtedly missed something. The "lengthy instructions" include creating the project files, which is already done.

### One Time

```
pip3 install twine
pip3 install wheel
```

Get an account and have permissions to https://pypi.org/user/redwoodeda/.
Create an [API token](https://pypi.org/help/#apitoken).

Create `$home/.pypirc` on a system without prying eyes, containing:

```
[pypi]
username = __token__
password = <the token value, including the `pypi-` prefix>
```

### Create and Upload New Version

Update version # in `setup.py`.

From the top-level repo directory:

```
python3 setup.py sdist bdist_wheel
```

To upload to Test PyPI:
```
python3 -m twine upload --repository testpypi dist/*
```

To upload to the production PyPI:

```
twine upload dist/*
```

After a minute, visit: `https://pypi.org/project/makerchip-app` to confirm, and try to install using:

```
pip3 install makerchip-app==<version #>
```

And test.
