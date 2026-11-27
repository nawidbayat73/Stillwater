"""Paint the tileable surfaces and printed material for the rebuilt sets."""

from pathlib import Path
import argparse
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from photographic import game_maps, photo, photo_normal

# The tile size is in meters. Large grain, joints and inks stay in scale in all four sets.
SURFACES = {
    "sea_green": ("4c7774", "painted", .76, 1.8),
    "ward_red": ("874f42", "painted", .79, 1.8),
    "cream_siding": ("c2af86", "painted", .80, 1.8),
    "blue_siding": ("628394", "painted", .75, 1.8),
    "olive_siding": ("777c62", "painted", .77, 1.8),
    "garnet": ("854e4b", "painted", .75, 1.8),
    "ivory": ("d5c9a7", "painted", .66, 1.2),
    "roof_slate": ("3d4d58", "shingle", .82, 1.8),
    "roof_russet": ("695052", "shingle", .84, 1.8),
    "zinc": ("647177", "metal", .62, 1.9),
    "walnut": ("6b4935", "wood", .68, 1.35),
    "oak": ("97734c", "wood", .73, 1.55),
    "fir": ("806a50", "wood", .78, 1.75),
    "driftwood": ("766c5a", "wood", .86, 1.25),
    "parquet": ("977956", "planks", .72, 1.9),
    "plaster": ("c2b798", "plaster", .87, 1.55),
    "sage_plaster": ("939b83", "plaster", .88, 1.55),
    "wallpaper": ("b6aa88", "wallpaper", .90, 1.15),
    "brick": ("8f6657", "brick", .9, 1.35),
    "brick_dark": ("574741", "brick", .9, 1.35),
    "fieldstone": ("615e56", "stone", .83, 1.9),
    "cliff": ("444f4b", "stone", .73, 2.45),
    "wet_stone": ("3b504b", "stone", .47, 1.85),
    "moss": ("545c3d", "gravel", .94, 1.55),
    "sand": ("857e67", "gravel", .94, 1.6),
    "asphalt": ("4a5351", "gravel", .87, 1.8),
    "cobble": ("7e7d70", "cobble", .86, 1.55),
    "concrete": ("828784", "plaster", .88, 2.0),
    "floor_tile": ("b1a78b", "tile", .61, 1.25),
    "kitchen_tile": ("b0b9a7", "tile", .57, 1.10),
    "aged_steel": ("596867", "metal", .49, 1.65),
    "deep_steel": ("3c5054", "metal", .59, 1.65),
    "sand_enamel": ("a5a48b", "metal", .56, 1.65),
    "rust": ("88644a", "metal", .65, 1.65),
    "wet_iron": ("34464a", "metal", .45, 1.45),
    "canvas": ("bea889", "fabric", .92, .91),
    "blanket": ("605c6a", "fabric", .94, .83),
    "green_cloth": ("527369", "fabric", .89, .84),
    "teal_leather": ("426557", "fabric", .64, .95),
    "rouge_cloth": ("8e5847", "fabric", .89, .87),
    "linen": ("ded1b6", "fabric", .91, .90),
    "lace": ("d5c5a6", "lace", .85, .75),
    "cork": ("8f7856", "gravel", .90, .86),
    "dust": ("656a61", "plaster", .92, 1.9),
    "rug": ("787978", "rug", .92, 1.0),
    "diamond_plate": ("6b7370", "diamond", .54, 1.35),
    "bark": ("655947", "bark", .91, 1.7),
    "vehicle_paint": ("547779", "metal", .46, 2.56),
    "vehicle_cream": ("c7c2a7", "metal", .48, 2.56),
    "cargo_panel": ("88574a", "metal", .62, 1.9),
}

CARDS = [
    ("north_ward", "WARD", "HAUS 7", "SEEFUNK  •  W. WARD", "glass"),
    ("fish_sign", "Fischer & Söhne", "NORDKAI", "NETZMACHER  •  SEILEREI", "glass"),
    ("miller_sign", "Haus Miller", "UFERSTRASSE 4", "ZIMMER  •  GARTEN", "paper"),
    ("post_sign", "KÜSTENPOST", "STILLWATER", "BRIEFE  /  TELEGRAMME", "glass"),
    ("cafe_sign", "Café Morgenrot", "SEIT 1957", "KAFFEE  ·  KUCHEN  ·  BROT", "red"),
    ("library_sign", "LESESAAL", "GEMEINDE STILLWATER", "ORTSARCHIV  /  TONBÄNDER", "glass"),
    ("repair_sign", "KLEE & SOHN", "BOOTSWERKSTATT", "MOTOR  ·  SEGEL  ·  HOLZ", "red"),
    ("clock_sign", "UHRWERK WEST", "BLACKCLIFF  /  W-06", "ZUR NOTLEITUNG", "paper"),
    ("cafe_menu", "MORGENROT", "SPEISEKARTE", "KAFFEE  2,10    ZITRONENKUCHEN  3,20", "chalk"),
    ("post_hours", "ÖFFNUNGSZEITEN", "KÜSTENPOST", "MO–SA  07:00 – 12:00", "paper"),
    ("warning", "DRUCKSCHOTT", "W-06   /   GEFAHR", "BEI PEGELALARM ZURÜCKTRETEN", "red"),
    ("platform_sign", "PLATFORM 6", "NORTH SHELF RESEARCH", "SEKTION C   /   PERSONAL", "glass"),
    ("chart", "STILLWATER", "FUNKSEKTOREN  ·  1998", "W–06     NORDKAI     BLACKCLIFF", "chart"),
    ("dispatch", "PRÜFBLATT  P–2", "WARTUNG   /   18.11.", "ZULAUF ZU  ·  UMLAUF AUF  ·  START", "document"),
    ("ledger", "KUNDENBUCH", "NETZMACHEREI", "FISCHER & SÖHNE   ·   BAND 04", "document"),
    ("post_letter", "KÜSTENPOST", "18 NOV  1998", "STILLWATER  •  NORDKAI", "document"),
    ("town_print", "STILLWATER", "NORDKÜSTE", "SOMMER 1969", "ocean"),
    ("family_photo", "DEN STRAND", "WARD   •   1998", "", "photo"),
    ("old_headland", "AM KAP", "WINTER 1978", "", "ocean"),
    ("radio_book", "SEEFAHRTHANDBUCH", "NORDMEER", "W. WARD    19–11–98", "document"),
    ("lens_sign", "RESONANZKAMMER", "BLACKCLIFF  /  W–06", "DÄMPFUNG  ·  KOPPLUNG  ·  NULLSIGNAL", "glass"),
    ("breakfast", "FRISCH", "BACKSTUBE", "ZITRONE  ·  MANDEL", "paper"),
    ("pager", "KEIN DURCHGANG", "NORDKAI   /   04", "ÜBER DEN WARTUNGSSTEG", "red"),
    ("rack", "RÜCKLAUF", "SERVER  /  B–06", "BAND 11  ·  17.11.1998", "document"),
    ("landfall", "NORDKAI", "STILLWATER   /   NORDATLANTIK", "LANDGANG  ·  ZUR KÜSTENSTRASSE", "glass"),
    ("coast_guard", "KÜSTENSTRASSE", "STILLWATER", "STRASSENSPERRE   /   60 M", "paper"),
    ("archive_plate", "BEOBACHTUNG 08", "PLATFORM 6   /   17.11.1998", "NUR EINE KOPIE PRO SCHICHT", "glass"),
    ("rigel_plan", "RIGEL", "DECK B   /   LADEBUCH", "NORDATLANTIK   ·   NACHTSCHICHT", "chart"),
    ("coresheet", "W—06", "SCHALTFOLGE  /  BLACKCLIFF", "DÄMPFEN   /   KOPPELN   /   NULL", "document"),
    ("medicine", "KRANKENSTATION", "RIGEL   /   DECK B", "SANITÄTSMATERIAL   •   1998", "paper"),
    ("fuel_oil", "DIESEL", "BLACKCLIFF   /   01", "KRAFTSTOFF  ·  KEIN OFFENES LICHT", "red"),
    ("hydrophone", "LOTMESSUNG", "GEZEITENSTOLLEN   /   P–2", "SPUR I   •   16.11.1998", "document"),
    ("maritime", "KANAL 16", "NORDATLANTIK   /   04:12", "WARD   ·   FREQUENZPROTOKOLL", "glass"),
    ("closed", "GESCHLOSSEN", "HAFENAUFSICHT STILLWATER", "ANLEGEN NUR AM ROTEN LICHT", "paper"),
    ("cabins", "KOJEN 01–04", "RIGEL   /   CREW", "FREIWACHE · WINDSTÄRKE 6", "glass"),
    ("zero", "SUBJECT ZERO", "W–06   /   GEZEITENKERN", "FELDGRENZE   /   SCHALTSTELLE 3", "glass"),
]

SIZE = 384
CARD_ROWS = math.ceil(len(CARDS)/4)
PHOTO_SURFACES = {
    'painted': ('siding', .77), 'wood': ('timber', .58), 'planks': ('timber', .43),
    'stone': ('stone', .89), 'gravel': ('sand', .47), 'plaster': ('plaster', .58),
    'metal': ('metal', .60), 'brick': ('brick', .72), 'shingle': ('roof', .88), 'bark': ('bark', .91),
}
PHOTO_OVERRIDES = {
    'asphalt': ('road', .73), 'cargo_panel': ('metal', .69),
    'teal_leather': ('leather', .58), 'zinc': ('metal', .43),
    'vehicle_paint': ('metal', .16), 'vehicle_cream': ('metal', .13),
}


def tiled_noise(rng, n, height, width=None):
    width = width or height
    samples = rng.random((height, width))
    i = np.linspace(0, height, n, endpoint=False)
    j = np.linspace(0, width, n, endpoint=False)
    fy = (i % 1)[:, None]
    fx = (j % 1)[None, :]
    iy, ix = i.astype(int)[:, None], j.astype(int)[None, :]
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    return ((1-fy)*((1-fx)*samples[iy,ix]+fx*samples[iy,(ix+1)%width])
            +fy*((1-fx)*samples[(iy+1)%height,ix]+fx*samples[(iy+1)%height,(ix+1)%width]))-.5


def tile_surfaces(directory):
    y, x = np.mgrid[:SIZE, :SIZE] / SIZE
    for index, (name, (hex_color, kind, _, _)) in enumerate(SURFACES.items()):
        rng = np.random.default_rng(97006 + index)
        cloud = tiled_noise(rng, SIZE, 5)
        blot = tiled_noise(rng, SIZE, 19)
        grain = rng.uniform(-.5, .5, (SIZE, SIZE))
        detail = tiled_noise(rng, SIZE, 83)
        patina = .16*cloud+.12*blot+.20*grain
        elevation = .34*cloud+.16*blot+.07*detail
        for_ink = None
        if kind in ("wood","painted","planks"):
            fiber = tiled_noise(rng,SIZE,64,5)+tiled_noise(rng,SIZE,126,12)*.61
            rings = np.sin(math.tau*(56*y+3*cloud+.63*tiled_noise(rng,SIZE,3,8)))
            knots = np.zeros_like(x)
            for u,v in ((.23,.26),(.71,.69),(.48,.95)):
                dx = (x-u+.5)%1-.5
                dy = (y-v+.5)%1-.5
                knots += np.exp(-((dx/.14)**2+(dy/.035)**2))*(.65+.35*np.cos((dx*dx*14+dy*dy*490)*16))
            if kind=="painted":
                sizes = np.clip((detail+blot*.89+cloud*.45-.31)*2.9,0,.70)
                scratches = np.clip((fiber*.8+grain*.08+blot*.45-.35)*2.6,0,.53)
                patina=.17*fiber+.10*blot+.12*grain-.27*knots-.30*scratches
                for_ink=(sizes*.70+scratches*.52,(136,120,96))
                elevation+=.16*fiber-.14*scratches
            else:
                patina+=.25*fiber+.064*rings-.42*knots
                elevation+=.23*fiber+.1*rings
            if kind=="planks":
                row=np.floor(y*8)
                bias=(row*5%8)/8
                xx=(x+bias)%1
                seam=(np.minimum(y*8%1,1-y*8%1)<.018) | (xx<.010)
                patina += (((row*9+3)%11)-4)*.013 - seam*.38
                elevation -= seam*.19
        elif kind in ("brick","tile","cobble","shingle"):
            nx,ny={"brick":(6,12),"tile":(6,6),"cobble":(7,11),"shingle":(6,7)}[kind]
            row=np.floor(y*ny)
            tx=(x*nx+((row%2)*.5 if kind!="tile" else 0))%1
            ty=y*ny%1
            near=np.minimum(np.minimum(tx,1-tx),np.minimum(ty,1-ty))
            width=.021 if kind=="tile" else .040
            mortar=np.clip((width+.013+blot*.025-near)/(width+.010),0,1)
            stone_id=(np.floor(x*nx+(row%2)*.5)*13+row*37)%17
            patina += (stone_id-8)*.016+.14*detail
            if kind=="tile":
                ornament=np.clip((.18-(abs(tx-.5)+abs(ty-.5)))*16,0,1)
                checker=((np.floor(x*nx)+row)%2)
                patina+=.062*(checker*2-1)
                mortar += .29*ornament
            if kind=="shingle":
                patina-=ty*.16
            patina-=mortar*(.36 if kind!="brick" else .15)
            elevation += np.clip(near*8,0,.4)-mortar*.47
            grout={"shingle":(44,48,46),"brick":(113,110,96),"tile":(82,88,83),"cobble":(66,66,61)}[kind]
            for_ink=(np.clip(mortar*.75,0,.86),grout)
        elif kind in ("stone","gravel","plaster"):
            pitting = np.clip((detail*.8+grain*.46+blot*.59-.235)*2.1,0,.67)
            stain=np.clip((blot+2*cloud-.26)*.72,0,.61)
            patina+=.14*detail-.34*pitting-.23*stain
            elevation+=.21*detail-.24*pitting
            if kind=="stone":
                fault=(np.abs(cloud+blot*.64+detail*.13)<.031)
                patina+=.32*blot-.26*fault
                elevation+=.21*blot-.21*fault
                for_ink=(stain*.67,(111,110,78))
        elif kind in ("metal","diamond"):
            run=tiled_noise(rng,SIZE,6,102)+tiled_noise(rng,SIZE,19,42)*.58
            wear=np.clip((cloud*.86+blot*.62+detail*.33-.14)*1.68,0,.64)
            patina+=.21*run-.13*wear
            elevation+=.16*run-.15*wear
            for_ink=(wear*.61,(123,87,57))
            if kind=="diamond":
                phase=(np.floor(x*12)+np.floor(y*12))%2
                tx=(x*12%1-.5)
                ty=(y*12%1-.5)
                width=np.abs(tx+ty*(1-2*phase))
                bound=np.abs(ty+tx*(2*phase-1))
                lug=np.clip((.12-width)*12,0,1)*np.clip((.56-bound)*11,0,1)
                patina+=.22*lug
                elevation+=.50*lug
        elif kind in ("fabric","lace","wallpaper"):
            weave = np.sin(x*math.tau*88)*np.cos(y*math.tau*74)
            fold=np.sin(x*math.tau*7+cloud*3)*np.sin(y*math.tau*2)
            patina+=.085*weave+.071*fold
            elevation+=.09*weave+.050*fold
            if kind=="lace":
                linen=np.minimum(abs((x*8)%1-.5),abs((y*8)%1-.5))
                bloom=np.sin(x*math.tau*8)*np.sin(y*math.tau*8)
                patina+=.17*bloom-.20*np.clip((linen-.13)*4,0,.70)
            if kind=="wallpaper":
                stripe=(np.abs(x*6%1-.5)<.035)
                sprig=(abs(y*4%1-.5)+abs(x*6%1-.50)*1.9 <.15)
                for_ink=(np.clip(.56*sprig+.35*stripe,0,.7),(112,128,103))

        base=np.array([int(hex_color[i:i+2],16) for i in (0,2,4)],dtype=float)
        if for_ink is not None:
            fraction,ink=for_ink
            p=fraction[...,None]
            pixels=((1-p)*base+p*np.array(ink))*(1+patina[...,None])
        else:
            pixels=base*(1+patina[...,None])
        photograph = PHOTO_OVERRIDES.get(name, PHOTO_SURFACES.get(kind))
        if photograph:
            texture, weight = photograph
            fine, chroma = photo(texture,SIZE)
            dyed=base*(1+.91*fine[...,None])+.19*chroma
            pixels=pixels*(1-weight)+dyed*weight
        Image.fromarray(np.uint8(np.clip(pixels,0,255))).save(directory/f"{name}.jpg",quality=91,subsampling=0,optimize=True)
        if photograph or kind not in ("fabric","lace","wallpaper","rug","shingle"):
            dx=(np.roll(elevation,-1,1)-np.roll(elevation,1,1))*1.65
            dy=(np.roll(elevation,-1,0)-np.roll(elevation,1,0))*1.65
            normal=np.stack((-dx,dy,np.ones_like(dx)),axis=-1)
            if photograph:
                scanned=photo_normal(texture,SIZE)
                normal=normal*(1-weight)+scanned*weight
            normal=normal/np.sqrt((normal**2).sum(axis=2,keepdims=True))
            Image.fromarray(np.uint8(np.clip(normal*.5*255+127.5,0,255))).save(directory/f"{name}_n.png",optimize=True)


def font(size, face):
    directory = Path("/usr/share/fonts/truetype/dejavu")
    filename = {"serif":"DejaVuSerif-Bold.ttf","mono":"DejaVuSansMono.ttf","sans":"DejaVuSans-Bold.ttf"}[face]
    return ImageFont.truetype(str(directory/filename),size)


def ink_title(draw, text, y, color, size, face="serif", width=360):
    if not text:
        return
    letter = font(size,face)
    while draw.textlength(text,font=letter)>width and size>8:
        size-=1
        letter=font(size,face)
    draw.text((192,y),text,font=letter,fill=color,anchor="mm")


def coastal_print(draw, style, rng):
    for y in range(35,166):
        depth=(y-35)/130
        draw.line((26,y,358,y), fill=(int(154-depth*68),int(159-depth*57),int(146-depth*48)))
    draw.polygon([(26,122),(69,113),(85,102),(123,99),(150,116),(186,125),(26,143)], fill=(80,86,77))
    draw.polygon([(242,125),(266,115),(293,96),(321,99),(358,114),(358,142)], fill=(89,99,94))
    if style!="photo":
        draw.polygon([(98,104),(102,67),(111,67),(115,105)],fill=(186,180,155))
        draw.polygon([(98,67),(105,60),(113,67)],fill=(91,72,62))
        draw.rectangle((103,73,107,78),fill=(47,60,60))
    draw.polygon([(26,151),(73,146),(119,153),(175,161),(228,163),(253,154),(300,153),(358,149),(358,169),(26,169)],fill=(152,140,113))
    for _ in range(115):
        x,y=(int(rng.integers(27,350)),int(rng.integers(126,153)))
        draw.line((x,y,x+int(rng.integers(2,8)),y),fill=(118,128,123))
    if style=="photo":
        for x,y,h in [(172,161,70),(201,164,62),(228,166,43)]:
            draw.ellipse((x-6,y-h-12,x+6,y-h+2),fill=(81,70,59))
            draw.polygon([(x-8,y-h),(x+8,y-h),(x+11,y-21),(x-9,y-21)],fill=(91,90,74))
            draw.line((x-4,y-24,x-5,y),fill=(59,62,57),width=5)
            draw.line((x+5,y-24,x+7,y),fill=(63,60,52),width=5)


def print_cards(directory):
    rng=np.random.default_rng(59146)
    styles={
        "glass":((40,78,73),(236,222,182)),
        "chalk":((34,48,46),(226,210,174)),
        "red":((103,64,55),(234,217,178)),
        "paper":((204,188,151),(58,74,69)),
        "chart":((183,185,147),(58,79,71)),
        "document":((201,185,148),(83,78,55)),
    }
    atlas=Image.new("RGB",(384*4,192*CARD_ROWS),(54,65,62))
    for index,(name,title,heading,foot,style) in enumerate(CARDS):
        bg,fg=styles.get(style,((200,183,149),(64,70,65)))
        card=Image.new("RGB",(384,192),bg)
        draw=ImageDraw.Draw(card)
        draw.rounded_rectangle((8,8,375,183),radius=7,outline=fg,width=1)
        draw.rectangle((15,15,368,176),outline=fg,width=1)
        if style in ("photo","ocean"):
            coastal_print(draw,style,rng)
            ink_title(draw,title,20,fg,12,"mono")
            ink_title(draw,heading,174,fg,11,"mono")
        else:
            ink_title(draw,heading,39,fg,18,"mono")
            ink_title(draw,title,89,fg,42,"serif" if style!="chart" else "sans")
            ink_title(draw,foot,148,fg,17,"mono")
            draw.line((43,119,340,119),fill=fg,width=1)
            if style in ("document","chart"):
                for x in range(30,355,21):
                    draw.line((x,23,x,162),fill=tuple(int(v*.92) for v in bg),width=1)
                ink_title(draw,title,89,fg,36,"serif")
            else:
                for x in (23,360):
                    for y in (23,169):
                        draw.ellipse((x-3,y-3,x+3,y+3),fill=(135,124,102))
        array=np.asarray(card).astype(float)
        fine=rng.normal(0,2.8,(192,384,1))
        fade=np.asarray(Image.fromarray(np.uint8(rng.uniform(0,255,(8,14)))).resize((384,192),Image.Resampling.BICUBIC)).astype(float)
        worn=Image.fromarray(np.uint8(np.clip(array*(.91+fade[...,None]*.00058)+fine,0,255)))
        atlas.paste(worn,((index%4)*384,(index//4)*192))
    atlas.save(directory/"lettering.jpg",quality=92,subsampling=0,optimize=True)


def make_rug(directory):
    w,h=448,640
    y,x=np.mgrid[:h,:w]
    dx=np.minimum(x,w-1-x)
    dy=np.minimum(y,h-1-y)
    d=np.minimum(dx,dy)
    rng=np.random.default_rng(777)
    background=np.zeros((h,w,3))
    background[:]=[63,89,83]
    for edge in range(12,77,16):
        band=(d>=edge)&(d<edge+5)
        background[band]=[168,135,86] if edge%3 else [114,74,66]
    braid=(np.abs((dx+dy)%20-10)<2)&(d>=38)&(d<54)
    background[braid]=[184,147,105]
    stagger=(np.floor(x/57)+np.floor(y/68)*.5)
    medallion=(abs((stagger%1)-.5)+.66*abs((y/68%1)-.5)<.21)&(d>89)
    background[medallion]=[125,118,82]
    weave=(np.sin(x*2.2)*np.cos(y*2.31)+rng.normal(0,1,(h,w)))*4.8
    Image.fromarray(np.uint8(np.clip(background+weave[...,None],0,255))).save(directory/"rug.jpg",quality=92,subsampling=0,optimize=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--game-maps",type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    tile_surfaces(args.output)
    print_cards(args.output)
    make_rug(args.output)
    if args.game_maps:
        game_maps(args.game_maps)


if __name__=="__main__":
    main()
