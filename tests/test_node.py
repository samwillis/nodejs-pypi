"Test nodejs.node"

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_package_installed():
    import nodejs
    assert nodejs.__version__ is not None


def test_runs():
    from nodejs import node
    assert node.run(['--version']) is 0


def test_version(capfd):
    from nodejs import node, node_version
    node.run(['--version'])
    out, err = capfd.readouterr()
    assert out.startswith('v')
    assert out.strip() == f'v{node_version}'


def test_eval(capfd):
    from nodejs import node
    node.run(['--eval', 'console.log("hello")'])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_eval_error(capfd):
    from nodejs import node
    node.run(['--eval', 'console.error("error")'])
    out, err = capfd.readouterr()
    assert err.strip() == 'error'


def test_eval_error_exit():
    from nodejs import node
    ret = node.run(['--eval', 'process.exit(1)'])
    assert ret == 1


def test_script(capfd):
    from nodejs import node
    node.run([os.path.join(THIS_DIR, 'test_node', 'test_script.js')])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_args(capfd):
    from nodejs import node
    node.run([os.path.join(THIS_DIR, 'test_node', 'test_args.js'), 'hello'])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'

