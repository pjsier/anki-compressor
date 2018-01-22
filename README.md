# Anki Compressor

Compresses images and audio in [Anki](https://apps.ankiweb.net/) .apkg files to reduce the overall file size.

## Installation

`anki-compressor` can be installed with Pip, but it requires [Pydub](http://pydub.com/) and [Pillow](https://pillow.readthedocs.io/en/latest/) which have native dependencies that need to be installed.

Once you've installed those dependencies, run `pip install anki-compressor` to install the command line script.

## Usage

```bash
anki-compressor -i input.apkg -o output.apkg -q 50 -b 64k
```

### Arguments

* `-i`: Specifies the input file and is required
* `-o`: Output file name, defaults to `MIN_<INPUT>`
* `-q`: Image quality on a scale of 1-100 supplied to Pillow's image processing, defaults to 50
* `-b`: Bitrate for audio output, defaults to '48k'
