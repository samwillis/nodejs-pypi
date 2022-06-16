import os
import hashlib
import urllib.request
from email.message import EmailMessage
from wheel.wheelfile import WheelFile, get_zipinfo_datetime
from zipfile import ZipInfo, ZIP_DEFLATED
import libarchive # from libarchive-c


class ReproducibleWheelFile(WheelFile):
    def writestr(self, zinfo, *args, **kwargs):
        if not isinstance(zinfo, ZipInfo):
            raise ValueError("ZipInfo required")
        zinfo.date_time = (1980,1,1,0,0,0)
        zinfo.create_system = 3
        super().writestr(zinfo, *args, **kwargs)


def make_message(headers, payload=None):
    msg = EmailMessage()
    for name, value in headers.items():
        if isinstance(value, list):
            for value_part in value:
                msg[name] = value_part
        else:
            msg[name] = value
    if payload:
        msg.set_payload(payload)
    return msg


def write_wheel_file(filename, contents):
    with ReproducibleWheelFile(filename, 'w') as wheel:
        for member_info, member_source in contents.items():
            if not isinstance(member_info, ZipInfo):
                member_info = ZipInfo(member_info)
                member_info.external_attr = 0o644 << 16
            member_info.file_size = len(member_source)
            member_info.compress_type = ZIP_DEFLATED
            wheel.writestr(member_info, bytes(member_source))
    return filename


def write_wheel(out_dir, *, name, version, tag, metadata, description, contents, entry_points):
    wheel_name = f'{name}-{version}-{tag}.whl'
    dist_info  = f'{name}-{version}.dist-info'
    return write_wheel_file(os.path.join(out_dir, wheel_name), {
        **contents,
        f'{dist_info}/entry_points.txt': ("""\
[console_scripts]
{entry_points}
""".format(entry_points='\n'.join([f'{k} = {v}' for k, v in entry_points.items()] if entry_points else []))).encode('ascii'),
        f'{dist_info}/METADATA': make_message({
            'Metadata-Version': '2.1',
            'Name': name,
            'Version': version,
            **metadata,
        }, description),
        f'{dist_info}/WHEEL': make_message({
            'Wheel-Version': '1.0',
            'Generator': 'nodejs-pypi make_wheels.py',
            'Root-Is-Purelib': 'false',
            'Tag': tag,
        }),
    })


NODE_BINS = ('bin/node', 'node.exe')
NODE_OTHER_BINS = {
    'bin/npm': ('npm', True),
    'npm.cmd': ('npm', False),
    'bin/npx': ('npx', True),
    'npx.cmd': ('npx', False),
    'bin/corepack': ('corepack', True),     
    'corepack.cmd': ('corepack', False),
}


def write_nodejs_wheel(out_dir, *, version, platform, archive):
    contents = {}
    entry_points = {}
    contents['nodejs/__init__.py'] = f'__version__ = "{version}"\n'.encode('ascii')

    with libarchive.memory_reader(archive) as archive:
        for entry in archive:
            entry_name = '/'.join(entry.name.split('/')[1:])
            if entry.isdir or not entry_name:
                continue

            zip_info = ZipInfo(f'nodejs/{entry_name}')
            zip_info.external_attr = (entry.mode & 0xFFFF) << 16
            contents[zip_info] = b''.join(entry.get_blocks())

            if entry_name in NODE_BINS:
                entry_points['node'] = 'nodejs.node:main'
                contents['nodejs/node.py'] = f'''\
import os, sys, subprocess
def run(args):
    return subprocess.call([
        os.path.join(os.path.dirname(__file__), "{entry_name}"),
        *args
    ])
def main():
    sys.exit(run(sys.argv[1:]))
if __name__ == '__main__':
    main()
'''.encode('ascii')
                contents['nodejs/__main__.py'] = f'''\
from .node import main
if __name__ == '__main__':
    main()
'''.encode('ascii')
            elif entry_name in NODE_OTHER_BINS and NODE_OTHER_BINS[entry_name][1]:
                entry_points[NODE_OTHER_BINS[entry_name][0]] = f'nodejs.{NODE_OTHER_BINS[entry_name][0]}:main'
                script_name = '/'.join(os.path.normpath(os.path.join(os.path.dirname(entry.name), entry.linkpath)).split('/')[1:])
                contents[f'nodejs/{NODE_OTHER_BINS[entry_name][0]}.py'] = f'''\
import os, sys
from .node import run as run_node
def run(args):
    return run_node([
        os.path.join(os.path.dirname(__file__), "{script_name}"),
        *args
    ])
def main():
    sys.exit(run(sys.argv[1:]))
if __name__ == '__main__':
    main()
'''.encode('ascii')
            elif entry_name in NODE_OTHER_BINS:
                entry_points[NODE_OTHER_BINS[entry_name][0]] = f'nodejs.{NODE_OTHER_BINS[entry_name][0]}:main'
                contents[f'nodejs/{NODE_OTHER_BINS[entry_name][0]}.py'] = f'''\
import os, sys, subprocess
def run(args):
    return subprocess.call([
        os.path.join(os.path.dirname(__file__), "{entry_name}"),
        *args
    ])
def main():
    sys.exit(run(sys.argv[1:]))
if __name__ == '__main__':
    main()
'''.encode('ascii')

    with open('README.pypi.md') as f:
        description = f.read()

    return write_wheel(out_dir,
        name='nodejs',
        version=version,
        tag=f'py3-none-{platform}',
        metadata={
            'Summary': 'Node.js is an open-source, cross-platform, back-end JavaScript runtime environment that runs on the V8 engine and executes JavaScript code outside a web browser.',
            'Description-Content-Type': 'text/markdown',
            'License': 'MIT',
            'Classifier': [
                'License :: OSI Approved :: MIT License',
            ],
            'Project-URL': [
                'Homepage, https://nodejs.org',
            ],
            'Requires-Python': '~=3.5',
        },
        description=description,
        contents=contents,
        entry_points=entry_points,
    )


def main():
    print('Making Node.js Wheels')
    node_version = '16.15.1'
    out_version = f'{node_version}a1'

    for node_platform, python_platform in {
        'win-x86':      'win32',
        'win-x64':      'win_amd64',
        'darwin-x64':   'macosx_10_9_x86_64',
        'darwin-arm64': 'macosx_11_0_arm64',
        'linux-x64':    'manylinux_2_12_x86_64.manylinux2010_x86_64',
        'linux-armv7l': 'manylinux_2_17_armv7l.manylinux2014_armv7l',
        'linux-arm64':  'manylinux_2_17_aarch64.manylinux2014_aarch64',
    }.items():
        print(f'- Making Wheel for {node_platform}')
        node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-{node_platform}.' + \
                ('zip' if node_platform.startswith('win-') else 'tar.xz')
        with urllib.request.urlopen(node_url) as request:
            node_archive = request.read()
            print(f'  {hashlib.sha256(node_archive).hexdigest()} {node_url}')

        wheel_path = write_nodejs_wheel('dist/',
            version=out_version,
            platform=python_platform,
            archive=node_archive)
        with open(wheel_path, 'rb') as wheel:
            print(f'  {hashlib.sha256(wheel.read()).hexdigest()} {wheel_path}')


if __name__ == '__main__':
    main()