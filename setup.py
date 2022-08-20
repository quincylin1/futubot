from setuptools import find_packages, setup


def readme():
    with open('README.md', 'r') as f:
        long_description = f.read()
    return long_description


version_file = 'futubot/version.py'


def get_version():
    with open(version_file, 'r') as f:
        exec(compile(f.read(), version_file, 'exec'))
    return locals()['__version__']


if __name__ == '__main__':
    print('version no', get_version())
    setup(
        name='futubot',
        version=get_version(),
        description='Futubot - An intraday trading robot utilizing Futu APIs',
        long_description=readme(),
        author='Quincy Lin',
        author_email='quincylin.333@gmail.com',
        packages=find_packages(exclude=('configs', 'tools', 'demo')),
        install_requires=[
            'dash', 'dash-bootstrap-components', 'dash-core-components',
            'futu-api', 'pandas', 'plotly', 'numpy'
        ],
    )
