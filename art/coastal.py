"""Meter-scale replacements for the silhouettes on the original coast."""

import math
import random

from mesh import PI, TAU, Set, rotate_y
from shore import barrel, book, clock_dial, coil, crate, cup, curtain, desk_lamp, grass, hooks, lamp, net_panel, plant, radiator, rug, stacks


def connect(m, rows, color, smooth=False):
    size=len(rows[0])
    verts=[v for row in rows for v in row]
    faces=[(k*size+j,(k+1)*size+j,(k+1)*size+(j+1)%size,k*size+(j+1)%size)
           for k in range(len(rows)-1) for j in range(size)]
    m.add(verts,faces,color,smooth=smooth)


def stone(m, seed):
    rng=random.Random(seed)
    count=22
    notches=[rng.uniform(.79,1.14) for _ in range(count)]
    rows=[]
    for y,r,shift in [(-.88,.62,-.025),(-.51,1.01,.07),(-.09,1.04,0),(.20,.94,.08),
                      (.45,.89,.12),(.71,.77,.14),(1.00,.54,.092),(1.15,.274,.09),(1.21,.030,.02)]:
        row=[]
        for i in range(count):
            a=TAU*i/count
            radius=r*notches[i]*rng.uniform(.89,1.10)
            x=1.47*radius*math.cos(a)+shift
            z=radius*math.sin(a)+shift*.39
            row.append((x,y+.16*x+.074*z+rng.uniform(-.070,.080)*r,z))
        rows.append(row)
    for k in range(len(rows)-1):
        for j in range(count):
            i=(j+1)%count
            pts=[rows[k][j],rows[k+1][j],rows[k+1][i],rows[k][i]]
            key='wet_stone' if k<2 else ('fieldstone' if k in (4,6) and (j+seed)%6<4 else 'cliff')
            m.add(pts,[(0,1,3),(1,2,3)],key,smooth=False)
    m.add(rows[-1],[tuple(reversed(range(count)))],'cliff')


def pine(m, seed, height, width, detailed=True):
    rng=random.Random(seed)
    bark=[]
    drift=rng.uniform(-.33,.33)
    leaves=('leaf_dark','leaf','moss_green','leaf_light')
    for i in range(13):
        t=i/12
        rad=.226*(1-t)**.88+.014
        bark.append([(drift*t+rad*math.cos(a*TAU/14),t*height,.158*t+rad*math.sin(a*TAU/14)) for a in range(14)])
    connect(m,bark,'bark',True)
    for i in range(9):
        angle=i*TAU*.38197
        length=rng.uniform(.32,.71)
        x,z=math.cos(angle)*length,math.sin(angle)*length
        m.revolve((0,.028,0),[(0,.085),(length,.014)],'bark',7,(x,-.10,z))
    for ring in range(10):
        t=(ring+.1)/10.25
        y=height*(.17+.79*t)
        num=max(3,round(7-3.4*t))
        for j in range(num):
            a=ring*2.39+j*TAU/num+rng.uniform(-.19,.19)
            ux,uz=math.cos(a),math.sin(a)
            reach=width*(1-t)**.68*rng.uniform(.69,1.17)
            x0,z0=drift*y/height,.158*y/height
            to=(x0+ux*reach,y-.24+reach*.09,z0+uz*reach)
            heel=(x0,y,z0)
            mid=(x0+ux*reach*.48,y-reach*.19,z0+uz*reach*.48)
            m.rope([heel,mid,to],max(.014,.048*(1-t)),'bark',6)
            sprays=4 if detailed else 3
            twigs=5 if detailed else 3
            for spray in range(sprays):
                u=(spray+1)/sprays
                for side in (-1,1):
                    s=reach*(.39-.22*u)*rng.uniform(.7,1.16)*side
                    yy=y+(-.40*math.sin(u*PI)+.04*u)*reach
                    at=(x0+ux*reach*u,yy,z0+uz*reach*u)
                    tip=(at[0]-uz*s+ux*reach*.18,yy+.071+reach*.09,at[2]+ux*s+uz*reach*.18)
                    m.tube(at,tip,.016,'bark',5,.19)
                    for twig in range(twigs):
                        k=(twig+1)/twigs
                        xx,dy,zz=[a+(b-a)*k for a,b in zip(at,tip)]
                        leaf=reach*rng.uniform(.146,.232)*(1-.36*k)
                        for n in (range(3) if detailed else (1,)):
                            turn=a+(n-1)*1.16+side*.49
                            bx,bz=math.cos(turn)*leaf,math.sin(turn)*leaf
                            up=(xx+bx*.54,dy+.071,zz+bz*.54)
                            end=(xx+bx,dy+.013+leaf*.32,zz+bz)
                            base=(xx,dy-.016,zz)
                            left=(up[0]+bz*.25,up[1]-.018,up[2]-bx*.25)
                            right=(up[0]-bz*.26,up[1]-.022,up[2]+bx*.26)
                            color=leaves[(ring+twig+spray+n//2)%len(leaves)]
                            m.add([base,left,end,right,up],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),
                                (0,4,1),(1,4,2),(2,4,3),(3,4,0)],color)


def van(m):
    # A rounded, pressed steel body with separately modelled roof, windows, seals and trim.
    bays=[(-2.15,.78,.69,1.09),(-2.02,.91,.53,1.20),(-1.58,.94,.47,1.25),
          (-1.04,.94,.43,1.61),(-.69,.96,.42,1.72),(.49,.97,.42,1.73),
          (1.56,.97,.43,1.72),(2.01,.92,.50,1.62),(2.14,.85,.55,1.50)]
    rows=[]
    for z,half,bottom,top in bays:
        upper=top-.155
        outline=[(-half*.87,bottom),(-half*.97,bottom+.075),(-half,bottom+.31),
                 (-half*.99,min(.999,top-.12)),(-half*.82,upper),(-half*.69,top-.027),
                 (-half*.45,top),(half*.45,top),(half*.69,top-.027),
                 (half*.82,upper),(half*.99,min(.999,top-.12)),(half,bottom+.31),
                 (half*.97,bottom+.075),(half*.87,bottom)]
        rows.append([(x,y,z) for x,y in outline])
    for k in range(len(rows)-1):
        for j in range(len(rows[0])):
            n=(j+1)%len(rows[0])
            color='vehicle_cream' if 3<=j<=9 else 'vehicle_paint'
            m.add([rows[k][j],rows[k][n],rows[k+1][n],rows[k+1][j]],[(3,2,1,0)],color,smooth=True)
    m.add(rows[0],[tuple(range(len(rows[0])))],'vehicle_paint')
    m.add(rows[-1],[tuple(reversed(range(len(rows[-1]))))],'vehicle_paint')
    for side in (-1,1):
        x=.96*side
        for z in (-1.30,1.32):
            m.revolve((x-.071*side,.35,z),[(0,.260),(.031,.312),(.081,.338),(.238,.338),(.286,.279)],
                      'tire',28,(side,0,0))
            m.revolve((x+.207*side,.35,z),[(0,.214),(.019,.215),(.045,.179),(.072,.095),(.074,.054)],
                      'zinc',25,(side,0,0))
            for i in range(6):
                a=TAU*i/6
                m.tube((x+.251*side,.35+math.sin(a)*.136,z+math.cos(a)*.136),
                       (x+.283*side,.35+math.sin(a)*.136,z+math.cos(a)*.136),.026,'deep_steel',8)
            arch=[(x+.023*side,.36+math.cos(i*PI/16)*.365,z+math.sin(i*PI/16)*.365) for i in range(-8,9)]
            m.rope(arch,.028,'vehicle_paint',7)
        for lo,hi in [(-1.09,-.20),(-.15,.97),(1.04,1.79)]:
            points=[(.956*side,1.018,lo),(.957*side,1.020,hi),(.808*side,1.53,hi-.045),(.814*side,1.53,lo+.105)]
            m.quad(list(reversed(points)) if side>0 else points,'deep_glass')
            m.rope(points+[points[0]],.034,'tar',7)
        for z in (-.16,.995,1.83):
            m.rope([(x,1.012,z),(1.002*side,.879,z),(1.008*side,.697,z),(.965*side,.48,z)],.008,'coal',6)
        m.tube((1.007*side,.942,-.366),(1.012*side,.942,-.213),.029,'chrome',10)
        m.tube((1.003*side,.942,1.10),(1.006*side,.942,1.28),.026,'chrome',10)
        m.rope([(.942*side,1.16,-.94),(1.121*side,1.20,-.91),(1.142*side,1.32,-.89)],.029,'tar',8)
        m.soft((1.16*side,1.318,-.858),(.16,.17,.092),'chrome',.03)
        m.tube((1.012*side,.84,-1.72),(1.013*side,.84,1.82),.020,'zinc',8)
    glass=[(-.78,1.116,-1.635),(.78,1.116,-1.635),(.672,1.565,-1.115),(-.672,1.565,-1.115)]
    m.quad(list(reversed(glass)),'deep_glass')
    m.rope(glass+[glass[0]],.036,'tar',8)
    for x in (-.34,.36):
        m.rope([(x-.22,1.134,-1.614),(x+.19,1.247,-1.475)],.013,'tar',8)
    m.soft((0,.53,-2.149),(1.82,.15,.22),'zinc',.067)
    m.soft((0,.59,2.143),(1.83,.15,.20),'zinc',.063)
    m.soft((0,.855,-2.153),(.81,.24,.042),'tar',.025)
    for y in (.792,.826,.860,.895,.929):
        m.tube((-.391,y,-2.192),(.391,y,-2.192),.013,'zinc',8)
    for x in (-.684,.684):
        m.revolve((x,.899,-2.107),[(0,.115),(.038,.153),(.068,.143)],'chrome',22,(0,0,-1))
        m.revolve((x,.899,-2.181),[(0,.112),(.025,.123),(.046,.090)],'porcelain',22,(0,0,-1))
        m.soft((x,.804,2.128),(.179,.262,.071),'ceramic_red',.033)
    for side in (-1,1):
        m.soft((side*.426,1.243,2.099),(.68,.438,.068),'deep_glass',.043)
        m.tube((side*.87,1.70,-.51),(side*.87,1.71,1.60),.028,'zinc',10)
    m.soft((0,.687,2.188),(.403,.129,.027),'ivory',.013)
    m.tube((.72,.485,2.00),(.74,.457,2.28),.032,'wet_iron',10)


def hull(m, length, width, deck, deck_material='parquet'):
    stations=[(-.50,.60,.09),(-.46,.79,-.02),(-.36,.94,-.10),(-.19,1,-.12),(.08,1,-.10),
              (.27,.875,-.04),(.39,.60,.075),(.46,.30,.18),(.5,.03,.23)]
    keel=[]
    side=[]
    for s in (-1,1):
        planks=[]
        for row in range(7):
            t=row/6
            points=[]
            for j,(station,beam,rise) in enumerate(stations):
                rim=beam*width*.5
                x=s*rim*(.016+.984*math.sin(t*PI*.47)**.54)
                y=deck-.55*(1-t)+rise*(.48+t*.52)
                points.append((x,y,station*length))
            planks.append(points)
        for i in range(len(planks)-1):
            for j in range(len(stations)-1):
                p=[planks[i][j],planks[i+1][j],planks[i+1][j+1],planks[i][j+1]]
                m.add(p,[(3,2,1,0) if s<0 else (0,1,2,3)],
                      ('ward_red' if i<2 else 'vehicle_paint' if i<5 else 'cream_siding'),smooth=True)
        m.rope(planks[-1],.052,'oak',10)
        m.rope(planks[-2],.027,'tar',9)
        side.append(planks[-1])
        keel.append(planks[0])
    for i in range(len(stations)-1):
        boundary=[side[0][i],side[1][i],side[1][i+1],side[0][i+1]]
        lower=[keel[1][i],keel[0][i],keel[0][i+1],keel[1][i+1]]
        m.quad(list(reversed(boundary)),deck_material)
        m.quad(list(reversed(lower)),'ward_red')
    m.add([side[0][0],side[1][0],keel[1][0],keel[0][0]],[(0,1,2,3)],'ward_red')


def launch(m):
    hull(m,5.67,2.30,.69)
    m.soft((-.08,.887,.55),(1.37,.51,.60),'oak',.07)
    m.box((-.08,1.126,.493),(1.38,.092,.65),'vehicle_paint')
    m.soft((-.418,1.238,.524),(.36,.143,.337),'deep_steel',.047)
    m.box((-.416,1.291,.420),(.184,.034,.117),'volt')
    m.tube((.32,1.158,.18),(.32,1.206,.111),.065,'aged_steel',13)
    m.hoop((.32,1.224,.106),.184,.024,'walnut',segments=20)
    for i in range(5):
        a=TAU*i/5
        m.tube((.32,1.225,.112),(.32+math.sin(a)*.171,1.225+math.cos(a)*.171,.111),.013,'brass',8)
    for s in (-1,1):
        for z in (.90,1.647,2.103):
            w=.99 if z<1.65 else .538
            m.tube((s*w,.73,z),(s*w,1.173,z),.023,'zinc',10)
        m.rope([(s*.994,1.172,.89),(s*.994,1.17,1.64),(s*.54,1.167,2.10),(s*.15,1.166,2.57)],.032,'zinc',10)
    m.soft((0,.828,-2.01),(1.43,.248,.47),'vehicle_cream',.05)


def trawler(m):
    hull(m,9.23,3.17,.72)
    m.soft((0,1.03,-1.16),(2.25,.67,2.44),'vehicle_cream',.068)
    m.soft((0,1.67,-1.32),(2.22,1.31,2.16),'vehicle_cream',.057)
    m.soft((0,2.325,-1.305),(2.49,.146,2.42),'vehicle_paint',.069)
    for s in (-1,1):
        x=s*1.121
        for z in (-1.82,-.96):
            m.soft((x,1.84,z),(.06,.49,.616),'tar',.027)
            m.soft((x+s*.055,1.841,z),(.056,.414,.568),'deep_glass',.021)
        m.tube((x,.861,-4.07),(x,1.22,-4.07),.028,'zinc',10)
        for z in (-2.78,-.39,.72,1.58,2.66,3.57):
            width=1.53 if abs(z)<2.8 else 1.15
            m.tube((s*width,.72,z),(s*width,1.34,z),.022,'zinc',9)
        m.rope([(s*1.12,1.22,-4.07),(s*1.43,1.33,-2.78),(s*1.55,1.33,.72),
                (s*1.51,1.33,2.66),(s*1.15,1.33,3.57),(s*.36,1.33,4.30)],.032,'zinc',10)
    for x in (-.71,0,.71):
        m.soft((x,1.864,-.230),(.60,.49,.095),'tar',.034)
        m.soft((x,1.865,-.167),(.535,.412,.043),'deep_glass',.025)
        m.tube((x-.13,1.67,-.139),(x+.119,1.86,-.14),.011,'zinc',8)
    m.soft((.41,1.42,-2.425),(.72,1.36,.12),'vehicle_paint',.035)
    m.box((.41,1.70,-2.503),(.49,.44,.025),'deep_glass')
    m.revolve((-.68,2.38,-.91),[(0,.12),(.65,.101),(.698,.139)],'rust',14)
    m.revolve((0,2.38,-1.78),[(0,.084),(1.17,.031)],'zinc',13)
    m.tube((-.637,3.103,-1.78),(.637,3.103,-1.78),.036,'zinc',12)
    m.sign('landfall',(0,2.09,-.149),.57,.145,0,'vehicle_paint')
    crate(m,-.66,.713,1.57,.63,.49,.45,'fir')
    net_panel(m,.93,1.23,2.43,.76,.55)
    coil(m,-.63,.776,2.77,.33,.026,6)


def cargo(m):
    w,h,d=2.49,2.13,4.57
    m.soft((0,h*.49,0),(w-.11,h,d-.10),'cargo_panel',.041)
    for x in (-w/2,w/2):
        for i in range(19):
            z=(-9+i)*.235
            m.soft((x,h*.49,z),(.097,1.939,.149),'cargo_panel',.029)
        for z in (-2.243,2.243):
            m.soft((x,h*.49,z),(.12,h,.142),'aged_steel',.025)
        for y in (.069,2.074):
            m.box((x,y,0),(.131,.143,4.53),'deep_steel')
    for z in (-2.273,2.273):
        for s in (-1,1):
            m.soft((s*.598,1.084,z),(1.13,1.856,.13),'cargo_panel',.045)
            for n in range(5):
                m.soft((s*(.203+.193*n),1.084,z+.058*math.copysign(1,z)),(.113,1.651,.07),'cargo_panel',.019)
            latch_z=z+.095*math.copysign(1,z)
            m.tube((s*.404,.17,latch_z),(s*.404,1.985,latch_z),.022,'zinc',10)
            m.tube((s*.404,.899,latch_z),(s*.81,.899,latch_z),.023,'zinc',10)
        m.sign('rigel_plan',(0,1.62,z+.152*math.copysign(1,z)),.479,.213,0 if z>0 else PI,'deep_steel')


def reel(m):
    m.revolve((0,.02,0),[(0,.389),(.088,.396),(.129,.157),(.691,.157),(.721,.39),(.802,.389)],'oak',28)
    for y in (.11,.72):
        m.hoop((0,y,0),.394,.019,'aged_steel','y',28)
    for i in range(15):
        a=i*TAU/15
        m.tube((.37*math.cos(a),.752,.37*math.sin(a)),(.155*math.cos(a),.752,.155*math.sin(a)),.009,'walnut',6)
    points=[(.253*math.cos(i*TAU/24),.14+i*.536/366,.253*math.sin(i*TAU/24)) for i in range(367)]
    m.rope(points,.029,'rope',7)
    m.revolve((0,.805,0),[(0,.096),(.022,.103),(.031,.060)],'wet_iron',16)


def pallet(m):
    for i in range(7):
        x=(i-3)*.158
        m.soft((x,.151,0),(.141,.061,1.03),'driftwood',.013)
        for z in (-.43,0,.43):
            for dx in (-.042,.042):
                m.blob((x+dx,.184,z),(.010,.005,.010),'wet_iron',segments=7,rings=4)
    for x in (-.45,0,.45):
        for z in (-.439,0,.439):
            m.box((x,.069,z),(.146,.14,.139),'walnut')
        m.box((x,.021,0),(.138,.041,1.02),'driftwood')


def fittings(region):
    van(region.mesh('minivan'))
    trawler(region.mesh('trawler'))
    launch(region.mesh('rv_launch'))
    cargo(region.mesh('container'))
    pallet(region.mesh('pallet'))
    reel(region.mesh('rope_reel'))
    for name,seed in [('cliff_0',8),('cliff_1',9),('cliff_2',10)]:
        stone(region.mesh(name),seed)
    for name,seed,height,width in [('fir_0',7434,8.67,2.35),('fir_1',8109,9.99,2.72)]:
        pine(region.mesh(name),seed,height,width)
        pine(region.mesh(name+'_distance'),seed,height,width,False)
    for name,w,d,h,material in [('crate',.84,.76,.70,'fir'),('fish_boxes',.97,.69,.58,'sea_green')]:
        m=region.mesh(name)
        crate(m,0,0,0,w,d,h,material)
        m.sheet('ledger',(0,.121,.0),.241,.215,.14)
        if name=='fish_boxes': crate(m,.24,.014,-.28,.65,.54,.43,'oak')
    for name in ('barrel','bc_oil_drum'):
        m=region.mesh(name)
        barrel(m,0,.009,0,.345,.946,'rust' if name=='bc_oil_drum' else 'driftwood',False)
        m.revolve((0,.953,0),[(0,.272),(.016,.294),(.038,.274)],'aged_steel',24)
        m.revolve((.085,1.00,-.102),[(0,.061),(.019,.061),(.036,.047)],'chrome',12)
    m=region.mesh('bollard')
    m.soft((0,.047,0),(.50,.079,.356),'deep_steel',.032)
    m.revolve((0,.085,0),[(0,.092),(.252,.087),(.282,.13),(.368,.152),(.414,.108)],'rust',20)
    for x in (-.181,.181):
        for z in (-.108,.108):
            m.revolve((x,.081,z),[(0,.042),(.021,.042),(.028,.035)],'wet_iron',6)


def streets(region):
    m=region.mesh('Straßenränder, Fallrohre und Hafenbögen')
    rng=random.Random(4527)
    for s in (-1,1):
        for i in range(125):
            z=24-i*.49
            edge=s*(3.57+.077*math.sin(z*.2))
            m.soft((edge,.032,z),(.186,.068,.467),'fieldstone',.019,yaw=.023*math.cos(z))
            if i%8==2 and z not in (-13,-14,-15):
                for _ in range(3):
                    grass(m,s*rng.uniform(3.92,4.54),.004,z+rng.uniform(-.38,.36),rng,rng.uniform(.46,1.01))
    for x,y,z,side in [(-5.25,2.76,3.91,1),(6.28,2.92,-8.12,-1),(6.24,2.92,1.16,-1),
                     (8.19,3.80,-16.45,-1),(8.19,3.80,-28.75,-1),(-.81,2.66,-33.5,1),
                     (-7.31,2.64,-16.17,1),(-7.15,2.62,-7.38,1),(6.84,2.72,14.55,-1)]:
        m.rope([(x,y,z),(x+.11*side,y-.19,z),(x+.12*side,.4,z),
                (x+.16*side,.19,z-.10),(x+.27*side,.135,z-.16)],.046,'zinc',10)
        for h in (.52,1.49,y-.36):
            m.hoop((x+.115*side,h,z),.056,.011,'wet_iron','y',14)
    for i in range(24):
        z=-22.96+i*.39
        if -15.11<z<-13.87:
            continue
        m.soft((18.68,-.109,z),(.301,.204,.368),'wet_stone',.048,yaw=.08*math.sin(i*1.23))
        if i%4==0:
            m.tube((18.75,-.135,z),(18.75,-.761,z),.059,'zinc',10)
    for x,z in [(15.12,-12.80),(4.60,-18.79),(-6.01,10.18),(-6.98,-13.32),(11.26,-9.05)]:
        plant(m,x,z,size=rng.uniform(.78,1.22),rng=rng,flower=False)
    for x,z in [(17.69,-18.1),(17.61,-22.42)]:
        m.tube((x,.84,z),(x,2.88,z),.097,'aged_steel',12)
        m.revolve((x,2.80,z),[(0,.128),(.11,.166),(.18,.114)],'zinc',16)
        m.tube((x,.72,z),(x+.438,.72,z),.049,'rust',9)
        m.collision((x,.48,z),(.214,1.03,.214))
    m.sign('fish_sign',(8.176,2.727,-22.34),1.63,.59,-PI/2,'deep_steel')
    m.sign('post_hours',(6.208,1.47,-5.15),.283,.389,-PI/2,'walnut')


def panels(m, sections, z, paint, facing=1):
    for left,right in sections:
        centre=(left+right)*.5
        width=right-left
        m.box((centre,.412,z),(width,.824,.028),paint)
        m.box((centre,.821,z+facing*.021),(width,.058,.035),'oak')
        m.box((centre,.055,z+facing*.023),(width,.107,.081),'walnut')
        count=math.ceil(width/.164)
        for i in range(count):
            x=left+(i+.5)*width/count
            m.box((x,.439,z+facing*.021),(.013,.713,.016),'fir')


def sash_lining(m,x,z,sill,head,width,yaw=0):
    def at(u,y,v):
        dx,dy,dz=rotate_y((u,y,v),yaw)
        return x+dx,dy,z+dz
    curtain(m,at,0,width,sill,head)
    m.soft(at(0,sill-.027,-.185),(width+.19,.074,.246),'oak',.019,yaw)


def old_rooms(region):
    house=region.mesh('Fischerhaus · Eichentäfelung und Stube',(-9,.022,7.1),PI/2)
    partition=[(-4.26,-1.035),(.056,2.031),(3.025,4.26)]
    panels(house,partition,.395,'sea_green')
    panels(house,partition,.176,'olive_siding',-1)
    panels(house,[(-4.21,-1.80),(-.587,4.13)],3.52,'sea_green',-1)
    panels(house,[(-4.17,4.17)],-3.522,'olive_siding')
    for x in [-3.66,-2.43,-.57,.88,2.26,3.61]:
        house.soft((x,2.71,1.90),(.146,.183,3.36),'fir',.020)
        house.soft((x,2.71,-1.68),(.144,.176,3.63),'fir',.020)
    sash_lining(house,1.75,3.55,.92,2.08,1.64)
    sash_lining(house,2.27,-3.55,.92,2.05,1.41,PI)
    sash_lining(house,-2.2,-3.55,.93,2.03,1.26,PI)
    rug(house,(-.23,.012,2.12),1.08,2.03)
    rug(house,(.44,.012,-2.20),.99,1.76)
    house.sign('town_print',(1.28,1.73,.414),.65,.435)
    house.sign('old_headland',(-2.32,1.81,.417),.63,.405)
    house.sign('family_photo',(-3.30,1.55,.414),.51,.344)
    house.sign('radio_book',(-1.12,1.61,-3.518),.42,.38,frame='oak')
    clock_dial(house,1.31,2.18,.437,.141,time=4.12)
    hooks(house,-2.14,3.411,'blanket')
    radiator(house,-.761,-3.355,0)
    lamp(house,-1.71,2.52,1.78,'#ffd3a2',1.24)
    lamp(house,.53,2.49,-2.02,'#ebbc91',1.16)
    cup(house,-2.23,.852,-3.10,'ceramic_blue')
    book(house,-2.79,.846,-3.106,.24,.047,.17,'blue_siding',.22)
    desk_lamp(house,-3.065,.847,-3.161)

    market=region.mesh('Proviantladen · Regale und Ladentheke',(10.6,.016,-2.7),-PI/2)
    panels(market,[(-5.34,-1.177),(.174,5.33)],4.112,'ivory',-1)
    for x in (-4.62,-3.05,-1.13,.64,2.61,4.44):
        market.soft((x,2.94,.92),(.18,.16,6.14),'fir',.022)
    for x in (-3.52,2.98):
        sash_lining(market,x,4.137,.75,2.46,2.13)
        lamp(market,x,2.73,1.70,'#e6bc8e',1.10)
    for x in (-3.73,-1.42,.95,3.82):
        for k in range(6):
            dx=-.65+.248*k
            if k%3==0:
                market.revolve((x+dx,1.50,.64),[(0,.067),(.037,.081),(.162,.077),(.184,.071)],'garnet',13)
                market.revolve((x+dx,1.677,.64),[(0,.072),(.021,.071)],'zinc',13)
            else:
                market.soft((x+dx,1.586,.63),(.177,.184,.233),'canvas' if k%2 else 'sea_green',.020)
                market.box((x+dx,1.609,.752),(.122,.072,.011),'paper')
    market.sign('post_hours',(3.38,1.45,3.608),.47,.365,PI)
    market.sign('closed',(-1.92,1.712,-1.855),.48,.284)
    cup(market,4.19,.909,2.62,'ceramic_blue')
    stacks(market,4.47,2.73,.25,.902,3)

    wharf=region.mesh('Netzhalle · Balken, Rolle und Packstation',(13.52,.022,-22.7),-PI/2)
    for i,x in enumerate((-5.36,-2.61,.54,3.10,5.65)):
        wharf.soft((x,3.79,.34),(.22,.24,9.84),'driftwood',.025)
        for z in (-4.49,4.53):
            wharf.beam((x,3.43,z),(x,3.81,z*.74),.16,.19,'walnut')
        if i%2==1:
            lamp(wharf,x,3.21,2.09,'#e9bb89',1.38)
    for x,z in [(-5.50,3.94),(-3.78,3.95),(2.86,3.95),(4.52,3.95)]:
        for h in (.77,1.30,1.84):
            wharf.box((x,h,z+.351),(1.27,.043,.044),'aged_steel')
        coil(wharf,x,2.276,z,.25,.021,4)
        wharf.sign('ledger',(x,1.97,z+.341),.284,.191,0,'zinc')
    wharf.rope([(-.19,3.82,2.94),(-.19,3.03,2.94),(-.19,2.82,2.94)],.026,'aged_steel',9)
    wharf.hoop((-.194,2.77,2.938),.081,.028,'zinc',segments=16)
    wharf.sign('rigel_plan',(3.59,1.55,-1.104),.76,.40)
    wharf.sign('closed',(-2.22,2.91,-5.12),.80,.40,0,'aged_steel')


def build():
    props=Set('coastal_props')
    fittings(props)
    village=Set('coastal_street')
    streets(village)
    old_rooms(village)
    return props,village
