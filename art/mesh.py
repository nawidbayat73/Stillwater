"""Blender mesh construction in Godot coordinates, with a shared scene layout."""

from __future__ import annotations

import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

from textures import CARD_ROWS, CARDS, SURFACES

PI=math.pi
TAU=math.tau
ATLAS = {card[0]:i for i,card in enumerate(CARDS)}
TEXTURES = Path(os.environ.get("STILLWATER_TEXTURES", "/tmp/stillwater-art/textures"))

SOLID = {
    "tar":("232d2c",.85,0,0),"coal":("222d2d",.85,0,0),
    "ink":("222f2c",.78,0,0),"black":("131d1f",.87,0,0),
    "deep_glass":("5b7472",.23,.20,0),"glazing":("879f9a",.23,.09,0),"glass_green":("557983",.28,.28,0),
    "glass_amber":("bd9e6f",.27,.19,.12),"chrome":("9aaa9f",.33,.59,0),
    "brass":("a68b58",.43,.42,0),"copper":("a57656",.44,.38,0),
    "paper":("ccbd9d",.91,0,0),"porcelain":("e2d4b9",.42,0,0),
    "ceramic_blue":("4f7080",.41,.02,0),"ceramic_red":("a36150",.41,0,0),
    "bulb":("f5cf91",.36,0,1.9),"amber":("edb56f",.37,0,.98),
    "volt":("91ccc4",.32,0,.82),"signal":("af5144",.46,0,.86),
    "moss_green":("677355",.88,0,0),"leaf":("5f754e",.88,0,0),
    "leaf_light":("879366",.88,0,0),"leaf_dark":("455846",.88,0,0),
    "flower":("b49478",.9,0,0),"petal":("d5bd8c",.86,0,0),
    "chalk":("cdc198",.88,0,0),"toast":("b39661",.9,0,0),
    "pie":("a97a4d",.94,0,0),"peel":("d9bf8c",.91,0,0),
    "rust_red":("9b5742",.66,.19,0),"blue_ink":("3f6174",.76,0,0),
    "dark_crt":("355753",.31,.14,.22),"crt_light":("90c4a9",.52,0,.70),
    "conduit":("736858",.72,.15,0),"rope":("a99167",.93,0,0),
    "net":("827b67",.91,0,0),"tire":("383c37",.9,0,0),
    "sodium":("da9558",.45,0,1.10),
    "hazard":("bb9856",.62,.02,0),
    "soup":("45352b",.52,0,0),
}
MATERIALS = {}


def point(value):
    x,y,z=value
    return x,-z,y


def srgb(hex_value):
    values=[int(hex_value[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values)


def mat(name):
    if name in MATERIALS:
        return MATERIALS[name]
    material=bpy.data.materials.new(name.replace("_"," ").capitalize())
    material.use_nodes=True
    tree=material.node_tree
    bsdf=tree.nodes.get("Principled BSDF")
    texture = TEXTURES / ("lettering.jpg" if name=="print" else f"{name}.jpg")
    emissive=0
    if name in SURFACES:
        hex_value,_,rough,_=SURFACES[name]
        metal=.15 if name in {"aged_steel","deep_steel","diamond_plate","zinc","wet_iron"} else 0
    elif name=="print":
        hex_value,rough,metal="bcaf8e",.83,0
    else:
        hex_value,rough,metal,emissive=SOLID[name]
    color=srgb(hex_value)
    material.diffuse_color=(*color,1)
    bsdf.inputs["Base Color"].default_value=(*color,1)
    bsdf.inputs["Roughness"].default_value=rough
    bsdf.inputs["Metallic"].default_value=metal
    if name=="glazing":
        bsdf.inputs["Alpha"].default_value=.29
        material.surface_render_method="DITHERED"
    if texture.is_file():
        node=tree.nodes.new("ShaderNodeTexImage")
        node.image=bpy.data.images.load(str(texture),check_existing=True)
        node.image.pack()
        tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        normal = TEXTURES/f"{name}_n.png"
        if normal.is_file():
            image=tree.nodes.new("ShaderNodeTexImage")
            image.image=bpy.data.images.load(str(normal),check_existing=True)
            image.image.colorspace_settings.name="Non-Color"
            image.image.pack()
            bump=tree.nodes.new("ShaderNodeNormalMap")
            bump.inputs["Strength"].default_value=.36
            tree.links.new(image.outputs["Color"],bump.inputs["Color"])
            tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    if emissive:
        bsdf.inputs["Emission Color"].default_value=(*color,1)
        bsdf.inputs["Emission Strength"].default_value=emissive
    MATERIALS[name]=material
    return material


def rotate_y(v, yaw):
    x,y,z=v
    c,s=math.cos(yaw),math.sin(yaw)
    return (x*c+z*s,y,-x*s+z*c)


class Set:
    def __init__(self,name):
        self.name=name
        self.meshes=[]
        self.data={"colliders":[],"lamps":[],"anchors":{}}
        self.collection=bpy.data.collections.new(name.title())
        bpy.context.scene.collection.children.link(self.collection)

    def mesh(self,name,at=(0,0,0),yaw=0):
        group=Mesh(self,name,at,yaw)
        self.meshes.append(group)
        return group

    def finish(self):
        return [item.create() for item in self.meshes if item.faces]


class Mesh:
    def __init__(self,region,name,at,yaw):
        self.region=region
        self.name=name
        self.at=at
        self.yaw=yaw
        self.verts=[]
        self.faces=[]
        self.keys=[]
        self.uv=[]
        self.smooth=[]

    def location(self,v):
        return tuple(a+b for a,b in zip(self.at,rotate_y(v,self.yaw)))

    def collision(self, at, size, yaw=0.0):
        data=[*self.location(at),*size,yaw+self.yaw]
        self.region.data["colliders"].append([round(x,4) for x in data])

    def light(self,at,color,power,radius,shadow=False):
        self.region.data["lamps"].append([*self.location(at),color,power,radius,shadow])

    def anchor(self,name,at):
        anchors=self.region.data["anchors"]
        if name in anchors:
            raise ValueError(f"Duplicate {self.region.name} anchor {name}")
        anchors[name]=[round(x,4) for x in self.location(at)]

    def add(self, verts, faces, key, uv=None, smooth=False):
        start=len(self.verts)
        self.verts.extend(point(v) for v in verts)
        seen=set()
        for i, face in enumerate(faces):
            indices=frozenset(face)
            if len(indices)!=len(face) or indices in seen:
                continue
            seen.add(indices)
            coords=[verts[j] for j in face]
            mapping=uv[i] if uv else self.project(coords,key)
            if len(face)>4:
                pieces=[(0,k,k+1) for k in range(1,len(face)-1)]
            else:
                pieces=[tuple(range(len(face)))]
            for piece in pieces:
                self.faces.append(tuple(start+face[j] for j in piece))
                self.keys.append(key)
                self.uv.append(tuple(mapping[j] for j in piece))
                self.smooth.append(smooth)

    @staticmethod
    def project(coords,key):
        a,b,c=(Vector(v) for v in coords[:3])
        axis=max(range(3),key=lambda idx:abs((b-a).cross(c-a)[idx]))
        d0,d1=((2,1),(0,2),(0,1))[axis]
        meters=SURFACES[key][3] if key in SURFACES else 1
        return [(v[d0]/meters,v[d1]/meters) for v in coords]

    def quad(self, coords,key,uv=None):
        self.add(coords,[(0,1,2,3)],key,[uv] if uv else None)

    def box(self, at, size, key, solid=False, yaw=0):
        x,y,z=(v*.5 for v in size)
        raw=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
             (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
        verts=[tuple(a+b for a,b in zip(at,rotate_y(v,yaw))) for v in raw]
        self.add(verts,[(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)],key)
        if solid:
            self.collision(at,size,yaw)

    def soft(self, at, size, key, rounding=.08, yaw=0, solid=False):
        """Rounded plan and gently sloping upholstery at the top and bottom."""
        w,h,d=size
        r=min(rounding,w*.35,d*.35,h*.42)
        verts=[]
        corners=[(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]
        for height, radius in [(-h/2,r*.28),(-h/2+r*.7,r),(h/2-r*.75,r),(h/2,r*.25)]:
            for x,z,offset in corners:
                for i in range(4):
                    a=math.radians(offset+90*i/3)
                    v=(x+radius*math.cos(a),height,z+radius*math.sin(a))
                    verts.append(tuple(p+q for p,q in zip(at,rotate_y(v,yaw))))
        n=16
        sides=[(r0*n+j,(r0+1)*n+j,(r0+1)*n+(j+1)%n,r0*n+(j+1)%n)
               for r0 in range(3) for j in range(n)]
        self.add(verts,sides,key,smooth=True)
        self.add(verts,[tuple(range(n)),tuple(range(4*n-1,3*n-1,-1))],key)
        if solid:
            self.collision(at,size,yaw)

    def revolve(self,at,profile,key,segments=14,axis=(0,1,0),caps=True):
        up=Vector(axis).normalized()
        side=up.cross(Vector((0,0,1))).normalized() if abs(up.z)<.93 else up.cross(Vector((1,0,0))).normalized()
        across=up.cross(side)
        verts=[]
        for height, radius in profile:
            for j in range(segments):
                angle=j*TAU/segments
                verts.append(tuple(Vector(at)+up*height+(side*math.cos(angle)+across*math.sin(angle))*radius))
        faces=[(k*segments+j,k*segments+(j+1)%segments,
                (k+1)*segments+(j+1)%segments,(k+1)*segments+j)
               for k in range(len(profile)-1) for j in range(segments)]
        self.add(verts,faces,key,smooth=True)
        if caps:
            start=segments*(len(profile)-1)
            self.add(verts,[tuple(reversed(range(segments))),tuple(range(start,start+segments))],key)

    def tube(self,a,b,r,key,sides=8,taper=1):
        direction=Vector(b)-Vector(a)
        if direction.length>.0005:
            self.revolve(a,[(0,r),(direction.length,r*taper)],key,sides,direction,caps=r>=.035)

    def beam(self,a,b,w,d,key):
        end=Vector(b)-Vector(a)
        up=end.normalized()
        x=up.cross(Vector((0,0,1))).normalized() if abs(up.z)<.95 else up.cross(Vector((1,0,0))).normalized()
        z=x.cross(up)
        center=(Vector(a)+Vector(b))*.5
        verts=[]
        for s,t,u in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            verts.append(tuple(center+x*(s*w*.5)+up*(t*end.length*.5)+z*(u*d*.5)))
        self.add(verts,[(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)],key)

    def rope(self,points,r,key,sides=6):
        verts=[]
        for i, coord in enumerate(points):
            tangent=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])).normalized()
            v=tangent.cross(Vector((0,1,0))).normalized() if abs(tangent.y)<.96 else tangent.cross(Vector((0,0,1))).normalized()
            w=tangent.cross(v)
            for j in range(sides):
                a=j*TAU/sides
                verts.append(tuple(Vector(coord)+r*(v*math.cos(a)+w*math.sin(a))))
        faces=[(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j)
               for i in range(len(points)-1) for j in range(sides)]
        self.add(verts,faces,key,smooth=True)

    def hoop(self,at,r,t,key,axis="z",segments=24):
        u=list(at)
        i,j={"x":(1,2),"y":(0,2),"z":(0,1)}[axis]
        points=[]
        for n in range(segments+1):
            a=n*TAU/segments
            v=u.copy()
            v[i]+=r*math.cos(a)
            v[j]+=r*math.sin(a)
            points.append(v)
        self.rope(points,t,key,7)

    def blob(self,at,size,key,rng=None,segments=10,rings=6,jitter=.12):
        x,y,z=at
        rx,ry,rz=size
        rows=[]
        for i in range(1,rings):
            h=i*PI/rings
            for j in range(segments):
                a=j*TAU/segments
                variation=1+(rng.uniform(-jitter,jitter) if rng else jitter*.48*math.sin(i*2.3+j*3.05))
                rows.append((x+rx*math.sin(h)*math.cos(a)*variation,y+ry*math.cos(h)*variation,
                             z+rz*math.sin(h)*math.sin(a)*variation))
        top=len(rows)
        rows.extend([(x,y+ry,z),(x,y-ry,z)])
        faces=[]
        for j in range(segments):
            k=(j+1)%segments
            last=(rings-2)*segments
            faces.append((top,j,k))
            faces.append((top+1,last+k,last+j))
            for i in range(rings-2):
                ii=i*segments
                faces.append((ii+j,ii+segments+j,ii+segments+k,ii+k))
        self.add(rows,[tuple(reversed(face)) for face in faces],key,smooth=jitter<.17)

    def sign(self,card,at,width,height,yaw=0,frame="walnut"):
        x,y,z=at
        if frame:
            self.box(at,(width+.08,height+.075,.061),frame,False,yaw)
        front=.033 if frame else 0
        vectors=[(-width/2,-height/2,front),(width/2,-height/2,front),
                 (width/2,height/2,front),(-width/2,height/2,front)]
        coords=[tuple(a+b for a,b in zip(at,rotate_y(v,yaw))) for v in vectors]
        self.quad(coords,"print",self.card_uv(card))

    def sheet(self,card,at,w,d,yaw=0):
        vectors=[(-w/2,0,d/2),(w/2,0,d/2),(w/2,0,-d/2),(-w/2,0,-d/2)]
        self.quad([tuple(a+b for a,b in zip(at,rotate_y(v,yaw))) for v in vectors],"print",self.card_uv(card))

    @staticmethod
    def card_uv(card):
        index=ATLAS[card]
        left=(index%4+.016)/4
        right=(index%4+.984)/4
        top=1-(index//4+.016)/CARD_ROWS
        bottom=1-(index//4+.984)/CARD_ROWS
        return [(left,bottom),(right,bottom),(right,top),(left,top)]

    def create(self):
        data=bpy.data.meshes.new(self.name)
        data.from_pydata(self.verts,[],self.faces)
        data.update()
        obj=bpy.data.objects.new(self.name,data)
        self.region.collection.objects.link(obj)
        obj.location=point(self.at)
        obj.rotation_euler.z=self.yaw
        keys=list(dict.fromkeys(self.keys))
        for key in keys:
            data.materials.append(mat(key))
        indices={k:i for i,k in enumerate(keys)}
        layer=data.uv_layers.new(name="UVMap")
        for polygon,key,smooth,uv in zip(data.polygons,self.keys,self.smooth,self.uv):
            polygon.material_index=indices[key]
            polygon.use_smooth=smooth
            for loop, xy in zip(polygon.loop_indices,uv):
                layer.data[loop].uv=xy
        return obj
