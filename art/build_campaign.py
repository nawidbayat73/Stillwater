"""Export the campaign sets in meter-scale coordinates for the game and Blender."""
from pathlib import Path
import argparse
import json
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_scenery import export_model
from campaign import build


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenery",type=Path)
    parser.add_argument("scene",type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    args.scenery.mkdir(parents=True,exist_ok=True)
    args.scene.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    sets=build()
    for region in sets:
        objects=region.finish()
        export_model(args.scenery,region,objects)
        (args.scenery/f"{region.name}.json").write_text(json.dumps(region.data,ensure_ascii=False,separators=(",",":"))+"\n")
        print(region.name,len(objects),"objects",sum(len(o.data.polygons) for o in objects),"faces")
    # Lay out the asset collections for inspection after opening the Blender file.
    offsets={"launch":(0,52),"landfall":(0,0),"chapter1":(0,0),"chapter2":(0,0),
             "chapter3":(0,0),"rigel_medic":(0,0),"chapter4":(105,2),"chapter5":(139,3),"chapter7":(175,8),"instruments":(198,0)}
    for region in sets:
        off=offsets[region.name]
        for obj in list(region.collection.objects):
            obj.location.x+=off[0]
            obj.location.y+=off[1]
    scene=bpy.context.scene
    scene.unit_settings.system="METRIC"
    for screen in bpy.data.screens:
        for editor in screen.areas:
            if editor.type=="VIEW_3D":
                space=editor.spaces.active
                space.clip_end=410
                space.shading.color_type="MATERIAL"
                space.region_3d.view_distance=165
                space.region_3d.view_location=(82,13,4)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(args.scene),compress=True)

if __name__=="__main__":
    main()
