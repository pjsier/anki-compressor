# Anki Compressor

[![Build status](https://github.com/pjsier/anki-compressor/workflows/CI/badge.svg)](https://github.com/pjsier/anki-compressor/actions)
![pypi](https://img.shields.io/pypi/v/anki-compressor)

Compresses images and audio in [Anki](https://apps.ankiweb.net/) .apkg files to reduce the overall file size.

## Installation

`anki-compressor` can be installed with Pip, but it requires [Pydub](http://pydub.com/) and [Pillow](https://pillow.readthedocs.io/en/latest/) which have native dependencies that need to be installed. You'll need to include support for `libvorbis` in the audio library, since all audio is converted to `ogg` and all images are converted to `jpg`.

Once you've installed those dependencies, run `pip install anki-compressor` to install the command line script.

## Usage

```shell
usage: anki-compressor [-h] -i INPUT [-o OUTPUT] [-q QUALITY] [-b BITRATE]

Compress Anki .apkg file size

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input .apkg file to compress
  -o OUTPUT, --output OUTPUT
                        Output file to write, defaults to MIN_<INPUT>
  -q QUALITY, --quality QUALITY
                        Quality value for image compression (0-100), defaults to 50
  -b BITRATE, --bitrate BITRATE
                        ffmpeg-compliant bitrate value for audio compression, defaults to 48k
```

Here's an example of compressing a file `input.apkg` and writing the output to `output.apkg`:

```bash
anki-compressor -i input.apkg -o output.apkg -q 50 -b 64k
```

### Arguments

- `-i`: Specifies the input file and is required
- `-o`: Output file name, defaults to `MIN_<INPUT>`
- `-q`: Image quality on a scale of 1-100 supplied to Pillow's image processing, defaults to 50
- `-b`: Bitrate for audio output, defaults to '48k'
