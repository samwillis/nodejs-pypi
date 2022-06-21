from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nodejs-cmd',
    version='0.0.1a',
    author="Sam Willis",
    description="Additional Standard Command Line Commands For nodejs-bin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samwillis/nodejs-pypi",
    py_modules=['nodejs_cmd'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='~=3.5',
    entry_points={
        'console_scripts': [
            'node = nodejs_cmd:node_main',
            'npm = nodejs_cmd:npm_main',
            'npx = nodejs_cmd:npx_main',
        ],
    },
)
