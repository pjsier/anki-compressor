import argparse
import json
import os
import sqlite3
from io import BytesIO
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from PIL import Image
from pydub import AudioSegment
from tqdm import tqdm

IMAGE_EXT = ("jpg", "jpeg", "png", "tif", "tiff", "gif", "webp")
AUDIO_EXT = (
    "wav",
    "mp3",
    "ogg",
    "flac",
    "mp4",
    "swf",
    "mov",
    "mpeg",
    "mkv",
    "m4a",
    "3gp",
    "spx",
    "oga",
)


def update_db(conn, cur, filename, ext):
    new_filename = ".".join([".".join(filename.split(".")[:-1]), ext])
    cur.execute(
        "SELECT id, flds, sfld FROM notes WHERE flds LIKE ? OR sfld LIKE ?",
        ("%{}%".format(filename), "%{}%".format(filename)),
    )
    rows = cur.fetchall()
    for row in rows:
        cur.execute(
            "UPDATE notes SET flds = ?, sfld = ? WHERE id = ?",
            (
                str(row[1]).replace(filename, new_filename),
                str(row[2]).replace(filename, new_filename),
                row[0],
            ),
        )
        conn.commit()


def compress_image(ext, image_bytes, quality=50):

    # PIL does not recognize .tif extension
    if ext == "tif":
        ext = "tiff"

    img_buf = BytesIO()
    img_buf.write(image_bytes)
    img_buf.seek(0)

    try:
        im = Image.open(img_buf)
        output_buf = BytesIO()
        im.convert("RGB").save(output_buf, format=ext, optimize=True, quality=quality)

        return output_buf.getvalue()
    except Exception:
        pass


def compress_audio(ext, audio_bytes, bitrate="48k"):
    in_tmp = NamedTemporaryFile(delete=False)
    out_tmp = NamedTemporaryFile(delete=False)

    in_tmp.write(audio_bytes)
    in_tmp.seek(0)
    in_tmp.close()
    out_tmp.close()

    try:
        segment = AudioSegment.from_file(in_tmp.name, ext)
        segment.export(out_tmp.name, format="ogg", bitrate=bitrate)

        with open(out_tmp.name, "rb") as f:
            compressed_audio = f.read()

        os.remove(in_tmp.name)
        os.remove(out_tmp.name)

        return compressed_audio
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Compress Anki .apkg file size")
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        required=True,
        help="Input .apkg file to compress",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="Output file to write, defaults to MIN_<INPUT>",
    )
    parser.add_argument(
        "-q",
        "--quality",
        dest="quality",
        default=50,
        type=int,
        help="Quality value for image compression (0-100), defaults to 50",
    )
    parser.add_argument(
        "-b",
        "--bitrate",
        dest="bitrate",
        default="48k",
        help="ffmpeg-compliant bitrate value for audio compression, defaults to 48k",
    )
    parser.add_argument(
        "-t",
        "--image_type",
        dest="image_type",
        default="jpeg",
        choices=IMAGE_EXT,
        help="Filetype for image compression, defaults to jpeg",
    )

    args = parser.parse_args()

    output_file = args.output
    if output_file is None:
        output_file = os.path.join(
            os.path.dirname(args.input), "MIN_{}".format(os.path.basename(args.input))
        )

    if args.input == output_file:
        raise ValueError("Output file cannot have the same name as input")

    anki_zip = ZipFile(args.input)
    if "media" not in anki_zip.namelist():
        raise ValueError("{} does not contain a media file".format(args.input))

    # Create new zip, temp file for SQLite database
    compressed_zip = ZipFile(output_file, "w")
    db_tmp = NamedTemporaryFile(delete=False)
    db_tmp.write(anki_zip.read("collection.anki2"))
    db_tmp.seek(0)
    db_tmp.close()
    conn = sqlite3.connect(db_tmp.name)
    cur = conn.cursor()

    # Read media JSON, create new dict for updates
    media_json = json.loads(anki_zip.read("media").decode("utf-8"))
    media = {}

    for k, v in tqdm(media_json.items()):
        if len(v.split(".")) < 2:
            compressed_zip.writestr(k, anki_zip.read(k))
            continue
        ext = v.split(".")[-1].lower()
        contents = None
        if ext in IMAGE_EXT:
            contents = compress_image(
                args.image_type, anki_zip.read(k), quality=args.quality
            )
            if contents is not None:
                update_db(conn, cur, v, args.image_type)
                v = ".".join([".".join(v.split(".")[:-1]), args.image_type])
        elif ext in AUDIO_EXT:
            contents = compress_audio(ext, anki_zip.read(k), bitrate=args.bitrate)
            if contents is not None:
                update_db(conn, cur, v, "ogg")
                v = ".".join([".".join(v.split(".")[:-1]), "ogg"])
        if contents is None:
            contents = anki_zip.read(k)
        media[k] = v
        compressed_zip.writestr(k, contents)

    compressed_zip.writestr("media", json.dumps(media))
    conn.close()
    with open(db_tmp.name, "rb") as db_file:
        compressed_zip.writestr("collection.anki2", db_file.read())
    os.remove(db_file.name)
    compressed_zip.close()


if __name__ == "__main__":
    main()
