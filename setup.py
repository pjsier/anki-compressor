import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='anki-compressor',
    version='0.0.7',
    url='https://github.com/pjsier/anki-compressor',
    license='MIT',
    author='Patrick Sier',
    description='Compress Anki deck .apkg file size',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'Pillow',
        'pydub',
        'tqdm'
    ],
    packages=['anki_compressor'],
    entry_points={
        'console_scripts': [
            'anki-compressor = anki_compressor.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/pjsier/anki-compressor/issues',
        'Source': 'https://github.com/pjsier/anki-compressor',
    },
)
