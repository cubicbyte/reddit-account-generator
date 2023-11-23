import re
from setuptools import setup, find_packages


def read(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def get_version(ver_file: str) -> str:  # Credits to pyTelegramBotAPI setup.py
    with open(ver_file, 'r', encoding='utf-8') as f:
        return re.search(r"^__version__\s*=\s*'(.*)'.*$",
                         f.read(), flags=re.MULTILINE).group(1)


setup(
    name='reddit-account-generator',
    version=get_version('reddit_account_generator/_version.py'),
    description='Automatic reddit account generator on selenium.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='cubicbyte',
    author_email='bmaruhnenko@gmail.com',
    url='https://github.com/cubicbyte/reddit-account-generator',
    packages = find_packages(),
    license='MIT',
    keywords='python reddit account-generator account-maker account-generation r-place rplace',
    install_requires=[
        'selenium >=4.7.0, <=4.15.2',
        'selenium-recaptcha-solver==1.9.0',
        'random-username >=1.0.0, <=1.0.2',
        'webdriver-manager~=4.0.1',
        'stem >=1.8.0, <=1.8.2',
        'static-ffmpeg >=2.3, <=2.5',
        'tempmail-python==2.3.2',
        'beautifulsoup4~=4.12.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
    ],
)
