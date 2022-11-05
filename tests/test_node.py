"Test nodejs.node"

import os
from pytest import CaptureFixture


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_package_installed() -> None:
    import nodejs
    assert nodejs.__version__ is not None


def test_runs() -> None:
    from nodejs import node
    assert node.call(['--version']) is 0


def test_version(capfd: CaptureFixture) -> None:
    from nodejs import node, node_version
    node.call(['--version'])
    out, err = capfd.readouterr()
    assert out.startswith('v')
    assert out.strip() == f'v{node_version}'


def test_eval(capfd: CaptureFixture) -> None:
    from nodejs import node
    node.call(['--eval', 'console.log("hello")'])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_eval_error(capfd: CaptureFixture) -> None:
    from nodejs import node
    node.call(['--eval', 'console.error("error")'])
    out, err = capfd.readouterr()
    assert err.strip() == 'error'


def test_eval_error_exit() -> None:
    from nodejs import node
    ret = node.call(['--eval', 'process.exit(1)'])
    assert ret == 1


def test_script(capfd: CaptureFixture) -> None:
    from nodejs import node
    node.call([os.path.join(THIS_DIR, 'test_node', 'test_script.js')])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_args(capfd: CaptureFixture) -> None:
    from nodejs import node
    node.call([os.path.join(THIS_DIR, 'test_node', 'test_args.js'), 'hello'])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'

