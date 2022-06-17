Node.js PyPI distribution
=====================

[Node.js][nodejs] is an open-source, cross-platform, back-end JavaScript runtime environment that runs on the V8 engine and executes JavaScript code outside a web browser. 

**Note: this is an unofficial Node.js distribution.**

The [nodejs-bin][pypi] Python package redistributes Node.js so that it can be used as a dependency of Python projects.

**This is intended for use within Python virtual environments and containers, it should probably not be used for global instillation.**

This PyPI distribution is provided by <https://github.com/samwillis/nodejs-pypi>.

[nodejs]: https://nodejs.org/
[pypi]: https://pypi.org/project/nodejs-bin/

Usage
-----

To install:

```shell
pip install nodejs-bin
```

To run Node.js from the command line, use:

```shell
python -m nodejs
# or (see below)
node
```

`npm` and `npx` are also available as `python -m nodejs.npm` and `python -m nodejs.npx`.

To run Node.js from a Python program:

```python
from nodejs import node, npm, npm

# Run Node.js and return the exit code.
node.run(['script.js', 'arg1', ...])

# Run npm and return the exit code.
npm.run(['command', 'arg1', ...])

# Run npx and return the exit code.
npx.run(['command', 'arg1', ...])
```

Alternatively use `sys.executable` to locate the Python binary to invoke. For example:

```python
import sys, subprocess

subprocess.call([sys.executable, "-m", "nodejs"])
```

Additionally, the standard `node`, `npm` and `npx` commands are also added to your Python environment's `bin` directory. This is usually on your `PATH` and so they should be available in your shell environment.

License
-------

The [Node.js license](https://raw.githubusercontent.com/nodejs/node/master/LICENSE).