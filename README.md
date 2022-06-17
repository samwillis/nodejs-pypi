Node.js PyPI distribution
=====================

This repository contains the script used to repackage the [releases][nodejsdl] of [Node.js][nodejs] as [Python binary wheels][wheel]. This document is intended for maintainers; see the [package README][pkgreadme] for rationale and usage instructions.

The repackaged artifacts are published as the [node-js PyPI package][pypi].

[nodejs]: https://nodejs.org/
[nodejsdl]:  https://nodejs.org/en/download/
[wheel]: https://github.com/pypa/wheel
[pkgreadme]: README.pypi.md
[pypi]: https://pypi.org/project/node-js/

This tool is based on the work of the creators of the [Zig language][ziglang], see [the original][basedon]. Thank you!

[ziglang]: https://ziglang.org
[basedon]: https://github.com/ziglang/zig-pypi

Preparation
-----------

The script requires Python 3.5 or later.

Install the dependencies:

```shell
pip install wheel twine libarchive-c
```

The `libarchive-c` Python library requires the native [libarchive][] library to be available.

[libarchive]: https://libarchive.org/

Building wheels
---------------

Run the repackaging script:

```shell
python make_wheels.py
```

This command will download the Node.js release archives for every supported platform and convert them to binary wheels, which are placed under `dist/`. The Node.js version and platforms are configured in the script source.

The process of converting release archives to binary wheels is deterministic, and the output of the script should be bit-for-bit identical regardless of the environment and platform it runs under. To this end, it prints the SHA256 hashes of inputs and outputs; the hashes of the inputs will match the ones on the [Zig downloads page][nodejsdl], and the hashes of the outputs will match the ones on the [PyPI downloads page][pypidl].

[pypidl]: https://pypi.org/project/node-js/#files

Uploading wheels
----------------

Run the publishing utility:

```shell
twine dist/*
```

This command will upload the binary wheels built in the previous step to PyPI.

License
-------

This script is distributed under the terms of the [MIT (Expat) license](LICENSE.txt).