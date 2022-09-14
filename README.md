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

To use `pyodk`, you will first need to build a client.

Then, the library gives you two ways to interact with the Central API:
- Methods that validate parameters and provide typed results. This gives you quick, well-documented access to the most common uses of the API.
- The `.get`, `.post`, `.put`, `.patch`, `.delete` methods on a `Client` let you make direct requests to the Central API. This is useful if you need to make requests to endpoints not explicitly supported by this library or if you prefer to use the Central API documentation directly. You will need to do your own input validation, results typing and error handling.

## Initializing a client
```python
from pyodk.client import Client

client = Client()
```

The `Client` is not specific to a project, but a default `project_id` can be set by:

- A `default_project_id` in the configuration file.
- An init argument: `Client(project_id=1)`.
- A property on the client: `client.project_id = 1`.

The `Client` is specific to a configuration and cache file. These correspond to the session which the `Client` represents and encourage segregating credentials. These paths can be set by:

- Setting environment variables `PYODK_CONFIG_FILE` and `PYODK_CACHE_FILE`
- Init arguments: `Client(config_path="my_config.toml", cache_path="my_cache.toml")`.

## Library methods

There are several modules which expose methods intended to provide easy access to the most common interactions with the Central API. Some map directly to single API calls and others wrap a few calls. If you"re not finding support for some action that you need to take, see below for direct access to the API and please file an issue describing what you"d like to be able to do!

```python
from pyodk.client import Client

client = Client()
projects = client.projects.read_all()
```

Available methods on `Client`:

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

## Direct requests to the Central API

`Client` exposes methods that let you make direct calls to the Central API. These are identical to the corresponding methods in the [request library](https://requests.readthedocs.io/en/latest/api/#main-interface) except that they take in the endpoint path without the base URL and they use the configured authentication.

The method name (`.get`, `.post`, `.put`, `.patch`, `.delete`) represents the [HTTP request method](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods) of the request. In the [API docs](https://odkcentral.docs.apiary.io/), the HTTP method is specified next to the example URL.

Let's say you want to retrieve the XLSForm for a past form version. You can start by finding the API documentation [here](https://odkcentral.docs.apiary.io/#reference/forms/published-form-versions/retrieving-form-version-xls(x)). The `GET` method is specified so you will use your client"s `.get` method. You can start by pasting the desired endpoint path as a parameter:

```
r = client.get("/projects/projectId/forms/xmlFormId/versions/version.xlsx")
```

The parts of the URL that are colored in Apiary are parameters that you need to set. For example, let's say you want to access version `2011080401` of a form with the form ID `foo` in project `7` on your server, you would fill in the placeholders as follows:

```
r = client.get("/projects/7/forms/foo/versions/2011080401.xlsx")
```
The `r` variable now holds a [Response](https://requests.readthedocs.io/en/latest/api/#requests.Response) object representing the response to your request. If the request was successful, you can access the bytes of the file with `r.content` and do things like open it with [`openpyxl`](https://openpyxl.readthedocs.io/en/stable/) or write the bytes to a file.

If your request needs to specify some attributes, you can use request's [data parameter](https://requests.readthedocs.io/en/latest/api/#requests.request). 

For example, let's say you want to create a new App User with name "Lab Tech". Start by reviewing the [API docs](https://odkcentral.docs.apiary.io/#reference/accounts-and-users/app-users/creating-a-new-app-user). The `POST` method is specified so you will use your client's `.post` method. As above, you can copy the path and fill in values for the parameters:

```
r = client.post("/projects/7/app-users")
```

You also need to specify a value for the `displayName` attribute in your request:

```
r = client.post("/projects/7/app-users", data={"displayName": "Lab Tech"})
```
The `r` variable now holds a [Response](https://requests.readthedocs.io/en/latest/api/#requests.Response) object representing the response to your request. If the request was successful, you can access the response json by calling `r.json()`. You can then do things like use the `id` or `token` in additional requests.


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
