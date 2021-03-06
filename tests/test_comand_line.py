"Test nodejs command line"

import os, sys, subprocess


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_runs():
    assert subprocess.call([sys.executable, "-m", "nodejs", "--version"]) == 0


def test_version(capfd):
    subprocess.call([sys.executable, "-m", "nodejs", "--version"])
    out, err = capfd.readouterr()
    assert out.startswith('v')


def test_eval(capfd):
    subprocess.call([sys.executable, "-m", "nodejs", "--eval", "console.log('hello')"])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_eval_error(capfd):
    subprocess.call([sys.executable, "-m", "nodejs", "--eval", "console.error('error')"])
    out, err = capfd.readouterr()
    assert err.strip() == 'error'


def test_eval_error_exit():
    ret = subprocess.call([sys.executable, "-m", "nodejs", "--eval", "process.exit(1)"])
    assert ret == 1


def test_script(capfd):
    subprocess.call([sys.executable, "-m", "nodejs", os.path.join(THIS_DIR, "test_node", "test_script.js")])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_args(capfd):
    subprocess.call([sys.executable, "-m", "nodejs", os.path.join(THIS_DIR, "test_node", "test_args.js"), "hello"])
    out, err = capfd.readouterr()
    assert out.strip() == 'hello'


def test_npm_runs():
    assert subprocess.call([sys.executable, "-m", "nodejs.npm", "--version"]) == 0


def test_npm_version(capfd):
    subprocess.call([sys.executable, "-m", "nodejs.npm", "--version"])
    out, err = capfd.readouterr()
    assert isinstance(out, str)


def test_install_package(tmp_path, capfd):
    os.chdir(tmp_path)
    subprocess.call([sys.executable, "-m", "nodejs.npm", "init", "-y"])
    assert (tmp_path / 'package.json').exists()
    subprocess.call([sys.executable, "-m", "nodejs.npm", "install", "is-even"])
    assert (tmp_path / 'node_modules' / 'is-even').exists()
    out, err = capfd.readouterr()
    subprocess.call([sys.executable, "-m", "nodejs", "--eval", 'console.log(require("is-even")(42))'])
    out, err = capfd.readouterr()
    assert out.strip() == 'true'
    subprocess.call([sys.executable, "-m", "nodejs", "--eval", 'console.log(require("is-even")(43))'])
    out, err = capfd.readouterr()
    assert out.strip() == 'false'
