from pathlib import Path

from setuptools import setup, find_packages

from reddit_account_generator._version import __version__ as version


def read(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def get_requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with Path('requirements.txt').open() as reqs:
        for install in reqs:
            if install.startswith('#'):
                continue
            requirements_list.append(install.strip())

    return requirements_list


setup(
    name='reddit-account-generator',
    version=version,
    description='Automatic reddit account generator on selenium.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='cubicbyte',
    author_email='bmaruhnenko@gmail.com',
    url='https://github.com/cubicbyte/reddit-account-generator',
    packages = find_packages(),
    license='MIT',
    keywords='python reddit account-generator account-maker account-generation r-place rplace',
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
    ],
)
