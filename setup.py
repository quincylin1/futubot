from setuptools import find_packages, setup


def readme():
    with open('README.md', 'r') as f:
        long_description = f.read()
    return long_description


if __name__ == '__main__':
    setup(
        name='futubot',
        version='1.0.0',
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
