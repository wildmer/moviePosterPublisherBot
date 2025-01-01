#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ffmpeg # type: ignore
# pip3 uninstall FFmpeg ffmpeg-python
import hashlib
from pathlib import Path
import json
# from pprint import pprint
from dotenv import load_dotenv # type: ignore
# python-dotenv
import os

# ----------------------------------------CONFIG---------------------------------------------#
load_dotenv()
FOLDER = os.getenv("FOLDER")
FILE = os.getenv("FILE")

dir = FOLDER
file_path = FILE

if file_path is None:
    file_path = input("Enter the path of the video file: ")
    local_file_path =  Path(file_path)
    print(f"Local file path: {local_file_path}")
    if not local_file_path.exists():
        print("The file does not exist")

if dir is None:
    print("The FOLDER environment variable is not set")
    # exit()
else:
    local_file_path = Path(dir) / file_path
    print(f"Local file path: {local_file_path}")
    if not local_file_path.exists():
        print("The file does not exist")


# Function to get the MD5 hash of a file
def get_md5_hash_file(file_path: Path, block_size: int = 65536) -> str:
    """Calcula el hash MD5 de un archivo utilizando un tamaño de bloque fijo.
    Este método reduce significativamente el uso de memoria y permite calcular el hash de archivos grandes sin problemas. Además, puedes ajustar el tamaño del block_size para optimizar el rendimiento en función del sistema y del tamaño del archivo.

    Args:
        file_path (Path): _description_
        block_size (int, optional): _description_. Defaults to 65536.

    Returns:
        str: _description_
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            md5_hash.update(block)
    return md5_hash.hexdigest()

print('try to get md5 hash')
md5 = get_md5_hash_file(local_file_path)

file_name_info = md5 + ".json"
info = ffmpeg.probe(local_file_path)
info["md5"] = md5
# write info in a file json

try:
    with open(file_name_info, "w", encoding="utf-8") as file:
        json.dump(
            info,
            file,
            indent=4,  # indent: nos permite darle un formato al archivo json
            ensure_ascii=True,  # indent: nos permite darle un formato al archivo json
            # separators=(
            #     ". ",
            #     " = ",
            # ),  # parámetro para cambiar el separador predeterminado
            sort_keys=True,  # sort_keys: nos permite ordenar las llaves del diccionario
        )
except FileNotFoundError:
    print("File not found")

duration = info["format"]["duration"]
# convert duration to minutes
minutes = int(float(duration)) // 60
seconds = int(float(duration)) % 60
# print(f"Duration: {minutes} minutes and {seconds} seconds")

print('try to get cuts')
cut_one = False
cut_two = False
cut_three = False
cut_four = False

if minutes >= 25:
    cut_one = True

if minutes >= 45:
    cut_two = True

if minutes >= 65:
    cut_three = True

if minutes >= 85:
    cut_four = True


ffmpeg_cmd = f"ffmpeg -i {local_file_path} -ss 00:20:00 -t 00:00:15 -c copy {md5}_cut1{local_file_path.suffix}"
ffmpeg_cmd2 = f"ffmpeg -i {local_file_path} -ss 00:40:00 -t 00:00:15 -c copy {md5}_cut2{local_file_path.suffix}"
ffmpeg_cmd3 = f"ffmpeg -i {local_file_path} -ss 01:00:00 -t 00:00:15 -c copy {md5}_cut3{local_file_path.suffix}"
ffmpeg_cmd4 = f"ffmpeg -i {local_file_path} -ss 01:20:00 -t 00:00:15 -c copy {md5}_cut4{local_file_path.suffix}"

if cut_one:
    os.system(ffmpeg_cmd)
    print("Cut 1 created")

if cut_two:
    os.system(ffmpeg_cmd2)
    print("Cut 2 created")

if cut_three:
    os.system(ffmpeg_cmd3)
    print("Cut 3 created")

if cut_four:
    os.system(ffmpeg_cmd4)
    print("Cut 4 created")

