import os
import sys
import json
import argparse
from io import BytesIO
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from PIL import Image
from tqdm import tqdm


IMAGE_EXT = ('jpg', 'jpeg', 'png', 'tif', 'tiff', 'gif', 'webp')
AUDIO_EXT = ('wav', 'mp3', 'ogg', 'flac', 'mp4', 'swf', 'mov', 'mpeg', 'mkv', 'm4a', '3gp', 'spx', 'oga')


parser = argparse.ArgumentParser(description='Compress Anki .apkg file size')
parser.add_argument('-i', '--input', dest='input', required=True,
                    help='Input .apkg file to compress')
parser.add_argument('-o', '--output', dest='output', required=False,
                    help='Output file to write, defaults to MIN_<INPUT>')
parser.add_argument('-q', '--quality', dest='quality', default=50, type=int,
                    help='Quality value for image compression (0-100), defaults to 50')
parser.add_argument('-b', '--bitrate', dest='bitrate', default='48k',
                    help='ffmpeg-compliant bitrate value for audio compression, defaults to 48k')


def compress_image(ext, image_bytes, quality=50):
    img_buf = BytesIO()
    img_buf.write(image_bytes)
    img_buf.seek(0)

    im = Image.open(img_buf)
    output_buf = BytesIO()
    if ext == 'jpg':
        ext = 'JPEG'
    im.save(output_buf, ext, optimize=True, quality=quality)

    return output_buf.getvalue()


def compress_audio(ext, audio_bytes, bitrate='48k'):
    in_tmp = NamedTemporaryFile(delete=False)
    out_tmp = NamedTemporaryFile(delete=False)

    in_tmp.write(audio_bytes)
    in_tmp.seek(0)
    in_tmp.close()
    out_tmp.close()

    segment = AudioSegment.from_file(in_tmp.name, ext)
    segment.export(out_tmp.name, format=ext, bitrate=bitrate)

    with open(out_tmp.name, 'rb') as f:
        compressed_audio = f.read()

    os.remove(in_tmp.name)
    os.remove(out_tmp.name)

    return compressed_audio


def main():
    args = parser.parse_args()

    output_file = args.output
    if output_file is None:
        output_file = os.path.join(
            os.path.dirname(args.input),
            'MIN_{}'.format(os.path.basename(args.input))
        )

    if args.input == output_file:
        raise ValueError('Output file cannot have the same name as input')
    
    anki_zip = ZipFile(args.input)
    if not 'media' in anki_zip.namelist():
        raise ValueError('{} does not contain a media file'.format(args.input))
    
    # Create new zip, copy collection file
    compressed_zip = ZipFile(output_file, 'w')
    compressed_zip.writestr('collection.anki2', anki_zip.read('collection.anki2'))

    media_str = anki_zip.read('media').decode('utf-8')
    compressed_zip.writestr('media', media_str)
    media_json = json.loads(media_str)

    for k, v in tqdm(media_json.items()):
        if len(v.split('.')) < 2:
            compressed_zip.writestr(k, anki_zip.read(k))
            continue
        ext = v.split('.')[-1].lower()
        if ext in IMAGE_EXT:
            contents = compress_image(ext, anki_zip.read(k), quality=args.quality)
        elif ext in AUDIO_EXT:
            contents = compress_audio(ext, anki_zip.read(k), bitrate=args.bitrate)
        else:
            contents = anki_zip.read(k)
        compressed_zip.writestr(k, contents)

    compressed_zip.close()


if __name__ == '__main__':
    main()
