"Test nodejs.npm"

import os
import pathlib
from pytest import CaptureFixture


def test_runs() -> None:
    from nodejs import npm
    assert npm.call(['--version']) is 0


def test_version(capfd: CaptureFixture) -> None:
    from nodejs import npm
    npm.call(['--version'])
    out, err = capfd.readouterr()
    assert isinstance(out, str)


def test_install_package(tmp_path: pathlib.Path, capfd: CaptureFixture) -> None:
    from nodejs import npm, node
    
    os.chdir(tmp_path)
    npm.call(['init', '-y'])
    assert (tmp_path / 'package.json').exists()
    npm.call(['install', 'is-even'])
    assert (tmp_path / 'node_modules' / 'is-even').exists()
    out, err = capfd.readouterr()
    node.call(['--eval', 'console.log(require("is-even")(42))'])
    out, err = capfd.readouterr()
    assert out.strip() == 'true'
    node.call(['--eval', 'console.log(require("is-even")(43))'])
    out, err = capfd.readouterr()
    assert out.strip() == 'false'
