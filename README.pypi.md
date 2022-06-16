Node.js PyPI distribution
=====================

[Node.js][] is an open-source, cross-platform, back-end JavaScript runtime environment that runs on the V8 engine and executes JavaScript code outside a web browser. 

The [node-js][pypi] Python package redistributes Node.js so that it can be used as a dependency of Python projects.

[zig]: https://nodejs.org/
[pypi]: https://pypi.org/project/node-js/

Usage
-----

To run the Zig toolchain from the command line, use:

```shell
python -m nodejs
```

To run Node.js from a Python program, use `sys.executable` to locate the Python binary to invoke. For example:

```python
import sys, subprocess

subprocess.call([sys.executable, "-m", "nodejs"])
```

License
-------

The [Node.js license](https://raw.githubusercontent.com/nodejs/node/master/LICENSE).