import os
import hashlib
import urllib.request
import libarchive
from email.message import EmailMessage
from wheel.wheelfile import WheelFile
from zipfile import ZipInfo, ZIP_DEFLATED
from inspect import cleandoc


# Versions to build if run as a script:
BUILD_VERSIONS = ('14.19.3', '16.15.1', '18.4.0')

# Suffix to append to the Wheel
# For pre release versions this should be 'aN', e.g. 'a1'
# For release versions this should be ''
# See https://peps.python.org/pep-0427/#file-name-convention for details.
BUILD_SUFFIX = 'a3'

# Main binary for node
# Path of binary inn downloaded distribution to match
NODE_BINS = ('bin/node', 'node.exe')

# Other binaries
# key: path of binary inn downloaded distribution to match
# value: tuple of (
#   <name>,
#   <True = is a link to script to run with node, False = is executable>
# )
NODE_OTHER_BINS = {
    'bin/npm': ('npm', True),
    'npm.cmd': ('npm', False),
    'bin/npx': ('npx', True),
    'npx.cmd': ('npx', False),
    'bin/corepack': ('corepack', True),     
    'corepack.cmd': ('corepack', False),
}

# Mapping of node platforms to Python platforms
PLATFORMS = {
    'win-x86':      'win32',
    'win-x64':      'win_amd64',
    'darwin-x64':   'macosx_10_9_x86_64',
    'darwin-arm64': 'macosx_11_0_arm64',
    'linux-x64':    'manylinux_2_12_x86_64.manylinux2010_x86_64',
    'linux-armv7l': 'manylinux_2_17_armv7l.manylinux2014_armv7l',
    'linux-arm64':  'manylinux_2_17_aarch64.manylinux2014_aarch64',
}


class ReproducibleWheelFile(WheelFile):
    def writestr(self, zinfo, *args, **kwargs):
        if not isinstance(zinfo, ZipInfo):
            raise ValueError("ZipInfo required")
        zinfo.date_time = (1980, 1, 1, 0, 0, 0)
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
    name_snake = name.replace('-', '_')
    wheel_name = f'{name_snake}-{version}-{tag}.whl'
    dist_info  = f'{name_snake}-{version}.dist-info'
    if entry_points:
        contents[f'{dist_info}/entry_points.txt'] = (cleandoc("""
            [console_scripts]
            {entry_points}
        """).format(entry_points='\n'.join([f'{k} = {v}' for k, v in entry_points.items()] if entry_points else []))).encode('ascii'),
    return write_wheel_file(os.path.join(out_dir, wheel_name), {
        **contents,
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


def write_nodejs_wheel(out_dir, *, node_version, version, platform, archive):
    contents = {}
    entry_points = {}
    init_imports = []

    with libarchive.memory_reader(archive) as archive:
        for entry in archive:
            entry_name = '/'.join(entry.name.split('/')[1:])
            if entry.isdir or not entry_name:
                continue

            zip_info = ZipInfo(f'nodejs/{entry_name}')
            zip_info.external_attr = (entry.mode & 0xFFFF) << 16
            contents[zip_info] = b''.join(entry.get_blocks())

            if entry_name in NODE_BINS:
                # entry_points['node'] = 'nodejs.node:main'
                init_imports.append('from . import node')
                contents['nodejs/node.py'] = cleandoc(f"""
                    import os, sys, subprocess
                    from typing import TYPE_CHECKING

                    path = os.path.join(os.path.dirname(__file__), "{entry_name}")

                    if TYPE_CHECKING:
                        call = subprocess.call
                        run = subprocess.run
                        Popen = subprocess.Popen

                    else:
                        def call(args, **kwargs):
                            return subprocess.call([
                                path,
                                *args
                            ], **kwargs)

                        def run(args, **kwargs):
                            return subprocess.run([
                                path,
                                *args
                            ], **kwargs)
                        
                        def Popen(args, **kwargs):
                            return subprocess.Popen([
                                path,
                                *args
                            ], **kwargs)
                        
                    def main() -> None:
                        sys.exit(call(sys.argv[1:]))
                        
                    if __name__ == '__main__':
                        main()
                """).encode('ascii')
                contents['nodejs/__main__.py'] = cleandoc(f"""
                    from .node import main

                    if __name__ == '__main__':
                        main()
                """).encode('ascii')
            elif entry_name in NODE_OTHER_BINS and NODE_OTHER_BINS[entry_name][1]:
                # entry_points[NODE_OTHER_BINS[entry_name][0]] = f'nodejs.{NODE_OTHER_BINS[entry_name][0]}:main'
                init_imports.append(f'from . import {NODE_OTHER_BINS[entry_name][0]}')
                script_name = '/'.join(os.path.normpath(os.path.join(os.path.dirname(entry.name), entry.linkpath)).split('/')[1:])
                contents[f'nodejs/{NODE_OTHER_BINS[entry_name][0]}.py'] = cleandoc(f"""
                    import os, sys
                    from typing import TYPE_CHECKING
                    from . import node

                    if TYPE_CHECKING:
                        call = subprocess.call
                        run = subprocess.run
                        Popen = subprocess.Popen

                    else:
                        def call(args, **kwargs):
                            return node.call([
                                os.path.join(os.path.dirname(__file__), "{script_name}"),
                                *args
                            ], **kwargs)

                        def run(args, **kwargs):
                            return node.run([
                                os.path.join(os.path.dirname(__file__), "{script_name}"),
                                *args
                            ], **kwargs)
                        
                        def Popen(args, **kwargs):
                            return node.Popen([
                                os.path.join(os.path.dirname(__file__), "{script_name}"),
                                *args
                            ], **kwargs)
                    
                    def main() -> None:
                        sys.exit(call(sys.argv[1:]))
                    
                    if __name__ == '__main__':
                        main()
                """).encode('ascii')
            elif entry_name in NODE_OTHER_BINS:
                # entry_points[NODE_OTHER_BINS[entry_name][0]] = f'nodejs.{NODE_OTHER_BINS[entry_name][0]}:main'
                init_imports.append(f'from . import {NODE_OTHER_BINS[entry_name][0]}')
                contents[f'nodejs/{NODE_OTHER_BINS[entry_name][0]}.py'] = cleandoc(f"""
                    import os, sys, subprocess
                    from typing import TYPE_CHECKING

                    if TYPE_CHECKING:
                        call = subprocess.call
                        run = subprocess.run
                        Popen = subprocess.Popen

                    else:
                        def call(args, **kwargs):
                            return subprocess.call([
                                os.path.join(os.path.dirname(__file__), "{entry_name}"),
                                *args
                            ], **kwargs)

                        def run(args, **kwargs):
                            return subprocess.run([
                                os.path.join(os.path.dirname(__file__), "{entry_name}"),
                                *args
                            ], **kwargs)
                        
                        def Popen(args, **kwargs):
                            return subprocess.Popen([
                                os.path.join(os.path.dirname(__file__), "{entry_name}"),
                                *args
                            ], **kwargs)
                    
                    def main() -> None:
                        sys.exit(call(sys.argv[1:]))
                    
                    if __name__ == '__main__':
                        main()
                """).encode('ascii')
    
    contents['nodejs/__init__.py'] = (cleandoc("""
        from .node import path, main, call, run, Popen
        {init_imports}

        __version__ = "{version}"
        node_version = "{node_version}"
    """)).format(
        init_imports='\n'.join(init_imports),
        version=version,
        node_version=node_version,
    ).encode('ascii')

    with open('README.md') as f:
        description = f.read()

    return write_wheel(out_dir,
        name='nodejs-bin',
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
                'Project Homepage, https://github.com/samwillis/nodejs-pypi',
                'Node.js Homepage, https://nodejs.org',
            ],
            'Requires-Python': '~=3.5',
            'Provides-Extra': 'cmd',
            'Requires-Dist': "nodejs-cmd; extra == 'cmd'",
        },
        description=description,
        contents=contents,
        entry_points=entry_points,
    )


def make_nodejs_version(node_version, suffix=''):
    wheel_version = f'{node_version}{suffix}'
    print('--')
    print('Making Node.js Wheels for version', node_version)
    if suffix:
        print('Suffix:', suffix)

    for node_platform, python_platform in PLATFORMS.items():
        print(f'- Making Wheel for {node_platform}')
        node_url = f'https://nodejs.org/dist/v{node_version}/node-v{node_version}-{node_platform}.' + \
                ('zip' if node_platform.startswith('win-') else 'tar.xz')
        
        try:
            with urllib.request.urlopen(node_url) as request:
                node_archive = request.read()
                print(f'  {node_url}')
                print(f'    {hashlib.sha256(node_archive).hexdigest()}')
        except urllib.error.HTTPError as e:
            print(f'  {e.code} {e.reason}')
            print(f'  Skipping {node_platform}')
            continue

        wheel_path = write_nodejs_wheel('dist/',
            node_version=node_version,
            version=wheel_version,
            platform=python_platform,
            archive=node_archive)
        with open(wheel_path, 'rb') as wheel:
            print(f'  {wheel_path}')
            print(f'    {hashlib.sha256(wheel.read()).hexdigest()}')

def main():
    for node_version in BUILD_VERSIONS:
        make_nodejs_version(node_version, suffix=BUILD_SUFFIX)

if __name__ == '__main__':
    main()