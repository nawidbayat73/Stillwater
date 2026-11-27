"""Props and set construction for the original route and the reconstructed later chapters."""

from __future__ import annotations
import math
import random

from mesh import PI, TAU, Set, rotate_y
from shore import (
    barrel, book, boot_pair, cabinet, chair, clock_dial, coil, crate, cup, desk_lamp, dish,
    gear, grass, hooks, lamp, net_panel, picture, shelf, stacks, stool, tape_deck,
    table, paving, railing, plant, stovepipe,
)


def fixture(m, at, glow="bulb", power=1.35, reach=7.0, color="#ffc89b", yaw=0, shadow=False):
    x,y,z=at
    m.box((x,y+.072,z),(.32,.13,.23),"deep_steel",False,yaw)
    m.revolve((x,y-.021,z),[(0,.105),(.066,.139),(.112,.116)],"zinc",14)
    m.revolve((x,y-.195,z),[(0,.049),(.055,.088),(.186,.093)],glow,12)
    for i in range(6):
        a=i*TAU/6
        dx,dz=math.cos(a)*.098,math.sin(a)*.098
        m.tube((x+dx*.63,y-.201,z+dz*.63),(x+dx,y-.03,z+dz),.009,"aged_steel",6)
    m.hoop((x,y-.14,z),.09,.010,"aged_steel","y",16)
    m.light((x,y-.25,z+.07),color,power,reach,shadow)


def meter(m,x,y,z,r=.11,shell="brass",face="porcelain",phase=.7):
    m.revolve((x,y,z),[(0,r*.97),(.020,r*1.10),(.043,r),(.052,r*.94)],shell,20,(0,0,1))
    m.revolve((x,y,z+.052),[(0,.84*r),(.005,.84*r)],face,20,(0,0,1))
    for j in range(11):
        a=PI*(-.76+j*.152)
        m.tube((x+r*.62*math.sin(a),y+r*.62*math.cos(a),z+.059),
            (x+r*.75*math.sin(a),y+r*.75*math.cos(a),z+.059),r*.034,"ink",6)
    m.tube((x,y,z+.068),(x+r*.68*math.sin(phase),y+r*.68*math.cos(phase),z+.068),r*.039,"ceramic_red",7)
    m.blob((x,y,z+.068),(r*.073,r*.073,.013),"brass",segments=8,rings=4)


def crt(m,x,y,z,scale=.68,tag=0):
    m.soft((x,y+.264*scale,z),(.79*scale,.54*scale,.51*scale),"deep_steel",.049)
    m.soft((x-.026*scale,y+.293*scale,z+.261*scale),(.678*scale,.386*scale,.055*scale),"coal",.020)
    m.soft((x-.026*scale,y+.293*scale,z+.287*scale),(.593*scale,.294*scale,.035*scale),"dark_crt",.014)
    line=[]
    for j in range(39):
        t=j/38
        line.append((x+(-.294+.539*t)*scale,y+(.298+.095*math.sin(t*38+tag)*(1-(2*t-1)**4))*scale,z+.308*scale))
    m.rope(line,.0045*scale,"crt_light",5)
    for j in range(6):
        m.box((x+.313*scale,y+(.15+j*.054)*scale,z+.264*scale),(.042*scale,.020*scale,.013*scale),"aged_steel")
    m.box((x+.197*scale,y+.084*scale,z+.271*scale),(.054*scale,.018*scale,.015*scale),"signal")
    for j in range(6):
        m.box((x+(-.28+j*.10)*scale,y+.541*scale,z-.128*scale),(.061*scale,.013*scale,.089*scale),"coal")


def service_panel(m,x,y,z,width=1.08,depth=.36,height=1.13,accent="deep_steel"):
    m.soft((x,y+height*.47,z),(width,height*.94,depth),"aged_steel",.054)
    m.box((x,y+.071,z),(width+.14,.142,depth+.11),"wet_iron")
    m.box((x,y+height*.32,z+depth*.51),(width*.70,height*.39,.048),accent)
    m.box((x,y+height*.79,z+depth*.53),(width*.89,height*.32,.048),"deep_steel")
    m.box((x,y+height*.81,z+depth*.616),(width*.49,height*.16,.026),"dark_crt")
    for col in range(8):
        m.box((x+width*(-.22+col*.057),y+.83*height,z+depth*.649),(.012,height*(.024+.052*abs(math.sin(1.3*col))),.016),"volt")
    for sx in (-1,1):
        xx=x+sx*width*.335
        m.revolve((xx,y+height*.80,z+depth*.63),[(0,.038),(.025,.033)],"brass",10,(0,0,1))
        m.revolve((xx,y+height*.67,z+depth*.63),[(0,.022),(.018,.022)],"signal" if sx==-1 else "amber",12,(0,0,1))
        for row in range(8):
            yy=y+(.17+row*.040)*height
            m.box((xx-sx*.115,yy,z+depth*.59),(width*.23,.013,.012),"coal")
    for side in (-1,1):
        for j in range(4):
            m.revolve((x+side*width*.443,y+height*(.13+.24*j),z+depth*.514),[(0,.012),(.011,.012)],"chrome",7,(0,0,1))


def emergency_beacon(m,x,y,z,red=True,small=False):
    scale=.50 if small else 1.0
    m.revolve((x,y,z),[(0,.179*scale),(.08*scale,.182*scale),(.18*scale,.124*scale),
        (.313*scale,.096*scale)],"aged_steel",16)
    m.revolve((x,y+.223*scale,z),[(0,.102*scale),(.075*scale,.105*scale),(.126*scale,.070*scale)],
              "signal" if red else "bulb",16)
    for j in range(7):
        a=j*TAU/7
        dx,dz=math.sin(a)*.115*scale,math.cos(a)*.115*scale
        m.tube((x+dx,y+.213*scale,z+dz),(x+dx*.7,y+.36*scale,z+dz*.7),.009*scale,"wet_iron",6)
    m.light((x,y+.47*scale,z),"#ee624c" if red else "#f7c58b",1.30 if red else .94,4.2 if small else 6.4,False)


def case(m,x,y,z,w=.56,d=.37,h=.25,material="deep_steel",yaw=0,solid=False):
    def at(dx,dy,dz):
        xx,yy,zz=rotate_y((dx,dy,dz),yaw)
        return x+xx,y+yy,z+zz
    m.soft(at(0,h*.52,0),(w,h,d),material,.039,yaw)
    m.box(at(0,h*.69,0),(w+.016,.025,d+.011),"chrome",yaw=yaw)
    for side in (-1,1):
        m.box(at(side*w*.33,h*.69,d*.515),(.033,.072,.016),"brass",False,yaw)
    points=[at(-w*.119,h*.42,d*.53),at(-w*.14,h*.31,d*.61),at(w*.14,h*.31,d*.61),at(w*.119,h*.42,d*.53)]
    m.rope(points,.017,"tar",7)
    if solid:
        m.collision(at(0,h*.52,0),(w,h,d),yaw)


def mooring_pile(m,x,z,y_base=-1.50):
    m.tube((x,y_base,z),(x,.69,z),.146,"driftwood",10,.895)
    m.tube((x,.622,z),(x,.683,z),.170,"zinc",12)
    m.revolve((x,.227,z),[(0,.166),(.101,.166)],"rope",12)
    for j in range(4):
        m.hoop((x,.255+j*.029,z),.166,.014,"rope","y",19)
    m.collision((x,.31,z),(.265,.75,.265))


def arrival():
    launch=Set("launch")
    m=launch.mesh("Steuerstand, Seefunk und Maras Karte")
    # Local coordinates follow the launch as it crosses the bay.
    m.box((.032,.79,-.049),(.43,.062,.322),"oak",False,.06)
    m.sheet("maritime",(.023,.823,-.054),.333,.234,.06)
    m.sheet("family_photo",(-.110,.827,.055),.167,.117,-.13)
    m.beam((.138,.83,-.153),(.202,.83,.033),.011,.011,"brass")
    m.soft((-.577,.894,.21),(.162,.087,.082),"deep_steel",.019)
    m.box((-.581,.924,.264),(.081,.015,.027),"brass")
    m.rope([(-.619,.859,.12),(-.656,.783,.096),(-.621,.648,.080),(-.484,.643,.429)],.009,"tar",8)
    m.tube((-.427,1.010,.544),(-.431,1.217,.547),.009,"chrome",9)
    m.revolve((-.429,1.005,.544),[(0,.028),(.015,.026)],"tar",11)
    meter(m,.388,.774,.056,.091,face="glass_amber",phase=.44)
    meter(m,.556,.738,.017,.063,face="glass_green",phase=-.53)
    for i in range(3):
        m.box((.267+.082*i,.729,.194),(.058,.037,.023),"amber" if i==1 else "tar")
    case(m,.56,.246,-1.52,.53,.37,.30,"garnet",.143)
    case(m,-.48,.319,1.29,.47,.31,.21,"sea_green",.235)
    coil(m,-.49,.354,1.60,.183,.018,5)
    m.revolve((.513,.360,1.647),[(0,.08),(.098,.082),(.131,.046)],"brass",14)
    m.revolve((.513,.469,1.647),[(0,.045),(.16,.037)],"glass_amber",12)
    m.light((.517,.68,1.646),"#ffac62",1.0,4.4,False)
    m.light((-.25,1.21,-.086),"#ffc387",1.28,3.0,False)
    m.light((-.31,1.19,.481),"#91cabe",.45,2.1,False)

    coast=Set("landfall")
    m=coast.mesh("Rote Hafenmarke und Landgang")
    for x,z in [(26.17,-15.41),(26.04,-13.72),(24.05,-15.40),(24.11,-13.73),(21.72,-15.42),(21.91,-13.63)]:
        mooring_pile(m,x,z)
    for x,z in [(25.41,-15.35),(23.93,-13.70),(22.69,-15.26)]:
        m.box((x,.095,z),(.33,.134,.224),"wet_iron")
        m.tube((x-.11,.144,z),(x+.11,.144,z),.041,"zinc",10)
        m.revolve((x,.099,z),[(0,.052),(.113,.049)],"aged_steel",12)
    coil(m,25.10,.102,-15.10,.183,.018,4)
    m.box((25.68,.768,-15.40),(.236,.102,.236),"wet_iron")
    emergency_beacon(m,25.68,.816,-15.40)
    # A tall pinned sign faces the camera across the water and leaves the exit clear.
    m.box((21.27,1.053,-15.52),(.169,2.14,.169),"walnut")
    m.sign("landfall",(21.15,1.518,-15.55),1.49,.60,PI/2)
    fixture(m,(21.27,2.12,-15.54),"bulb",2.05,8.5,shadow=True)
    m.sign("coast_guard",(18.28,1.22,-14.19),1.45,.56,PI/2)
    m.box((18.17,.60,-14.19),(.115,1.22,.121),"fir")
    for z in (-15.03,-13.86):
        for index in range(12):
            x=18.7+.65*index
            m.box((x,.070,z),(.36,.025,.062),"hazard" if index%4 else "ivory")
    for at in [(17.94,2.90,-16.41),(17.15,2.91,-8.98),(16.66,2.84,-20.29),(12.14,2.18,-12.08)]:
        fixture(m,at,"bulb",1.6,8.6,shadow=False)
    for x,z in [(22.34,-12.5),(24.6,-18.12),(30.61,-22.05),(39.49,-11.18)]:
        m.tube((x,-1.1,z),(x,.10,z),.146,"driftwood",10,.89)
        m.hoop((x,-.28,z),.174,.044,"moss","y")
    fence=coast.mesh("Bojen, Untiefen und Netzkisten")
    for p in [(38.1,-10.87),(33.26,-17.99),(24.5,-18.19)]:
        x,z=p
        fence.revolve((x,-.57,z),[(0,.24),(.045,.365),(.315,.291),(.467,.139),(.522,.118)],"garnet",20)
        fence.hoop((x,-.044,z),.08,.025,"brass","y")
        fence.tube((x,-.316,z),(x,-.163,z),.281,"ivory",20)
    for x,z in [(19.36,-17.19),(18.73,-17.91),(17.86,-11.12),(18.78,-10.32),(21.07,-15.01)]:
        crate(fence,x,.027,z,.65,.43,.325,"driftwood",True)
        coil(fence,x,.374,z,.19,.014,4)
    rnd=random.Random(33027)
    for x,z in [(20.5,-11.6),(21.4,-10.5),(20.4,-16.2),(21.4,-17.2),(18.7,-9.99),(19.9,-18.22)]:
        fence.blob((x,-.49,z),(rnd.uniform(.42,1.07),rnd.uniform(.44,.72),rnd.uniform(.54,.86)),"wet_stone",rnd,11,5,.20)
    return [launch,coast]


def original_village():
    region=Set("chapter1")
    street=region.mesh("Hafendorf und Straße")
    for x,z in [(-3.54,14.39),(-4.17,10.28),(-3.91,2.54),(3.93,3.25),(-3.57,-8.23),
                (4.15,-11.33),(5.68,-19.92),(5.42,-26.38),(-3.96,-17.8),(-3.65,-29.5)]:
        rnd=random.Random(round(x*115-z*371))
        for i in range(6):
            grass(street,x+rnd.uniform(-.32,.32),.016,z+.42*i,rnd,.71)
        street.box((x,.049,z),(.236,.123,.74),"fieldstone",False,.03)
    for x,z in [(-4.5,12.06),(-5.4,9.89),(5.40,-1.14),(6.40,3.49),(5.43,-23.68),
                (7.9,-25.9),(20.9,-22.3),(23.1,-25.15),(-3.11,-31.8)]:
        barrel(street,x,.023,z,.213,.574,"driftwood")
        if x>5:
            coil(street,x-.226,.052,z+.145,.193,.019,4)
    street.sign("coast_guard",(-3.41,1.168,1.60),.83,.48,PI/2)
    street.box((-3.43,.60,1.61),(.096,1.21,.102),"walnut",True)
    for x,z in [(-3.65,11.7),(5.51,-9.55),(4.94,-22.11)]:
        fixture(street,(x,2.47,z),"bulb",1.5,6.35,shadow=False)
        street.box((x,1.21,z),(.13,2.38,.145),"driftwood",True)
    # A practical fixing station occupies a quiet corner of the net shed yard.
    table(street,17.28,-27.05,1.80,.67,.772,"driftwood")
    net_panel(street,17.17,1.83,-27.75,1.91,1.21,.162,9,13)
    street.box((16.24,.987,-27.77),(.10,1.965,.139),"walnut")
    street.box((18.11,.987,-27.77),(.10,1.965,.139),"walnut")
    coil(street,17.09,.831,-26.96,.254,.018,4)
    case(street,17.64,.831,-27.03,.41,.26,.175,"deep_steel")
    store=region.mesh("Laden und Lotsenbüro")
    # Wall furnishings stay clear of the original key, fuse, switches and dialogue targets.
    for x,z,top in [(6.83,1.66,1.063),(7.21,.92,1.05),(6.85,1.08,1.05)]:
        case(store,x,top,z,.244,.213,.138,"sea_green",-.41)
    store.sign("post_hours",(6.443,1.95,-4.94),.62,.39,-PI/2,frame="walnut")
    store.sign("closed",(10.85,2.06,-18.48),.79,.49,PI)
    for x,z in [(10.98,-26.35),(11.51,-26.14),(10.34,-26.49)]:
        stacks(store,x,z,.205,.843,3)
    store.sign("chart",(3.18,1.66,-37.95),.94,.61)
    store.sign("post_letter",(.632,1.632,-37.95),.44,.30)
    store.sheet("rigel_plan",(2.55,.951,-37.19),.395,.258,-.44)
    cup(store,1.44,.949,-37.31,"ceramic_blue")
    desk_lamp(store,2.55,.932,-37.42)
    fixture(store,(1.97,2.16,-33.86),"bulb",.79,4.78)
    return region


def blackcliff():
    region=Set("chapter2")
    cliff=region.mesh("Blackcliff, Pfad und Funkwarte")
    # Wind-shorn grass and scree line the existing walkable approach.
    rng=random.Random(81032)
    approach=[(11.48,.18,-44.4),(14.86,.56,-46.44),(18.88,.89,-47.38),(24.76,1.52,-48.36),
              (28.73,2.25,-49.48),(30.53,3.289,-51.06),(32.33,4.329,-52.64),(34.13,5.368,-54.22)]
    for i,(x,y,z) in enumerate(approach):
        for j in range(9):
            xx=x+rng.uniform(-.50,.66)
            zz=z+rng.choice([-1,1])*rng.uniform(1.23,1.66)
            grass(cliff,xx,y-.045,zz,rng,rng.uniform(.59,1.08))
            cliff.blob((xx,y-.077,zz),(.149,.108,.183),"cliff",rng,8,4,.20)
        if i in (1,3,5,7):
            cliff.box((x-.21,y+.41,z+1.15),(.112,.83,.139),"driftwood")
            emergency_beacon(cliff,x-.21,y+.82,z+1.145,False,True)
    cliff.sign("fuel_oil",(34.266,6.66,-49.92),.61,.43,PI/2,"aged_steel")
    cliff.sign("coresheet",(40.806,6.76,-56.13),.69,.56,-PI/2)
    barrel(cliff,38.26,5.357,-53.95,.255,.65,"aged_steel")
    cliff.collision((38.26,5.681,-53.95),(.44,.65,.44))
    coil(cliff,38.27,6.023,-53.94,.208,.018,4)
    crate(cliff,35.41,5.365,-54.46,.64,.39,.36,"driftwood",True)
    fixture(cliff,(36.103,7.61,-53.95),"bulb",1.60,6.9)
    fixture(cliff,(42.976,7.42,-50.42),"bulb",1.51,6.2)
    fixture(cliff,(50.02,3.10,-32.91),"bulb",1.47,6.5)
    for i,(x,y,z) in enumerate([(50.36,5.36,-47.01),(47.22,3.96,-41.39),(42.47,3.1,-39.12),(47.4,1.21,-34.0)]):
        cliff.box((x,y+.38,z),(.105,.75,.105),"deep_steel")
        emergency_beacon(cliff,x,y+.75,z,False,True)

    rooms=region.mesh("Wärterhaus, Maschinenraum und Suchlicht")
    rooms.sign("old_headland",(36.285,6.883,-59.401),.67,.45,0)
    rooms.sign("chart",(35.16,6.734,-57.42),.47,.36,PI/2)
    cup(rooms,36.115,6.278,-58.23,"ceramic_blue")
    case(rooms,39.29,5.39,-57.78,.48,.29,.25,"sea_green",.34,True)
    boot_pair_at(rooms,39.81,5.376,-54.39)
    rooms.hoop((35.27,6.60,-49.611),.22,.048,"rope",segments=20)
    meter(rooms,38.055,6.623,-51.139,.163,face="glass_amber",phase=-.63)
    meter(rooms,38.438,6.613,-51.139,.122,face="glass_amber",phase=.88)
    rooms.rope([(38.05,6.55,-51.194),(38.03,5.99,-51.21),(37.87,5.77,-50.81),
        (37.25,5.77,-50.74)],.031,"copper",8)
    case(rooms,35.002,5.39,-50.96,.55,.31,.23,"garnet",.27,True)
    fixture(rooms,(37.47,7.31,-49.80),"bulb",1.12,5.4)
    rooms.sign("coresheet",(44.68,14.156,-54.73),.64,.49,0,"aged_steel")
    rooms.hoop((44.05,13.214,-53.15),2.09,.022,"brass","y",44)
    for i in range(16):
        a=TAU*i/16
        x,z=44.05+2.40*math.sin(a),-53.15+2.40*math.cos(a)
        rooms.box((x,13.28,z),(.14,.139,.14),"brass",False,-a)
    for x,y,z in [(43.14,15.41,-50.70),(45.92,14.77,-54.88)]:
        fixture(rooms,(x,y,z),"glass_amber",.86,4.6)
    rooms.sign("rigel_plan",(51.80,2.262,-36.265),.94,.57,0)
    rooms.sign("post_letter",(52.89,2.33,-36.26),.30,.231,.01)
    cup(rooms,51.96,1.883,-35.42,"ceramic_blue")
    stacks(rooms,53.27,-35.324,.23,1.879,3)
    rooms.sheet("dispatch",(51.83,1.891,-35.37),.31,.192,-.17)
    fixture(rooms,(52.64,3.128,-35.18),"bulb",1.37,5.8)
    return region


def boot_pair_at(region,x,y,z):
    obj=region.region.mesh("Stiefel am Eingang",(x,y,z),0)
    boot_pair(obj,0,0)


def ship():
    region=Set("chapter3")
    deck=region.mesh("RIGEL, Backbord und Ladedeck")
    for x,y,z in [(56.10,2.27,-32.89),(65.87,4.21,-34.72),(70.21,5.05,-42.34),
                (79.49,4.96,-40.84),(76.61,4.96,-47.32),(72.88,5.03,-47.01)]:
        fixture(deck,(x,y,z),"bulb",1.8,8.9,shadow=False)
    for y,z in [(2.66,-35.09),(2.73,-22.28),(2.68,-31.74)]:
        coil(deck,67.72,y,z,.25,.023,5)
    case(deck,69.05,2.56,-34.26,.82,.43,.380,"sea_green",.083,True)
    case(deck,66.42,2.58,-23.23,.83,.50,.44,"rust",.211,True)
    deck.sign("rigel_plan",(73.39,4.44,-39.45),.82,.48,0,"deep_steel")
    for x in (66.95,68.01,75.32,78.38,80.23):
        for j in range(9):
            deck.box((x+.05*j,2.574,-37.24),(.034,.013,.22),"hazard",False,.39)
    # Interior details attach to the corresponding reality while the floor stays untouched.
    crew=region.mesh("RigelCrew")
    crew.sign("cabins",(71.03,4.41,-45.527),.62,.42,0)
    crew.sign("post_letter",(71.009,4.01,-43.46),.38,.28,0)
    crew.box((72.40,2.568,-44.34),(1.81,.027,.61),"rug")
    for j in range(3):
        case(crew,70.7,2.59+.21*j,-45.13,.51,.36,.185,"canvas",(.11-.12*j))
    cup(crew,71.54,3.501,-43.24,"porcelain")
    bottle_at(crew,71.82,3.508,-43.34)
    fixture(crew,(72.82,4.86,-42.49),"bulb",1.4,6.7)
    fixture(crew,(77.02,4.79,-46.12),"bulb",1.25,5.9)
    bridge=region.mesh("RigelBridge")
    bridge.sign("chart",(72.67,6.772,-48.16),.68,.43,0,"walnut")
    bridge.sign("rigel_plan",(74.96,7.15,-48.147),.81,.47,0,"aged_steel")
    bridge.box((71.98,5.462,-46.76),(2.29,.027,1.49),"deep_steel")
    for i in range(8):
        bridge.box((70.95+i*.29,5.482,-46.05),(.14,.014,.044),"hazard")
    bridge.soft((71.64,5.82,-47.85),(1.80,.71,.48),"aged_steel",.056,solid=True)
    bridge.box((71.64,6.199,-47.819),(1.91,.085,.64),"deep_steel")
    bridge.box((71.61,6.249,-47.68),(1.73,.029,.31),"oak")
    for x in (71.12,72.19):
        bridge.box((x,5.82,-47.59),(.78,.48,.05),"sea_green")
        for row in range(6):
            bridge.box((x,5.73+row*.046,-47.556),(.46,.017,.015),"coal")
    bridge.soft((77.83,5.82,-47.79),(1.08,.71,.58),"aged_steel",.051,solid=True)
    bridge.box((77.82,6.23,-47.80),(1.17,.062,.67),"deep_steel")
    crt(bridge,77.66,6.262,-47.811,.86,19)
    for i in range(4):
        bridge.box((77.34+i*.173,6.281,-47.538),(.058,.018,.049),"ceramic_red" if i==0 else "amber")
    bridge.sheet("dispatch",(78.18,6.267,-47.64),.206,.206,.23)
    cup(bridge,78.25,6.271,-47.86,"ceramic_blue")
    bridge.tube((77.99,5.43,-47.34),(77.99,6.32,-47.34),.026,"brass",12)
    for z in (-44.34,-45.69,-46.37):
        bridge.soft((78.67,5.715,z),(.32,.55,.59),"sea_green",.050,solid=True)
        bridge.box((78.45,5.535,z),(.145,.25,.55),"aged_steel")
    for x,z in [(71.68,-47.82),(72.28,-47.82)]:
        crt(bridge,x,6.372,z,.59,round(x*166))
    bridge.box((71.80,6.352,-47.73),(.56,.024,.181),"oak")
    bridge.sheet("maritime",(71.76,6.367,-47.68),.278,.155,-.19)
    meter(bridge,77.84,7.01,-47.82,.123,face="glass_green")
    for j in range(3):
        meter(bridge,75.23+j*.26,6.877,-48.23,.098,face="glass_amber",phase=-1.12+.71*j)
    fixture(bridge,(72.84,7.625,-44.54),"glass_amber",.78,6.9)
    fixture(bridge,(77.38,7.60,-46.72),"volt",1.14,6.9,color="#adcbc1")
    bridge.light((71.64,6.79,-47.14),"#efc28f",1.67,5.42,False)
    bridge.light((77.62,6.61,-47.17),"#82bab0",1.35,4.85,False)
    machines=region.mesh("RigelEngine")
    machines.sign("fuel_oil",(73.61,1.93,-49.12),.69,.381,0,"aged_steel")
    for x in (73.35,73.73,74.12):
        meter(machines,x,1.67,-49.06,.090,shell="chrome",face="glass_amber",phase=.75*(x%1))
        machines.rope([(x,1.61,-49.06),(x,1.40,-49.1),(x+.07,1.19,-49.26),(x+.19,1.09,-49.55)],.020,"copper",7)
    fixture(machines,(73.75,2.01,-47.31),"bulb",.97,5.7)
    hold=region.mesh("RigelHold")
    for z in (-22.42,-19.19,-15.50):
        fixture(hold,(72.48,2.06,z),"glass_amber",1.37,5.55,color="#ebaa73")
    for x,z in [(71.5,-22.96),(72.2,-22.99),(77.28,-14.98)]:
        crate(hold,x,.046,z,.57,.37,.32,"driftwood",True)
        coil(hold,x+.09,.387,z,.154,.016,3)
    hold.sign("rigel_plan",(76.88,1.266,-13.886),.71,.35,PI)
    hold.sheet("maritime",(75.87,.972,-14.62),.235,.384,-.14)

    medic=Set("rigel_medic")
    m=medic.mesh("Krankenstation 1998")
    m.sign("medicine",(70.36,1.728,-35.93),.74,.43)
    for i in range(5):
        bottle_at(m,69.348+.19*i,1.01,-34.31,"glass_green" if i%2 else "glass_amber")
    m.box((69.59,.991,-34.28),(.92,.035,.339),"chrome")
    case(m,69.71,1.017,-34.48,.36,.26,.10,"porcelain",.18)
    m.tube((69.37,.048,-34.77),(69.35,1.989,-34.78),.028,"chrome",10)
    m.hoop((69.35,1.91,-34.78),.105,.020,"chrome")
    m.soft((69.46,1.65,-34.776),(.115,.24,.053),"glass_amber",.037)
    m.rope([(69.43,1.563,-34.79),(69.44,1.27,-34.73),(69.54,.99,-34.60)],.006,"rope",6)
    return [region,medic]


def bottle_at(m,x,y,z,color="glass_green"):
    m.revolve((x,y,z),[(0,.048),(.028,.050),(.167,.045),(.192,.023),(.249,.024),(.268,.035)],color,12)
    m.revolve((x,y+.104,z),[(0,.050),(.046,.051)],"paper",12,caps=False)


def cave():
    region=Set("chapter4")
    m=region.mesh("Gezeitenstollen, Felsgewölbe und Treibholz")
    rng=random.Random(16111998)
    rings=[]
    lengthwise,across=52,34
    for i in range(lengthwise):
        z=12.67-i*59.2/(lengthwise-1)
        z_phase=math.sin(z*.19)
        profile=[]
        for j in range(across+1):
            a=j*PI/across
            rib=.27*math.sin(j*.58+z*.22)+.19*math.cos(j*1.9-z*.34)
            rx=8.13+.52*z_phase+rib*.7+rng.uniform(-.15,.22)
            height=4.11+.65*math.cos(z*.22)+rib+rng.uniform(-.11,.13)
            profile.append((rx*math.cos(a)-.19*math.sin(z*.12),
                            -.24+height*math.sin(a)+.16*math.cos(a*5+z*.24),
                            z+rng.uniform(-.16,.16)))
        rings.append(profile)
    for i in range(len(rings)-1):
        for j in range(across):
            a,b,c,d=rings[i][j],rings[i][j+1],rings[i+1][j+1],rings[i+1][j]
            m.add([a,b,c,d],[(0,1,2),(0,2,3)],"wet_stone" if (j//3+i//5)%4 else "cliff")
    m.box((0,-.25,-17),(17,.50,59),"wet_stone",True)
    m.box((0,2.4,12.62),(17,4.8,.43),"wet_stone",True)
    m.box((0,2.4,-46.31),(17,4.8,.47),"cliff",True)
    for s in (-1,1):
        m.collision((s*7.9,2.3,-17),(.6,5,60))
        for i in range(38):
            z=rng.uniform(-45.5,11.9)
            x=s*rng.uniform(6.68,8.13)
            h=rng.uniform(.35,1.36)
            rx,rz=rng.uniform(.55,1.18),rng.uniform(.47,1.58)
            m.blob((x,.26+h*.36,z),(rx,h,rz),"wet_stone" if i%3 else "cliff",rng,12,7,.23)
            if h>.72:
                m.collision((x,.26+h*.34,z),(rx*1.37,h*1.19,rz*1.35))
            if i%2==0:
                ridge=s*rng.uniform(2.8,5.56)
                y=3.74-.48*abs(ridge/5)+.43*math.sin(z*.25)
                m.revolve((ridge,y-.26,z),[(-.82,.012),(-.48,.061),(-.27,.131),(.11,.191),(.42,.28)],
                          "wet_stone",8)
    for z in (8.5,3.87,-3.9,-11.4,-20,-22.4,-31.0,-40.8):
        for x in (-6.41,6.27):
            m.beam((x+.08,-.08,z),(x,3.06,z-.04),.245,.31,"driftwood")
            m.beam((x,2.51,z),(x*.74,3.48,z-.09),.22,.236,"fir")
        m.beam((-5.01,3.53,z-.05),(4.95,3.53,z-.05),.196,.319,"driftwood")
        for x in (-4.88,4.89):
            m.box((x,3.53,z+.123),(.191,.211,.036),"rust")
            for t in (-.075,.075):
                m.revolve((x+t,3.54,z+.151),[(0,.016),(.017,.018)],"chrome",7,(0,0,1))
        if z not in (3.87,-22.4):
            fixture(m,(5.55,2.69,z+.28),"glass_amber",1.63,8.6,color="#ffbc7e")
    for i in range(10):
        z=10.6-i*5.9
        m.tube((-6.25,.623,z),(-6.25,.623,z-5.9),.171,"rust",14)
        m.tube((-6.25,.623,z+.096),(-6.25,.623,z-.078),.204,"aged_steel",14)
        m.tube((5.83,2.97,z),(5.83,2.97,z-5.9),.065,"wet_iron",12)
        m.rope([(5.78,2.81,z),(5.78,2.72,z-1.76),(5.76,2.69,z-3.91),(5.77,2.81,z-5.9)],.028,"copper",7)
    m.box((-5.83,2.0,3.87),(4.48,4.0,.40),"wet_stone",True)
    m.box((5.83,1.96,3.87),(4.48,3.92,.40),"wet_stone",True)
    m.box((-5.61,1.74,-22.40),(4.0,3.48,.35),"wet_stone",True)
    for z in (3.87,-22.40):
        m.box((-.04,2.71,z),(7.39,.181,.299),"rust")
        for x in (-3.51,3.51):
            m.box((x,1.47,z),(.18,2.94,.29),"aged_steel")
            m.rope([(x,1.4,z+.185),(x,2.84,z+.185),(x+.31,3.015,z+.185)],.033,"wet_iron",7)
        if z<0:
            m.sign("warning",(-4.85,1.90,z+.228),.71,.42)

    walk=region.mesh("Steg aus alten Eichenbohlen")
    for j in range(103):
        z=-2.25-j*.402
        h=.031+.009*math.cos(j*1.65)
        walk.box((4.87,h,z),(2.37+.07*math.cos(j),.073,.382),"driftwood",False,rng.uniform(-.019,.019))
        for side in (-1,1):
            x=4.88+side*.832
            walk.blob((x,h+.039,z),(.012,.005,.011),"rust",segments=6,rings=3)
        if j%4==0:
            for x in (3.93,5.72):
                walk.box((x,-.022,z),(.134,.193,.149),"walnut")
        if j%6==0:
            walk.box((6.014,.612,z),(.096,1.15,.093),"aged_steel")
            walk.box((6.014,1.166,z-1.203),(.070,.079,2.44),"zinc")
            walk.box((6.014,.586,z-1.196),(.059,.055,2.44),"wet_iron")
    walk.collision((4.87,.002,-22.57),(2.37,.062,41.45))
    walk.collision((6.014,.65,-22.61),(.11,1.29,41.25))
    for j in range(22):
        x=rng.uniform(1.1,2.58)
        z=rng.uniform(-42.8,-4.5)
        walk.box((x,.017,z),(.065,.033,.21),"driftwood",False,rng.uniform(-1,1))
    survey=region.mesh("Lotstelle P–2")
    table(survey,5.74,1.13,1.30,.69,.73,"fir")
    survey.sign("hydrophone",(5.86,1.416,.752),.62,.36,0,"aged_steel")
    survey.sheet("dispatch",(5.36,.783,1.39),.34,.251,.01)
    case(survey,5.78,.781,1.00,.56,.30,.241,"sea_green",.10)
    meter(survey,5.90,1.032,1.136,.087,face="glass_amber",phase=.51)
    coil(survey,6.04,.789,1.29,.135,.011,4,"net")
    crate(survey,6.21,.014,.04,.61,.41,.35,"driftwood",True)
    emergency_beacon(survey,5.47,.785,1.162,False,True)
    for x in (-4.63,-2.61):
        survey.box((x,.215,-12.78),(1.21,.39,1.78),"fieldstone")
        survey.revolve((x,.719,-13.29),[(0,.39),(.86,.404),(1.56,.33)],"deep_steel",24,(0,0,1))
        for j in range(12):
            zz=-13.12+j*.108
            survey.revolve((x,.72,zz),[(0,.435),(.039,.435)],"aged_steel",20,(0,0,1))
        survey.rope([(x,.86,-13.38),(x,1.38,-13.54),(x,1.79,-13.42),(x-.25,1.86,-13.24)],.142,"rust",14)
        survey.hoop((x,1.53,-12.01),.222,.036,"ceramic_red")
        for y in (1.06,1.74):
            survey.box((x,y,-12.50),(.077,.065,.79),"brass")
    fixture(survey,(-3.98,2.88,-10.22),"bulb",2.5,8.03,shadow=True)
    survey.sign("dispatch",(-3.95,2.063,-12.26),1.05,.49)
    stacks(survey,-5.85,-10.58,.257,.058,4)
    crate(survey,-6.44,.08,-15.51,.66,.53,.45,"driftwood",True)
    coil(survey,-6.47,.534,-15.48,.263,.020,5)

    for name,z in [("TideGate",3.87),("PressureGate",-22.4)]:
        gate=region.mesh(name,(0,1.13 if name=="TideGate" else 3.91,z))
        gate.box((0,0,0),(7.1,2.25,.247),"deep_steel")
        for i in range(14):
            x=-3.32+i*.508
            gate.box((x,.0,.160),(.113,2.05,.084),"aged_steel")
            gate.box((x,.843,.214),(.152,.081,.041),"rust")
            gate.box((x,-.781,.214),(.152,.081,.041),"rust")
        gate.box((0,-.930,.186),(7.02,.174,.102),"rust")
        gate.sign("warning",(0,.333,.224),.89,.41,0,"aged_steel")
        if name=="TideGate":
            emergency_beacon(survey,3.81,2.17,z,True,True)
    survey.sign("platform_sign",(0,2.236,-43.79),1.55,.65)
    fixture(survey,(0,3.36,-43.31),"volt",1.21,6.75,color="#a5dcce")
    return region


def hatch_wall(m,x,z,length=9.0):
    for dir in (-1,1):
        half=(length-1.80)*.5
        at=z+dir*(length+1.80)*.25
        m.box((x,1.65,at),(.238,3.30,half),"sand_enamel",True)
        m.box((x,1.32,at),(.256,2.04,half),"deep_steel")
        m.box((x,2.359,at),(.295,.095,half),"aged_steel")
        m.box((x,.135,at),(.292,.191,half),"diamond_plate")
        for i in range(5):
            zz=at-half/2+.193+i*(half-.4)/4
            m.box((x,1.59,zz),(.270,3.04,.036),"aged_steel")
        for y in (.292,2.34):
            m.box((x,y,z+dir*.916),(.288,.118,.129),"rust")
        m.box((x,1.117,z+dir*.919),(.315,2.22,.135),"aged_steel")
    m.box((x,2.724,z),(.244,1.152,1.80),"sand_enamel",True)
    m.box((x,2.176,z),(.319,.136,1.97),"aged_steel")
    for side in (-1,1):
        m.box((x+side*.15,2.118,z),(.028,.054,.59),"volt")


def bench_rack(m,x,z,length=.95,h=2.1,depth=.43,key="deep_steel"):
    for corner in (-1,1):
        m.box((x+corner*length*.48,h*.5,z),(.077,h,depth),key)
    m.box((x,.13,z),(length,.21,depth),"wet_iron")
    m.box((x,h*.50,z-depth*.48),(length,h-.17,.069),"aged_steel")
    for j in range(5):
        m.box((x,.16+j*(h-.18)/5,z),(length,.051,depth),"aged_steel")
    m.collision((x,h*.5,z),(length,h,depth))


def server(m,x,z,seed=3):
    bench_rack(m,x,z,1.15,2.37,.67)
    for j in range(10):
        y=.259+j*.177
        m.box((x,y,z+.109),(.997,.133,.548),"deep_steel")
        m.box((x-.071,y,z+.397),(.63,.058,.044),"coal")
        for k in range(8):
            m.box((x-.36+k*.083,y,z+.426),(.036,.017,.013),"aged_steel")
        for jx in range(3):
            m.revolve((x+.196+.084*jx,y,z+.392),[(0,.023),(.015,.023)],"signal" if (j+jx+seed)%7==0 else "volt",8,(0,0,1))
    for dx in (-.398,.40):
        m.tube((x+dx,1.95,z+.366),(x+dx,2.05,z+.365),.021,"chrome",7)


def instrument_table(m,x,z,w=2.2):
    table(m,x,z,w,.74,.836,"aged_steel")
    m.box((x,.889,z),(w+.03,.028,.78),"sand_enamel")
    m.box((x,.694,z+.368),(w*.91,.045,.036),"deep_steel")


def laboratory(m,x,z):
    instrument_table(m,x,z,3.81)
    for j in range(7):
        xx=x-1.65+j*.31
        m.revolve((xx,.901,z),[(0,.066),(.024,.087),(.18,.074),(.287,.037),(.32,.037)],"glass_green",13)
        m.revolve((xx,1.173,z),[(0,.042),(.055,.043)],"brass",13)
        m.box((xx,1.001,z+.072),(.088,.063,.008),"paper")
    instrument_table(m,x+1.10,z+2.41,1.69)
    m.soft((x+1.04,1.16,z+2.411),(.56,.52,.56),"aged_steel",.059)
    meter(m,x+1.045,1.28,z+2.691,.108,face="glass_amber")
    for j in range(7):
        m.box((x+.823+j*.073,1.115,z+2.700),(.041,.022,.018),"volt")
    m.tube((x+1.42,.912,z+2.24),(x+1.42,1.63,z+2.25),.013,"aged_steel",8)


def secured_room(m,x,z):
    instrument_table(m,x+.39,z,2.57)
    for i in range(3):
        crt(m,x-.34+i*.59,.906,z,.72,tag=i*8)
    meter(m,x-.529,1.74,z-.26,.109,face="glass_green")
    desk_lamp(m,x-1.38,.893,z-.189)
    chair(m,x+.12,z+.81,PI+.11,"green_cloth",True)
    for i in range(3):
        stacks(m,x-1.01+i*.197,z+.202,.168,.897,2)
    m.sign("platform_sign",(x+.029,2.14,z-.31),1.14,.50)


def berth(m,x,z):
    for dz in (-.29,2.38):
        for y in (.59,1.58):
            m.box((x,y,z+dz),(1.07,.121,2.15),"aged_steel")
            m.soft((x,y+.115,z+dz),(1.035,.149,2.098),"linen",.057)
            m.soft((x,y+.217,z+dz+.30),(1.049,.063,1.42),"blanket",.033)
            m.blob((x,y+.192,z+dz-.69),(.357,.112,.229),"canvas",segments=12,rings=6,jitter=.058)
        for dx in (-.523,.523):
            for sign in (-1,1):
                m.tube((x+dx,.028,z+dz+sign*1.004),(x+dx,2.17,z+dz+sign*1.004),.038,"aged_steel",8)
        m.collision((x,1.00,z+dz),(1.235,2.0,2.17))
    for i in range(3):
        xx=x+(.74+.57*i)
        m.box((xx,.879,z-2.42),(.53,1.758,.405),"deep_steel",True)
        m.box((xx,.929,z-2.201),(.446,1.586,.028),"sand_enamel")
        for j in range(6):
            m.box((xx,1.26+.061*j,z-2.176),(.246,.021,.019),"wet_iron")
        m.box((xx+.165,.754,z-2.166),(.052,.113,.019),"chrome")


def turbine_room(m,x,z,soft=False):
    for j in range(2):
        xx=x+1.37*j-.54
        m.box((xx,.15,z),(1.12,.30,2.28),"concrete",True)
        m.collision((xx,.659,z),(.79,1.03,1.85))
        m.revolve((xx,.69,z-1.02),[(0,.377),(.124,.413),(.636,.425),(1.72,.436),(1.82,.322)],
                  "aged_steel" if soft else "deep_steel",20,(0,0,1))
        for i in range(10):
            m.revolve((xx,.69,z-.83+i*.145),[(0,.458),(.055,.458)],"wet_iron",22,(0,0,1))
        m.revolve((xx,.69,z+.776),[(0,.244),(.11,.257),(.236,.224)],"rust",16,(0,0,1))
        m.rope([(xx,.984,z-.655),(xx,1.61,z-.654),(xx+.17,1.91,z-.832),(xx+.375,1.94,z-1.49)],
               .143,"rust",13)
        m.light((xx,1.13,z+.94),"#e0b58e",.33,3.73,False)
        meter(m,xx,1.21,z+.726,.108,face="glass_amber")


def archives(m,x,z):
    for idx,dx in enumerate((-1.75,1.75)):
        bench_rack(m,x+dx,z-.86,1.60,2.15,.53)
        bench_rack(m,x+dx,z+1.91,1.60,2.15,.53)
        for row in range(4):
            for col in range(6):
                px=x+dx-.58+col*.216
                for zz in (-.86,1.91):
                    colour=("canvas","aged_steel","garnet","sand_enamel")[(row+col+idx)%4]
                    m.box((px,.29+row*.413,z+zz),(.192,.196,.368),colour)
                    m.box((px,.319+row*.413,z+zz+.186),(.102,.058,.013),"paper")
    m.sign("archive_plate",(x,1.98,z-.53),.92,.39,0,"aged_steel")
    m.sign("rack",(x+.65,1.79,z-.522),.305,.25,.033,"deep_steel")


def platform():
    region=Set("chapter5")
    spine=region.mesh("Technikgang mit Kabeltrassen")
    spine.box((0,-.21,-16),(19.2,.42,58),"diamond_plate",True)
    spine.box((0,3.36,-16),(19.2,.24,58),"deep_steel",True)
    for x in (-9.52,9.52):
        spine.box((x,1.65,-16),(.35,3.3,58),"deep_steel",True)
        spine.tube((x*.96,2.74,12),(x*.96,2.74,-44),.178,"rust",14)
    for z in (12.4,-44.7):
        spine.box((0,1.65,z),(19.2,3.3,.35),"deep_steel",True)
        spine.sign("platform_sign",(0,2.68,z+.21 if z<0 else z-.21),2.1,.54,0 if z<0 else PI)
    for i in range(27):
        z=11.4-i*2.09
        spine.box((0,3.136,z),(5.33,.14,.167),"aged_steel")
        for x in (-2.457,2.457):
            spine.box((x,2.223,z),(.168,1.80,.066),"aged_steel")
        for x in (-1.53,1.53):
            spine.box((x,.013,z),(.049,.021,1.68),"hazard")
        for k in range(12):
            spine.box((-.704+k*.127,.005,z),(.053,.009,.49),"coal")
        if i%3==0:
            x=-1.05 if i%2 else 1.05
            fixture(spine,(x,2.97,z),"volt",1.8,6.5,color="#b9ddd2")
    for side in (-1,1):
        x=side*2.278
        spine.tube((x,2.813,12.37),(x,2.813,-43.82),.089,"rust",12)
        spine.tube((x,2.674,12.37),(x,2.674,-43.86),.045,"copper",10)
        for i in range(16):
            z=11.55-i*3.53
            spine.box((x,.011,z),(.74,.020,2.62),"deep_steel")
            spine.rope([(x,2.91,z),(x-side*.11,2.931,z-.92),(x-side*.15,2.96,z-2.62),(x,2.91,z-3.53)],.027,"conduit",7)
    for j in range(17):
        z=11.3-j*3.31
        for s in (-1,1):
            x=s*2.398
            spine.soft((x,2.48,z),(.25,.386,.221),"aged_steel",.037)
            spine.tube((x-s*.13,2.65,z),(x-s*.13,2.29,z),.026,"zinc",9)
            for u in (-.079,.072):
                spine.rope([(x,2.887,z),(x-s*.165,2.712,z+u),(x-s*.126,2.51,z+u)],.019,"copper" if j%3 else "rust",8)
    for x,z in [(1.96,7.77),(-2.04,-2.32),(1.99,-15.31),(-2.06,-26.83),(1.95,-38.65)]:
        spine.soft((x,.358,z),(.436,.717,.569),"deep_steel",.065,solid=True)
        spine.soft((x,.726,z),(.45,.06,.57),"sand_enamel",.020)
        for i in range(6):
            spine.box((x,.53-.041*i,z+.292),(.241,.021,.019),"aged_steel")
        spine.revolve((x+.12,.68,z+.301),[(0,.019),(.012,.018)],"signal",9,(0,0,1))
    for i in range(5):
        z=5.7-i*9.0
        for side in (-1,1):
            x=side*6.15
            room=region.mesh(f"Bay_{i}_{side+1}")
            hatch_wall(room,side*2.70,z)
            room.box((x,1.55,z-4.5),(6.83,3.1,.23),"sand_enamel",True)
            room.box((x,1.29,z-4.359),(6.66,2.19,.067),"deep_steel")
            room.box((x,2.42,z-4.310),(6.73,.078,.104),"aged_steel")
            for r in range(8):
                room.box((x+(r-3.5)*.824,1.55,z-4.312),(.035,3.036,.050),"aged_steel")
            code=i*2+(1 if side<0 else 2)
            fixture(room,(x,2.72,z-1.12),"glass_amber" if code%3==0 else "volt",1.49,6.1,
                    color="#f5c995" if code%3==0 else "#b3d1c8")
            if code in (1,4,9):
                dx=(.82 if code==1 else -.34)*side
                secured_room(room,x+dx,z-2.71 if code!=9 else z+2.54)
            elif code==2:
                berth(room,x-.42,z-.71)
            elif code==3:
                laboratory(room,x,z-2.39)
            elif code in (5,8):
                turbine_room(room,x,z-1.31,code==8)
            elif code==6:
                for q in range(3):
                    server(room,x+(q-1)*1.48,z-2.93,q)
                for q in range(2):
                    server(room,x-.73+q*1.78,z+3.18,q+2)
                room.sign("rack",(x-.506,1.93,z-.12),.647,.417,0)
            elif code==7:
                archives(room,x,z)
            else:
                for q in range(3):
                    bench_rack(room,x+(q-1)*1.47,z-2.72,1.20)
                    for k in range(4):
                        case(room,x+(q-1)*1.47,.19+k*.381,z-2.72,.602,.289,.178,
                             ["deep_steel","canvas","garnet"][q],.07*k)
    rubble=region.mesh("CollapsedBulkhead",(0,1.25,-8.02))
    rubble.box((0,-.574,0),(5.39,1.53,.76),"concrete")
    rng=random.Random(171198)
    for j in range(28):
        x=rng.uniform(-2.5,2.5)
        y=rng.uniform(-.65,.81)
        z=rng.uniform(-.39,.50)
        rubble.blob((x,y,z),(rng.uniform(.31,.80),rng.uniform(.28,.68),rng.uniform(.37,.82)),
                    "concrete" if j%5 else "cliff",rng,8,4,.24)
        if j%4==0:
            rubble.beam((x,y+.16,z),(x+.23,y+.58,z-.19),.066,.075,"rust")
    return region


def resonance():
    region=Set("chapter7")
    core=region.mesh("Basalt, Kabel und Laufstege")
    rng=random.Random(31606)
    core.box((0,-.19,0),(21,.38,24),"wet_stone",True)
    for side in (-1,1):
        core.box((side*10.46,4,0),(.41,8,24),"wet_stone",True)
        core.box((0,4,side*11.77),(21,8,.44),"cliff",True)
        for i in range(11):
            z=-11.46+i*2.21
            x=side*rng.uniform(9.8,10.13)
            h=rng.uniform(3.9,6.87)
            core.blob((x,h*.47,z),(rng.uniform(.75,1.69),h*.59,rng.uniform(.76,1.89)),
                      "wet_stone",rng,10,5,.24)
            core.tube((x-side*.47,.116,z),(x-side*.49,h*.77,z+.134),.17,"wet_iron",9,.45)
            core.beam((x-side*.57,h*.76,z+.134),(side*5.69,h*.86,z-.453),.275,.38,"aged_steel")
            if i%3==1:
                fixture(core,(x-side*1.29,2.46,z),"glass_amber",1.4,6.05,color="#ebaf78")
    for r,w in ((2.39,.11),(3.15,.061),(5.03,.067),(7.83,.040)):
        core.hoop((0,.031,-1.83),r,w,"brass" if r>3 else "volt","y",64)
    for i in range(18):
        a,b=TAU*i/18,TAU*(i+1)/18
        x,z=2.68*math.cos(a),2.68*math.sin(a)-1.83
        next_x,next_z=2.68*math.cos(b),2.68*math.sin(b)-1.83
        core.revolve((x,.012,z),[(0,.113),(.11,.132),(.189,.078),(.81,.064),(.85,.086)],"deep_steel",14)
        for y in (.327,.838):
            core.tube((x,y,z),(next_x,y,next_z),.042 if y<.4 else .061,"aged_steel",12)
        segment=math.hypot(next_x-x,next_z-z)+.064
        core.collision(((x+next_x)/2,.422,(z+next_z)/2),(segment,.852,.103),
                       -math.atan2(next_z-z,next_x-x))
    for i in range(24):
        a=i*TAU/24
        u=math.sin(a); v=math.cos(a)
        core.beam((7.72*u,.043,7.72*v-1.83),(7.32*u,.043,7.32*v-1.83),.048,.043,"brass")
        if i%4==0:
            core.rope([(u*3.13,.060,v*3.13-1.83),(u*4.5,.068,v*4.5-1.78),(u*5.38,.057,v*5.45-1.91),
                        (u*7.52,.054,v*7.56-1.81)],.056,"aged_steel",11)
            core.box((u*5.04,.08,v*5.04-1.83),(.187,.153,.195),"deep_steel")
    core.revolve((0,.009,-1.83),[(0,2.19),(.052,2.19),(.091,1.87)],"aged_steel",56)
    core.revolve((0,.092,-1.83),[(0,1.85),(.025,1.85),(.062,1.64)],"deep_steel",56)
    for i in range(18):
        a=i*TAU/18
        x,z=math.cos(a),math.sin(a)
        core.beam((1.42*x,.158,-1.83+1.42*z),(1.81*x,.158,-1.83+1.81*z),.077,.046,"volt" if i%3==0 else "chrome")
    for s in (-1,1):
        x=s*8.004
        core.rope([(x,.12,3.81),(x,.08,1.46),(x-s*.47,.08,-.86),(x-s*.53,.077,-4.85),(x,.096,-8.93)],
                  .073,"rust",10)
        for j in range(7):
            z=5.69-j*2.31
            core.box((x+s*.23,.091,z),(.811,.095,.69),"diamond_plate",False,s*.14)
    core.sign("zero",(0,5.07,-11.50),2.1,.67)
    fixture(core,(0,4.09,-8.6),"volt",2.25,9.8,color="#abded2")
    fixture(core,(-4.34,3.70,1.40),"glass_amber",1.30,6.38,color="#e8b082")
    fixture(core,(4.34,3.70,1.40),"glass_amber",1.30,6.38,color="#e8b082")
    for name,r,width,shade in [("FieldOuter",2.06,.109,"volt"),("FieldInner",1.62,.072,"amber")]:
        ring=region.mesh(name,(0,2.65,-1.82))
        ring.hoop((0,0,0),r,width*.58,shade,segments=92)
        for side in (-1,1):
            ring.hoop((0,0,side*.103),r+.029,width*.63,"aged_steel",segments=72)
        for i in range(24):
            a=i*TAU/24
            x=math.sin(a)*r
            y=math.cos(a)*r
            ring.box((x,y,0),(.133,.220,.309),"brass" if i%3==0 else "deep_steel",False)
            ring.tube((x,y,-.178),(x,y,.179),.012,shade,8)
    return region


def control():
    region=Set("instruments")
    terminal=region.mesh("ServiceConsole")
    service_panel(terminal,0,0,0,1.04,.66,1.125)
    terminal.collision((0,.552,0),(1.04,1.08,.68))
    return region


def build():
    return [*arrival(),original_village(),blackcliff(),*ship(),cave(),platform(),resonance(),control()]
