"""Extend the owner's recovered Windows Godot pack with the rebuilt chapters."""
import argparse
import hashlib
import io
from pathlib import Path
import re
import struct

def assemble(base, target):
    raw = base.read_bytes()
    size, magic = struct.unpack_from("<Q4s", raw, len(raw)-12)
    assert magic == b"GDPC"
    start = len(raw)-12-size
    pack = raw[start:-12]
    magic, version, major, minor, patch, flags, origin, table = struct.unpack_from("<4sIIIIIQQ", pack)
    assert (magic, version, flags) == (b"GDPC", 4, 2)
    directory = io.BytesIO(pack[table:])
    count, = struct.unpack("<I", directory.read(4))
    files = {}
    for _ in range(count):
        length, = struct.unpack("<I", directory.read(4))
        path = directory.read(length).rstrip(b"\0").decode()
        offset, length, digest, flag = struct.unpack("<QQ16sI", directory.read(36))
        files[path] = (offset, length, digest, flag)
    game = Path(__file__).resolve().parent/"game"
    scenery = ("ufer", "sturm", "landfall", "launch", "chapter1", "chapter2", "chapter3", "rigel_medic",
               "chapter4", "chapter5", "chapter7", "instruments", "coastal_props", "coastal_street")
    for model in scenery:
        for suffix in ("glb", "json"):
            name = f"scenery/{model}.{suffix}"
            if not (game/name).is_file():
                raise FileNotFoundError(f"Build scenery first: missing {name}")
    for kind in ("siding", "timber", "bark", "stone", "plaster", "brick", "road", "sand", "metal", "corrugated", "leather"):
        for map_suffix in (".jpg", "_n.jpg"):
            if not (game/f"finish/{kind}{map_suffix}").is_file():
                raise FileNotFoundError(f"Build photographic materials first: missing {kind}{map_suffix}")
    content = bytearray(pack[:table])
    def add(name, data):
        content.extend(bytes(-len(content) % 16))
        files[name] = (len(content)-origin, len(data), hashlib.md5(data).digest(), 0)
        content.extend(data)
    offset, length, _, _ = files.pop("main.tscn.remap")
    remap = pack[origin+offset:origin+offset+length].decode()
    old_scene = re.search(r'path="([^"]+)"', remap)[1]
    for file in sorted(game.rglob("*")):
        if file.is_file():
            data = file.read_bytes()
            if file.name == "main.tscn":
                data = data.replace(b"__BASE_SCENE__",old_scene.encode())
            add(file.relative_to(game).as_posix(),data)
    table = len(content)
    content.extend(struct.pack("<I", len(files)))
    for name,(offset,length,digest,flag) in sorted(files.items()):
        path = name.encode()
        path += bytes(-len(path)%4)
        content.extend(struct.pack("<I",len(path))+path+struct.pack("<QQ16sI",offset,length,digest,flag))
    content.extend(bytes(-(len(content)+12)%8))
    struct.pack_into("<Q",content,32,table)
    payload = content + struct.pack("<Q4s",len(content),b"GDPC")
    pe = bytearray(raw[:start])
    header, = struct.unpack_from("<I", pe,60)
    sections, = struct.unpack_from("<H", pe,header+6)
    optional, = struct.unpack_from("<H", pe,header+20)
    for i in range(sections):
        section = header+24+optional+40*i
        if pe[section:section+8].rstrip(b"\0")==b"pck":
            struct.pack_into("<II",pe,section+16,len(payload),start)
            break
    else: raise ValueError("Missing Windows pck section")
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("wb") as output:
        output.write(pe)
        output.write(payload)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("basis",type=Path)
    parser.add_argument("ziel",type=Path)
    args=parser.parse_args()
    assemble(args.basis,args.ziel)
