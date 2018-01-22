from setuptools import setup

setup(
    name='anki-compressor',
    version='0.0.2',
    url='https://github.com/pjsier/anki-compressor',
    license='MIT',
    author='Patrick Sier',
    author_email='pjsier@gmail.com',
    description='Compress Anki deck .apkg file size',
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
)
