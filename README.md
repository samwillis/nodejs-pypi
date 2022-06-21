Node.js PyPI distribution
=====================

[Node.js][nodejs] is an open-source, cross-platform, back-end JavaScript runtime environment that runs on the V8 engine and executes JavaScript code outside a web browser. 

The [nodejs-bin][pypi] Python package redistributes Node.js so that it can be used as a dependency of Python projects. With `nodejs-bin` you can call `nodejs`, `npm` and `npx` from both the [command line](#command-line-usage) and a [Python API](#python-api-usage).

**Note: this is an unofficial Node.js distribution.**

**This is intended for use within Python virtual environments and containers, it should probably not be used for global instillation.**

This PyPI distribution is provided by <https://github.com/samwillis/nodejs-pypi>.

[nodejs]: https://nodejs.org/
[pypi]: https://pypi.org/project/nodejs-bin/

Install
-------

To install:

```shell
pip install nodejs-bin
```

You can specify the Node.js version to install with:

```shell
pip install nodejs-bin==<version>

# Example:
pip install nodejs-bin==16.15.1
```

Command Line Usage
------------------

To run Node.js from the command line, use:

```shell
python -m nodejs
# or (see below)
node
```

`npm` and `npx` are also available as `python -m nodejs.npm` and `python -m nodejs.npx`.

Additionally, the standard `node`, `npm` and `npx` commands are also added to your Python environment's `bin` directory. This is usually on your `PATH` and so they should be available in your shell environment.

Python API Usage
----------------

`node-bin` has a simple Python API that wraps the Node.js command line with the [Python `subprocess`](https://docs.python.org/3/library/subprocess.html).

For `node`, `npm` and `npx` there are `.call()`, `.run()` and `.Popen()` methods that match the equivalent `subprocess` methods.

To run Node.js from a Python program and return the exit code:

```python
from nodejs import node, npm, npx

# Run Node.js and return the exit code.
node.call(['script.js', 'arg1', ...], **kwargs)

# Run npm and return the exit code.
npm.call(['command', 'arg1', ...], **kwargs)

# Run npx and return the exit code.
npx.call(['command', 'arg1', ...], **kwargs)
```

The `call(args, **kwargs)` functions wrap [`subprocess.call()`](https://docs.python.org/3/library/subprocess.html#subprocess.call), passes though all `kwargs` and returns the exit code of the process.

To run Node.js from a Python program and return a [CompletedProcess](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess) object:

```python
from nodejs import node, npm, npx

# Run Node.js and return the exit code.
node.run(['script.js', 'arg1', ...], **kwargs)

# Run npm and return the exit code.
npm.run(['command', 'arg1', ...], **kwargs)

# Run npx and return the exit code.
npx.run(['command', 'arg1', ...], **kwargs)
```

The `run(args, **kwargs)` functions wrap [`subprocess.run()`](https://docs.python.org/3/library/subprocess.html#subprocess.run), passes though all `kwargs` and returns a `CompletedProcess`.

Additionally, to start a Node.js process and return a `subprocess.Popen` object, you can use the `Popen(args, **kwargs)` functions:

```python
from nodejs import node, npm, npx

# Start Node.js and return the Popen object.
node_process = node.Popen(['script.js', 'arg1', ...], **kwargs)

# Start npm and return the Popen object.
npm_process = npm.Popen(['command', 'arg1', ...], **kwargs)

# Start npx and return the Popen object.
npx_process = npx.Popen(['command', 'arg1', ...], **kwargs)
```

The `Popen(args, **kwargs)` functions wrap [`subprocess.Popen()`](https://docs.python.org/3/library/subprocess.html#subprocess.Popen), passes though all `kwargs` and returns a [`Popen` object](https://docs.python.org/3/library/subprocess.html#popen-objects).

The `nodejs.node` api is also available as `nodejs.run` and `nodejs.call` and `nodejs.Popen`.

Finally, there are a number of convenient attributes on the `nodejs` module:

  * `nodejs.node_version`: the version of Node.js that is installed.
  * `nodejs.path`: the path to the Node.js executable.


License
-------

The [Node.js license](https://raw.githubusercontent.com/nodejs/node/master/LICENSE).