"""Export the coastal model library and scenery with an editable Blender layout."""

import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_scenery import export_model
from coastal import build


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game',type=Path)
    parser.add_argument('blend',type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    args.game.mkdir(parents=True,exist_ok=True)
    args.blend.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    for region in build():
        objects=region.finish()
        export_model(args.game,region,objects)
        with (args.game/f'{region.name}.json').open('w') as handle:
            json.dump(region.data,handle,separators=(',',':'))
        print(f'{region.name}: {len(objects)} objects, {sum(len(o.data.polygons) for o in objects)} faces')
        if region.name=='coastal_props':
            for i,obj in enumerate(objects):
                obj.location.x+=33+(i%4)*7.2
                obj.location.y+=(i//4)*9.2
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    for screen in bpy.data.screens:
        for editor in screen.areas:
            if editor.type=='VIEW_3D':
                space=editor.spaces.active
                space.clip_end=220
                space.shading.color_type='MATERIAL'
                space.region_3d.view_distance=61
                space.region_3d.view_location=(27,6,0)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend),compress=True)


if __name__=='__main__':
    main()
