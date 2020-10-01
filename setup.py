from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = []
with open('requirements.txt') as f:
    for line in f.readlines():
        line = line.strip()  # Remove spaces
        line = line.split('#')[0]  # Remove comments
        if line:  # Remove empty lines
            requires.append(line)

setup(
    name='django-clickhouse-huey',
    version='1.0.0',
    packages=['django_clickhouse'],
    package_dir={'': 'src'},
    url='https://github.com/oznakn/django-clickhouse-huey',
    license='MIT License',
    author='Ozan Akın',
    author_email='ozan@oznakn.com',
    description='Django extension to integrate with ClickHouse database',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requires
)
