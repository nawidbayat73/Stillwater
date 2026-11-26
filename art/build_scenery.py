"""Build the two versions of the waterfront as GLB and an editable Blender scene."""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh import point
from shore import build


def export_model(directory, region, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(directory/f"{region.name}.glb"),export_format="GLB",
        use_selection=True,export_tangents=True,export_animations=False,
    )


def preview(renders):
    region, objects=renders[0]
    scene=bpy.context.scene
    scene.unit_settings.system="METRIC"
    scene.world=bpy.data.worlds.new("Himmel über Stillwater")
    scene.world.color=(.26,.32,.34)
    env=bpy.data.lights.new("Tageslicht am Nordkai","SUN")
    env.energy=2.1
    env.angle=.16
    sunlight=bpy.data.objects.new("Tageslicht am Nordkai",env)
    scene.collection.objects.link(sunlight)
    sunlight.rotation_euler=(.764,-.38,.679)
    for label in (0,1):
        region, objects = renders[label]
        for x,y,z,color,power,reach,shadows in region.data["lamps"]:
            if power<.60:
                continue
            source=bpy.data.lights.new("Warmlicht" if label==0 else "Notbeleuchtung","POINT")
            source.energy=power*30
            source.color=tuple(int(color[k:k+2],16)/255 for k in (1,3,5))
            source.shadow_soft_size=.135
            obj=bpy.data.objects.new(source.name,source)
            obj.location=point((x,y,z))
            region.collection.objects.link(obj)
    from mathutils import Vector
    lens=bpy.data.cameras.new("Nordkai")
    lens.lens=29
    obj=bpy.data.objects.new("Nordkai",lens)
    scene.collection.objects.link(obj)
    obj.location=point((-32,2.75,3.2))
    obj.rotation_euler=(Vector(point((-9,1.6,-4.70)))-obj.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=obj
    # The night-only layers can be shown separately in the Outliner.
    renders[1][0].collection.hide_render=True
    renders[1][0].collection.hide_viewport=True
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active=renders[0][1][0]
    for screen in bpy.data.screens:
        for editor in screen.areas:
            if editor.type=="VIEW_3D":
                space=editor.spaces.active
                space.shading.color_type="MATERIAL"
                space.clip_end=360
                space.region_3d.view_distance=77
                space.region_3d.view_location=point((0,1.6,-5.4))


def main():
    argv=sys.argv[sys.argv.index("--")+1:]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target",type=Path)
    parser.add_argument("blender_scene",type=Path)
    args=parser.parse_args(argv)
    args.target.mkdir(parents=True,exist_ok=True)
    args.blender_scene.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    regions=build()
    renders = [(region,region.finish()) for region in regions]
    for region,objects in renders:
        export_model(args.target,region,objects)
        (args.target/f"{region.name}.json").write_text(json.dumps(region.data,ensure_ascii=False,separators=(",",":"))+"\n")
        print(region.name,len(objects),"objects",sum(len(obj.data.polygons) for obj in objects),"faces",len(region.data["colliders"]),"collision boxes")
    preview(renders)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blender_scene),compress=True)

if __name__=="__main__":
    main()
