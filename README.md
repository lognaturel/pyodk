# pyODK

An API client for ODK Central that makes it easier to interact with data in ODK from Python.

More details on the goals and implementation plans [are here](https://docs.google.com/document/d/1AamUcvO4R7VzphToIfeMhCjWEjxjbpVQ_DJR89FlpRc/edit).


# Install

The currently supported Python version for `pyodk` is 3.8.


## From pip

```
pip install pyodk
```


## From source

```
# Get a copy of the repository.
mkdir -P ~/repos/pyodk
cd ~/repos/pyodk
git clone https://github.com/getodk/pyodk.git repo

# Create and activate a virtual environment for the install.
/usr/local/bin/python3.8 -m venv venv
source venv/bin/activate

# Install pyodk and it's production dependencies.
cd ~/repos/pyodk/repo
pip install -e .

# Leave the virtualenv.
deactivate
```


# Configuration


## Main configuration file

The main configuration file uses the TOML format. The default file name is `.pyodk_config.toml`, and the default location is the user home directory. The file name and location can be customised by setting the environment variable `PYODK_CONFIG_FILE` to some other file path, or by passing the path at init with `Client(config_path="my_config.toml")`. The expected file structure is as follows:

```
[central]
base_url = "https://www.example.com"
username = "my_user"
password = "my_password"
default_project_id = 123
```


## Session cache file

The session cache file uses the TOML format. The default file name is `.pyodk_cache.toml`, and the default location is the user home directory. The file name and location can be customised by setting the environment variable `PYODK_CACHE_FILE` to some other file path, or by passing the path at init with `Client(config_path="my_cache.toml")`. This file should not be pre-created as it is used to store a session token after login.


# Usage


## Example

It's possible to interact with the API using a direct or a fluent style, as shown below.

```python
from pyodk.client import Client


# Direct style, using objects from the Client and providing parameters.
with Client() as client:
    projects = client.projects.read_all()
    forms = client.forms.read_all()
    submissions = client.submissions.read_all(form_id=next(forms).xmlFormId)
    form_data = client.submissions.read_all_table(form_id="birds", project_id=8)

# Fluent style, using chained methods on the result objects.
with Client() as client:
    meta = client.projects.read(8).m.forms.read("birds")
    # Result is a pydantic model, so you can use `meta.dict()` or `meta.json()`.
    data = client.projects.read(8).m.forms.read("birds").m.submissions.read_all_table()
    # Result is a dict for now, but will be a pydantic model later.
```

The `Client` is not specific to a project, but a default `project_id` can be set by:

- A `default_project_id` in the configuration file.
- An init argument: `Client(project_id=1)`.
- A property on the client: `client.project_id = 1`.

The `Client` is specific to a configuration and cache file. These approximately correspond to the session which the `Client` represents; it also encourages segregating credentials. These paths can be set by:

- Setting environment variables `PYODK_CONFIG_FILE` and `PYODK_CACHE_FILE`
- Init arguments: `Client(config_path="my_config.toml", cache_path="my_cache.toml")`.


## Endpoints

Available endpoints on `Client`:

- Projects
  - read
  - read_all
- Forms
  - read
  - read_all
  - read_odata_metadata
- Submissions
  - read
  - read_all
  - read_all_table

A detailed listing of current and planned endpoint mappings is in `docs/api_index.csv`.


## Logging

Errors and other messages are logged to a standard library `logging` logger in the `pyodk` namespace / hierarchy (e.g `pyodk.config`, `pyodk.endpoints.auth`, etc.). The logs can be manipulated from an application as follows.

```python
import logging


# Initialise an example basic logging config (writes to stdout/stderr).
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

# Get a reference to the pyodk logger.
pyodk_log = logging.getLogger("pyodk")

# Receive everything DEBUG level and higher.
pyodk_log.setLevel(logging.DEBUG)
pyodk_log.propagate = True

# Ignore everything below FATAL level.
pyodk_log.setLevel(logging.FATAL)
pyodk_log.propagate = False
```


# Development

Install the source files as described above, then:

```
pip install -r dev_requirements.pip
```

You can run tests with:

```
nosetests
```

On Windows, use:

```
nosetests -v -v --traverse-namespace ./tests
```


# Releases

1. Run all linting and tests.
2. Draft a new GitHub release with the list of merged PRs.
3. Checkout a release branch from latest upstream master.
4. Update `CHANGES.md` with the text of the draft release.
5. Update `pyodk/__init__.py` with the new release version number.
6. Commit, push the branch, and initiate a pull request. Wait for tests to pass, then merge the PR.
7. Tag the release and it will automatically be published (see `release.yml` actions file).
