"""The north quay as a working town, with different trades on both sides of the road."""
from __future__ import annotations

import math
import random

from mesh import PI, TAU, Set, rotate_y

DOORS = {
    "fisher":(-25,0,-11),
    "miller":(-9,0,-11),
    "ward":(7,0,-11),
    "post":(-25,0,11),
    "cafe":(-9,0,11),
    "library":(7,0,11),
    "repair":(25,0,11),
    "clock":(25,0,-11),
}


def brick_foundation(mesh,w,d,key="fieldstone"):
    mesh.box((0,-.175,0),(w+.12,.35,d+.16),key,True)
    for side in (-1,1):
        mesh.box((side*(w/2+.046),.18,0),(.072,.34,d),key)
        for row in range(2):
            z=-d/2+.12+row*.21
            while z<d/2-.11:
                mesh.box((side*(w/2+.061),.12+row*.156,z),(.065,.136,.39),key)
                z+=.43


def wall(mesh,at,length,height,cladding,lining,openings=(),yaw=0,style="board"):
    """Solid wall segments and real openings, then laid exterior cladding."""
    def loc(u,y,v=0):
        x,dy,z=rotate_y((u,y,v),yaw)
        return at[0]+x,at[1]+dy,at[2]+z
    def section(lo,hi,bottom,top):
        if hi-lo<.023 or top-bottom<.023:
            return
        c=(lo+hi)/2
        base=(bottom+top)/2
        mesh.box(loc(c,base),(hi-lo,top-bottom,.194),lining,True,yaw)
        if style=="board":
            courses=math.floor(bottom/.192)
            while courses*.192<top:
                start=max(bottom,courses*.192)
                end=min(top,(courses+1)*.192)
                if end-start>.003:
                    v=.104
                    mesh.box(loc(c,(start+end)/2,v),(hi-lo,end-start-.001,.055),cladding,False,yaw)
                    if end-start>.063 and start-bottom>.002:
                        mesh.box(loc(c,start+.011,v+.0305),(hi-lo,.021,.018),cladding,False,yaw)
                courses+=1
        elif style=="batten":
            mesh.box(loc(c,base,.111),(hi-lo,top-bottom,.046),cladding,False,yaw)
            for n in range(math.ceil(lo/.155),math.ceil(hi/.155)):
                u=n*.155
                if lo+.019<u<hi-.019:
                    mesh.box(loc(u,base,.143),(.031,top-bottom,.023),cladding,False,yaw)
        else:
            mesh.box(loc(c,base,.111),(hi-lo,top-bottom,.045),cladding,False,yaw)
        if bottom<.082:
            mesh.box(loc(c,.089,-.107),(hi-lo,.12,.038),"oak",False,yaw)
        if top>=height-.003:
            mesh.box(loc(c,height-.112,-.103),(hi-lo,.09,.04),lining,False,yaw)
    previous=-length/2
    for center,width,sill,head,kind in sorted(openings):
        left,right=center-width/2,center+width/2
        section(previous,left,0,height)
        section(left,right,0,sill)
        section(left,right,head,height)
        previous=right
        if kind=="window" or kind=="shop":
            sash(mesh,loc,center,width,sill,head,yaw,kind=="shop")
        else:
            casing(mesh,loc,center,width,head,yaw,kind=="wide")
    section(previous,length/2,0,height)


def casing(mesh,loc,u,w,top,yaw,wide=False):
    for face in (-1,1):
        for x in (-w/2,w/2):
            mesh.box(loc(u+x,top/2,face*.151),(.116,top+.07,.079),"ivory",False,yaw)
            mesh.box(loc(u+x,top/2,face*.199),(.038,top,.023),"oak",False,yaw)
        mesh.box(loc(u,top+.038,face*.150),(w+.17,.119,.083),"ivory",False,yaw)
    mesh.box(loc(u,.041,.085),(w+.14,.068,.43),"fieldstone",False,yaw)
    if not wide:
        # Park the leaf alongside the open doorway.
        mesh.box(loc(u-w*.5+.043,top*.47,-.451),(.081,top-.15,.74),"walnut",True,yaw)
        for offset in (.19,.45,.73):
            mesh.box(loc(u-w*.5+.091,top*offset,-.451),(.029,.038,.66),"oak",False,yaw)
        for face in (-1,1):
            mesh.tube(loc(u-w*.5+.046,1.02+face*.015,-.721),
                      loc(u-w*.5+.117,1.02+face*.015,-.721),.023,"brass",10)


def sash(mesh,loc,u,w,sill,head,yaw,shop):
    middle=(sill+head)/2
    # Recessed glazing sits behind the exterior sill and the curtain rail.
    mesh.box(loc(u,middle,0),(w,head-sill,.014),"glazing",True,yaw)
    for face in (-1,1):
        for s in (-1,1):
            mesh.box(loc(u+w*.5*s,middle,.145*face),(.112,head-sill+.13,.078),"ivory",False,yaw)
        for h in (sill-.025,head+.026):
            mesh.box(loc(u,h,.151*face),(w+.18,.095,.112),"ivory",False,yaw)
        mesh.box(loc(u,sill-.072,.179*face),(w+.25,.071,.227),"oak",False,yaw)
        for ratio in ([-.25,0,.25] if shop else [0]):
            mesh.box(loc(u+ratio*w,middle,face*.062),(.044,head-sill,.045),"brass" if shop else "ivory",False,yaw)
        mesh.box(loc(u,middle,face*.062),(w,.046,.047),"brass" if shop else "ivory",False,yaw)
    if shop:
        for i in range(2):
            x=u+(.58+i*.19)*w/2
            coords=[loc(x-.069,head-.43,.027),loc(x-.026,head-.43,.027),
                    loc(x+.080,head-.095,.027),loc(x+.048,head-.095,.027)]
            mesh.quad(coords,"glazing")
    else:
        curtain(mesh,loc,u,w,sill,head)


def curtain(mesh,loc,u,w,bottom,top):
    mesh.tube(loc(u-w*.57,top+.169,-.182),loc(u+w*.57,top+.169,-.182),.023,"brass",9)
    for side in (-1,1):
        for s in range(9):
            t0=s/9
            t1=(s+1)/9
            def cloth(t,y,end):
                x=u+side*(w*.46-(.36 if end else .48)*w*t)
                return loc(x,y+.035*math.sin(t*12),-.161+.065*math.cos(t*19))
            poly=[cloth(t0,bottom-.124,True),cloth(t1,bottom-.124,True),
                  cloth(t1,top+.137,False),cloth(t0,top+.137,False)]
            mesh.quad(poly if side==1 else list(reversed(poly)),"linen")


def inner_wall(m,z,w,center=0,lining="plaster"):
    m.box(((center-1.03-w*.5)/2,1.45,z),(center-1.03+w*.5,2.90,.14),lining,True)
    m.box(((center+1.03+w*.5)/2,1.45,z),(w*.5-center-1.03,2.90,.14),lining,True)
    m.box((center,2.56,z),(2.06,.68,.14),lining,True)
    m.box((center,2.279,z),(2.14,.126,.248),"walnut")
    for side in (-1,1):
        m.box((center+side*1.064,1.12,z),(.107,2.24,.248),"oak")


def roof(mesh,w,d,wall_h,rise,skin,key,attic=False,flue=None):
    half=w/2+.33
    ext=d/2+.36
    edge=wall_h+.02
    high=wall_h+rise
    for rear in (-1,1):
        points=[(-w/2,edge-.06,rear*d/2),(w/2,edge-.06,rear*d/2),(0,high,rear*d/2)]
        mesh.add(points,[(0,1,2) if rear==1 else (2,1,0)],key)
        mesh.beam((-half,edge,rear*ext),(0,high+.007,rear*ext),.12,.16,"ivory")
        mesh.beam((half,edge,rear*ext),(0,high+.007,rear*ext),.12,.16,"ivory")
    for s in (-1,1):
        pts=[(0,high,-ext),(s*half,edge,-ext),(s*half,edge,ext),(0,high,ext)]
        if s==1: pts.reverse()
        slope=math.hypot(half,rise)
        roof_uv=[(0,0),(slope/1.8,0),(slope/1.8,d/1.8),(0,d/1.8)]
        if s==1: roof_uv.reverse()
        mesh.quad(pts,skin,roof_uv)
        mesh.quad(list(reversed(pts)),"fir")
        mesh.box((s*half,edge-.072,0),(.119,.142,2*ext+.025),"ivory")
        mesh.tube((s*(half+.096),edge-.041,-ext),(s*(half+.096),edge-.041,ext),.074,"zinc",10)
        drain_x=s*(half+.09)
        z=ext-.24
        mesh.rope([(drain_x,edge,z),(drain_x,.31,z),(drain_x+.035*s,.11,z+.24)],.047,"zinc",9)
        for j in range(int((d+.5)/.48)+1):
            zz=min(-ext+j*.49,ext)
            mesh.beam((s*half,edge+.032,zz),(0,high+.053,zz),.025,.034,skin)
            if j%4==1:
                mesh.box((s*(half+.1),edge-.035,zz),(.21,.087,.063),"aged_steel")
    mesh.tube((0,high+.049,-ext),(0,high+.049,ext),.073,"zinc",12)
    if flue:
        x,z=flue
        mesh.box((x,wall_h+rise*.54,z),(.59,1.68,.63),"brick_dark")
        for y in (wall_h+rise*.54+.75,wall_h+rise*.54+.84):
            mesh.box((x,y,z),(.71,.096,.73),"fieldstone")
        for dx in (-.19,.19):
            mesh.revolve((x+dx,wall_h+rise*.54+.87,z),[(0,.14),(.28,.127),(.33,.15)],"brick",12)
    if attic:
        for j in (-1,1):
            z=j*(d/2+.013)
            center=wall_h+rise*.42
            mesh.box((0,center,z),(1.14,.68,.068),"ivory")
            mesh.box((0,center,z+j*.044),(.963,.524,.033),"glass_green")
            mesh.box((0,center,z+j*.065),(.036,.55,.033),"ivory")
            mesh.box((0,center-.33,z+j*.093),(1.27,.067,.21),"oak")


def planks(m,w,d,kind,material="parquet"):
    m.box((0,-.049,0),(w,.111,d),material,True)
    span_count={"cafe":6,"post":2,"clock":4,"ward":7,"miller":5,"fisher":8,"library":5,"repair":5}[kind]
    beam="garnet" if kind=="cafe" else ("ivory" if kind=="post" else "fir")
    for i in range(span_count):
        z=(i+.5-span_count*.5)*d/span_count
        m.box((0,2.79,z),(w-.20,.14,.156),beam)
    if kind in ("cafe","post","library"):
        for side in (-1,1):
            m.box((side*(w*.5-.125),2.76,0),(.073,.120,d-.21),beam)
            m.box((side*(w*.5-.164),2.804,0),(.025,.055,d-.21),"brass")
    m.box((0,2.92,0),(w,.12,d),"plaster")


def rug(m,pos,w,d):
    x,y,z=pos
    m.quad([(x-w/2,y,z+d/2),(x+w/2,y,z+d/2),(x+w/2,y,z-d/2),(x-w/2,y,z-d/2)],
           "rug",[(0,0),(1,0),(1,1),(0,1)])
    for side in (-1,1):
        for i in range(30):
            xx=x+((i+.5)/30-.5)*w
            m.tube((xx,y+.004,z+side*(d/2-.032)),(xx+.008*math.sin(i),y+.002,z+side*(d/2+.073)),.0053,"linen",5)


def bench(m,x,z,w=1.62,material="oak"):
    for dx in (-w*.37,w*.37):
        m.box((x+dx,.21,z),(.135,.42,.33),"deep_steel",True)
        m.box((x+dx,.64,z-.20),(.081,.63,.075),"deep_steel")
    for n in range(4):
        m.box((x,.454,z-.19+n*.126),(w,.064,.111),material)
    for i in range(3):
        m.box((x,.67+i*.124,z-.24),(w,.105,.046),material)
    m.collision((x,.50,z),(w,.92,.55))


def table(m,x,z,w,d,h=.76,material="oak",yaw=0,soft=False):
    put=m.soft if soft else m.box
    if soft:
        put((x,h,z),(w,.09,d),material,.08,yaw,True)
    else:
        put((x,h,z),(w,.086,d),material,True,yaw)
    for dx in (-1,1):
        for dz in (-1,1):
            local=rotate_y((dx*(w/2-.085),0,dz*(d/2-.083)),yaw)
            leg=(x+local[0],z+local[2])
            m.box((leg[0],(h-.03)/2,leg[1]),(.067,h-.03,.071),material,False,yaw)
    for d_side in (-1,1):
        local=rotate_y((0,0,d_side*(d/2-.066)),yaw)
        m.box((x+local[0],h-.104,z+local[2]),(w-.13,.14,.042),material,False,yaw)


def chair(m,x,z,yaw=0,style="green_cloth",detour=False):
    def v(dx,y,dz):
        xx,yy,zz=rotate_y((dx,y,dz),yaw)
        return (x+xx,yy,z+zz)
    m.soft(v(0,.455,0),(.45,.09,.42),style,.06,yaw)
    for side in (-1,1):
        m.beam(v(side*.174,.43,-.158),v(side*.218,.012,-.182),.040,.039,"walnut")
        m.beam(v(side*.174,.43,.163),v(side*.210,.014,.192),.041,.039,"walnut")
        m.beam(v(side*.176,.43,-.166),v(side*.202,.877,-.209),.046,.051,"walnut")
    m.soft(v(0,.792,-.192),(.42,.171,.059),style,.049,yaw)
    if detour:
        m.collision(v(0,.45,0),(.43,.88,.43),yaw)


def cup(m,x,y,z,color="porcelain",inside="soup"):
    profile=[(0,.062),(.014,.071),(.084,.074),(.094,.069),(.086,.062),(.02,.054)]
    m.revolve((x,y,z),profile,color,16, caps=False)
    m.revolve((x,y+.074,z),[(0,.059),(.002,.059)],inside,16)
    m.hoop((x+.081,y+.055,z),.037,.007,color)
    dish(m,x,y+.002,z,.11,color)


def dish(m,x,y,z,r=.13,material="porcelain"):
    m.revolve((x,y,z),[(0,r*.71),(.009,r*.94),(.020,r),(.026,r*.965),(.019,r*.81),(.013,r*.38)],material,20)


def bottle(m,x,y,z,color="glass_green",height=.23):
    p=[(0,.042),(.019,.049),(.54*height,.051),(.71*height,.043),(.80*height,.024),
       (.93*height,.022),(.95*height,.029),(height,.026)]
    m.revolve((x,y,z),p,color,12)
    m.revolve((x,y+.82*height,z),[(0,.024),(.022,.025)],"brass",10)
    m.revolve((x,y+.08,z),[(0,.052),(.041,.052)],"paper",12,caps=False)


def stool(m,x,z,y=.46,finish="teal_leather"):
    m.revolve((x,y,z),[(-.054,.173),(-.021,.206),(.025,.204),(.041,.18)],finish,16)
    for i in range(3):
        ang=i*TAU/3+.41
        m.beam((x+.13*math.cos(ang),y-.05,z+.13*math.sin(ang)),
               (x+.21*math.cos(ang),.02,z+.21*math.sin(ang)),.047,.054,"oak")
    m.hoop((x,y*.48,z),.16,.018,"deep_steel","y")
    m.collision((x,y*.51,z),(.37,y*1.02,.37))


def stacks(m,x,z,w=.20,y=.02,count=4,key="paper"):
    for i in range(count):
        angle=.16*math.sin(i*1.75)
        px=x+math.cos(i*2.7)*.032
        m.box((px,y+.009+i*.024,z+.036*math.sin(i)),(w,.015,w*.71),key,False,angle)


def book(m,x,y,z,w,h,depth,coat="garnet",yaw=0):
    m.box((x,y+h/2,z),(w,h,depth),coat,False,yaw)
    lx,ly,lz=rotate_y((0,h/2,depth*.5+.0015),yaw)
    m.box((x+lx,y+ly,z+lz),(w*.89,h*.77,.007),"paper",False,yaw)
    for side in (-1,1):
        xx,yy,zz=rotate_y((w*.37*side,h/2,depth*.515),yaw)
        m.box((x+xx,y+yy,z+zz),(.010,h*.83,.012),coat,False,yaw)


def shelf(m,x,z,width,depth=0.46,h=2.02,book_rows=True,seed=12,material="walnut"):
    rnd=random.Random(seed)
    for dx in (-width/2,width/2):
        m.box((x+dx,h/2,z),(.084,h,depth),material,True)
    m.box((x,h/2,z-depth*.5),(width,h,.048),"fir")
    for i in range(5):
        y=.11+(h-.16)*i/4
        m.box((x,y,z),(width,.064,depth+.033),material,True)
        if not book_rows or i==4: continue
        cursor=-width/2+.068
        while cursor<width/2-.12:
            w=rnd.uniform(.044,.126)
            h_book=rnd.uniform(.17,.34)
            d_book=rnd.uniform(.15,.34)
            paint=rnd.choice(["garnet","sea_green","cream_siding","blue_siding","walnut","olive_siding"])
            if rnd.random()<.85:
                book(m,x+cursor+w/2,y+.032,z-depth/2+d_book/2,w,h_book,d_book,paint)
                m.box((x+cursor+w/2,y+.075,z+depth*.10+d_book*.21),(w*.56,.024,.007),"brass")
            cursor+=w+.013


def cabinet(m,x,z,w=2.4,depth=.56,h=.89,front="sea_green",counter="walnut"):
    m.box((x,h/2,z),(w,h,depth),front,True)
    m.box((x,h+.029,z),(w+.07,.058,depth+.059),counter)
    n=max(2,round(w/.49))
    for j in range(n):
        x0=x+(j+.5-n*.5)*w/n
        m.box((x0,h*.49,z+depth*.5+.016),(w/n-.053,h*.79,.046),front)
        m.box((x0,h*.54,z+depth*.5+.053),(w/n-.145,h*.57,.029),front)
        m.revolve((x0+w/n*.25,h*.72,z+depth*.5+.058),
                  [(0,.022),(.014,.031),(.025,.026)],"brass",11,(0,0,1))
        m.box((x0,.099,z+depth*.5+.046),(w/n-.046,.128,.045),"walnut")


def picture(m,card,x,y,z,w=.56,h=.34,yaw=0):
    m.sign(card,(x,y,z),w,h,yaw)


def lamp(m,x,y,z,color="#ffd49b",power=1.85):
    m.revolve((x,y-.18,z),[(0,.219),(.035,.215),(.185,.125),(.209,.091)],"glass_amber",17)
    m.blob((x,y-.157,z),(.065,.065,.065),"bulb",segments=11,rings=5)
    m.tube((x,y+.03,z),(x,2.84,z),.015,"brass",8)
    m.light((x,y-.265,z),color,power,6.8,True)


def plant(m,x,z,y=0,size=1.0,rng=None,flower=True):
    rnd=rng or random.Random(round((x+43)*(z+24)*325))
    m.revolve((x,y,z),[(0,.124*size),(.027*size,.131*size),(.235*size,.187*size),
                        (.27*size,.205*size),(.307*size,.201*size),(.311*size,.174*size),
                        (.26*size,.168*size)],"ceramic_red",14,caps=False)
    m.revolve((x,y+size*.265,z),[(0,.170*size),(.007,.171*size)],"moss",12)
    leaves(m,x,y+size*.27,z,size*.79,rnd,flower)
    if y<.08:
        m.collision((x,y+.153*size,z),(.35*size,.306*size,.35*size))


def leaves(m,x,y,z,scale,rnd,flowers):
    for i in range(12):
        a=rnd.uniform(0,TAU)
        tip_h=rnd.uniform(.22,.64)*scale
        reach=rnd.uniform(.11,.36)*scale
        sx,sz=math.cos(a),math.sin(a)
        top=(x+sx*reach,y+tip_h,z+sz*reach)
        m.tube((x,y,z),top,.009*scale,"moss_green",5)
        for t in (.46,.75,.95):
            cx=x+sx*reach*t
            cy=y+tip_h*t
            cz=z+sz*reach*t
            along=(sx*.16*scale,sz*.16*scale)
            across=(-sz*.05*scale,sx*.05*scale)
            top_leaf=(cx+along[0],cy+scale*.017,cz+along[1])
            vert=[(cx,cy,cz),(cx+along[0]*.48+across[0],cy+.035*scale,cz+along[1]*.48+across[1]),top_leaf,
                  (cx+along[0]*.48-across[0],cy+.023*scale,cz+along[1]*.48-across[1])]
            material=["leaf","leaf_light","leaf_dark"][i%3]
            m.quad(vert,material)
            m.quad(list(reversed(vert)),material)
        if flowers and i%3==0:
            m.blob(top,(.041*scale,.018*scale,.042*scale),"petal",segments=8,rings=4)
            m.blob((top[0],top[1]+.014*scale,top[2]),(.019*scale,.010*scale,.019*scale),"flower",segments=8,rings=4)


def boot_pair(m,x,z):
    for dx in (0,.215):
        m.soft((x+dx,.065,z+.043),(.16,.13,.31),"tire",.05,yaw=.08*math.sin(dx*10))
        m.revolve((x+dx,.085,z-.039),[(0,.095),(.082,.087),(.275,.079),(.303,.084),(.307,.061)],"tire",13,caps=False)
        m.box((x+dx,.050,z+.054),(.16,.029,.30),"tar")


def hooks(m,x,z,kind="rouge_cloth"):
    m.box((x,1.71,z),(.91,.119,.06),"walnut")
    for i in range(4):
        sx=x-.31+i*.2
        m.rope([(sx,1.72,z+.025),(sx,1.66,z+.087),(sx,1.67,z+.115)],.021,"brass",6)
    m.soft((x-.29,1.25,z+.135),(.35,.77,.19),kind,.14)
    m.beam((x-.40,1.555,z+.168),(x-.55,1.063,z+.193),.119,.12,kind)
    m.beam((x-.17,1.553,z+.154),(x-.074,1.10,z+.172),.121,.124,kind)
    m.box((x-.275,1.32,z+.232),(.02,.57,.008),"brass")


def kettle(m,x,y,z,mat="porcelain"):
    m.revolve((x,y,z),[(0,.117),(.022,.13),(.085,.134),(.15,.102),(.174,.053),(.184,.052)],mat,18)
    m.revolve((x,y+.18,z),[(0,.056),(.013,.052),(.029,.026),(.041,.019)],"brass",12)
    m.rope([(x-.08,y+.045,z),(x-.17,y+.068,z+.008),(x-.223,y+.156,z+.015),(x-.209,y+.179,z+.017)],.031,mat,9)
    m.rope([(x+.074,y+.151,z),(x+.166,y+.171,z),(x+.188,y+.119,z),(x+.142,y+.074,z),(x+.098,y+.073,z)],.013,"walnut",8)


def tape_deck(m,x,y,z,scale=1,age=0):
    w=.72*scale
    m.soft((x,y+.185*scale,z),(w,.37*scale,.35*scale),"aged_steel",.035)
    m.box((x,y+.181*scale,z+.182*scale),(.669*scale,.309*scale,.022*scale),"sand_enamel")
    m.box((x,y+.041*scale,z+.201*scale),(.67*scale,.061*scale,.018*scale),"black")
    for s in (-1,1):
        rx=x+s*.18*scale
        ry=y+.264*scale
        m.revolve((rx,ry,z+.199*scale),[(0,.12*scale),(.020*scale,.117*scale)],"tar" if s==1 else "aged_steel",22,(0,0,1))
        m.hoop((rx,ry,z+.226*scale),.112*scale,.012*scale,"ivory",segments=24)
        for k in range(4):
            a=k*PI/2+.24*s
            m.tube((rx,ry,z+.229*scale),(rx+.106*math.cos(a)*scale,ry+.106*math.sin(a)*scale,z+.229*scale),.022*scale,"sand_enamel",8)
        m.revolve((rx,ry,z+.229*scale),[(0,.034*scale),(.024*scale,.027*scale)],"brass",10,(0,0,1))
    for i in range(5):
        m.box((x+(.063*i-.126)*scale,y+.068*scale,z+.224*scale),(.047*scale,.021*scale,.024*scale),"signal" if i==0 else "ivory")
    m.box((x,y+.135*scale,z+.208*scale),(.095*scale,.052*scale,.016*scale),"glass_amber")
    for i in range(7):
        m.box((x+(i-3)*.012*scale,y+.143*scale,z+.219*scale),(.003*scale,.016*scale,.005*scale),"amber" if i<5 else "signal")
    if age:
        m.box((x,y+.357*scale,z),(.742*scale,.018,.37*scale),"walnut")


def desk_lamp(m,x,y,z):
    m.revolve((x,y,z),[(0,.098),(.026,.111),(.043,.096),(.057,.043)],"brass",16)
    m.rope([(x,y+.05,z),(x-.028,y+.235,z+.014),(x-.012,y+.39,z+.013),
            (x+.103,y+.458,z-.022),(x+.215,y+.434,z+.009)],.018,"brass",10)
    m.revolve((x+.223,y+.359,z+.008),[(0,.157),(.028,.155),(.061,.113),(.100,.069),(.108,.044)],"sea_green",19)
    m.blob((x+.223,y+.354,z+.008),(.055,.037,.055),"bulb",segments=12)
    m.light((x+.23,y+.27,z+.05),"#f7bc76",.65,2.85,False)


def bread(m,x,y,z,cut=False):
    m.soft((x,y+.064,z),(.34,.128,.21),"toast",.08,yaw=.12)
    for i in range(4):
        m.box((x+(i-1.5)*.063,y+.128,z),(.024,.005,.104),"peel",False,-.34)
    if cut:
        for i in range(3):
            m.soft((x+.33+i*.046,y+.054,z+.01),(.036,.103,.169),"peel",.018)


def crate(m,x,y,z,w=.63,d=.43,h=.36,key="fir",solid=False):
    m.box((x,y+.036,z),(w,.071,d),key,solid)
    for side in (-1,1):
        for zside in (-1,1):
            m.box((x+side*(w*.5-.046),y+h*.5,z+zside*(d*.5-.048)),(.076,h,.076),"walnut")
        for j in range(3):
            cy=y+h*(j+.5)/3
            m.box((x,cy,z+side*d*.50),(w,.78*h/3,.034),key)
            m.box((x+side*w*.5,cy,z),(.035,.79*h/3,d),key)
        for dx in (-.38,.38):
            for j in range(3):
                m.blob((x+w*dx,y+h*(j+.54)/3,z+side*(d*.5+.021)),(.009,.009,.004),"chrome",segments=6,rings=3)
    if solid:
        m.collision((x,y+h/2,z),(w,h,d))


def barrel(m,x,y,z,r=.26,h=.68,material="fir",solid=True):
    m.revolve((x,y,z),[(0,r*.87),(.07*h,r*.92),(.30*h,r),(.72*h,r*.99),(.98*h,r*.89),(h,r*.86)],material,22)
    for ratio in (.13,.31,.73,.91):
        rr=r*(.935 if ratio in (.13,.91) else 1.02)
        m.revolve((x,y+h*ratio,z),[(0,rr),(.037,rr)],"aged_steel",22,caps=False)
    for k in range(10):
        a=k*TAU/10
        def p(length,dist):
            return x+dist*math.sin(a),y+h*length,z+dist*math.cos(a)
        m.rope([p(.045,r*.907),p(.31,r*1.001),p(.70,r*.995),p(.98,r*.891)],.0035,"walnut",5)
    if solid and y<.12 and h>.25:
        m.collision((x,y+h*.51,z),(r*1.79,h,r*1.79))


def coil(m,x,y,z,major=.27,thickness=.021,turns=5,key="rope"):
    points=[]
    for i in range(24*turns+1):
        u=i/(24*turns)
        a=u*TAU*turns
        r=major*(.45+.55*u)
        points.append((x+r*math.cos(a),y+.03*math.sin(u*PI)+.008*math.sin(a*.6),z+r*math.sin(a)))
    points.extend([(x+major+.07,y,z+.08),(x+major+.22,y+.011,z+.082),(x+major+.31,y+.012,z+.007)])
    m.rope(points,thickness,key,6)


def net_panel(m,x,y,z,w,h,tension=.21,rows=10,cols=15):
    coords=[]
    for row in range(rows+1):
        t=row/rows
        items=[]
        for col in range(cols+1):
            u=col/cols
            items.append((x+(u-.5)*w+(.5*(row%2))*w/cols,
                y-h*t-.07*math.sin(u*PI),z+tension*math.sin(u*PI)*math.sin(t*PI)+.043*math.sin(u*11+t*7)))
        coords.append(items)
    for row in range(rows):
        for col in range(cols):
            pair=coords[row][col]
            m.tube(pair,coords[row+1][col],.0056,"net",5)
            next_col=col+(-1 if row%2==0 else 1)
            if 0<=next_col<=cols:
                m.tube(pair,coords[row+1][next_col],.0056,"net",5)
            if row%3==0 and col%3==0:
                m.blob(pair,(.013,.01,.013),"rope",segments=7,rings=4)
    m.tube(coords[0][0],coords[0][-1],.020,"rope",8)
    for i in range(0,len(coords[0]),3):
        px,py,pz=coords[0][i]
        m.blob((px,py,pz),(.047,.042,.049),"cork",segments=9,rings=5)


def fish(m,x,y,z,scale=1,yaw=0):
    pieces=[(0,.009),(.06,.036),(.15,.05),(.237,.035),(.29,.011)]
    axis=rotate_y((1,0,0),yaw)
    m.revolve((x,y,z),[(pos*scale,w*scale) for pos,w in pieces],"glass_green",9,axis)
    p0=rotate_y((.283*scale,0,0),yaw)
    p1=rotate_y((.356*scale,0,.056*scale),yaw)
    p2=rotate_y((.362*scale,0,-.057*scale),yaw)
    v=[(x+a,y+b+.015,z+c) for a,b,c in (p0,p1,p2)]
    m.add(v,[(0,1,2),(0,2,1)],"aged_steel")
    p=rotate_y((.039*scale,.036*scale,.02*scale),yaw)
    m.blob((x+p[0],y+p[1],z+p[2]),(.013,.008,.013),"ink",segments=6,rings=4)


def bobber(m,x,y,z,color="garnet"):
    m.blob((x,y,z),(.055,.094,.055),color,rings=6)
    m.revolve((x,y+.012,z),[(0,.057),(.028,.056)],"ivory",11)
    m.tube((x,y+.067,z),(x,y+.155,z),.011,"walnut",6)


def fisherman(m):
    inner_wall(m,-.96,8.82,-.08,"plaster")
    table(m,-2.26,.68,2.16,.99,.82,"fir")
    m.box((-2.28,.875,.68),(1.68,.023,.76),"sea_green")
    m.sheet("ledger",(-2.30,.927,.85),.43,.272,-.16)
    m.box((-2.30,.903,.85),(.45,.050,.286),"walnut",False,-.16)
    m.anchor("log",(-2.30,.986,.863))
    m.beam((-2.01,.926,.85),(-1.85,.926,.72),.013,.013,"brass")
    desk_lamp(m,-3.00,.869,.36)
    chair(m,-2.77,1.61,PI*.88,"canvas",True)
    shelf(m,-3.55,-.59,1.32,.35,1.45,False,17,"fir")
    for i in range(4):
        barrel(m,-3.97+i*.262,.154,-.51,.108,.28,"oak")
    coil(m,-3.58,1.178,-.52,.156,.014,4)
    fisherman_tools(m,-1.46,-.843)
    net_panel(m,2.65,2.43,.27,2.68,1.29,.15)
    for k in range(5):
        m.tube((1.25+k*.72,2.65,.26),(1.25+k*.72,2.33,.26),.019,"rust",7)
    coil(m,3.02,.051,1.07,.36,.022)
    coil(m,3.48,.059,1.79,.272,.021,4,"net")
    for i in range(5):
        bobber(m,-3.69+i*.27,1.31,-.81,"rouge_cloth" if i%2 else "ceramic_blue")
    m.box((-3.15,1.15,-.79),(1.82,.086,.22),"walnut")
    for i in range(3):
        barrel(m,3.64-.59*i,0,-2.89, .25+.027*(i%2),.62)
    hooks(m,2.39,-.77,"canvas")
    boot_pair(m,3.59,2.84)
    cabinet(m,-2.78,-3.10,2.68,.66,.83,"olive_siding")
    for i in range(4):
        bottle(m,-3.56+i*.22,.895,-3.08,"glass_amber")
    crate(m,-1.94,0,-2.46,.69,.54,.31,"fir",True)
    for i in range(4):
        fish(m,-2.18+.105*i,.143,-2.58,.91,-1.22)
    rug(m,(.16,.017,2.65),1.22,1.33)
    picture(m,"old_headland",3.63,1.77,-.86,.46,.31)
    lamp(m,-1.54,2.50,1.31,power=1.65)
    lamp(m,-1.68,2.52,-2.50,color="#dbd2b5",power=1.01)


def stovepipe(m,x,z):
    m.soft((x,.43,z),(.77,.73,.63),"coal",.065,solid=True)
    m.box((x,.50,z+.324),(.51,.335,.046),"aged_steel")
    m.box((x,.519,z+.350),(.44,.249,.022),"glass_amber")
    m.box((x+.215,.49,z+.371),(.095,.024,.016),"brass")
    for side in (-1,1):
        m.box((x+side*.28,.11,z),(.10,.18,.49),"deep_steel")
    m.revolve((x,.79,z-.13),[(0,.097),(.041,.11),(1.94,.087)],"coal",14)
    kettle(m,x-.12,.826,z+.090,"ceramic_red")
    m.light((x,.52,z+.56),"#e99b66",.60,2.5)


def bed(m,x,z,style="blanket"):
    m.soft((x,.287,z),(1.47,.29,2.16),"walnut",.077,solid=True)
    m.soft((x,.515,z),(1.44,.25,2.09),"linen",.085,solid=True)
    m.soft((x,.662,z+.27),(1.45,.108,1.59),style,.044)
    m.soft((x,.71,z-.446),(1.42,.092,.23),"rouge_cloth",.038)
    m.blob((x-.293,.689,z-.775),(.274,.117,.266),"linen",segments=14,rings=8,jitter=.065)
    m.blob((x+.28,.69,z-.752),(.254,.096,.256),"canvas",segments=14,rings=8,jitter=.045)
    m.box((x,.78,z-1.035),(1.58,1.02,.112),"walnut",True)
    for i in range(8):
        m.box((x-.689+i*.197,.882,z-.967),(.067,.74,.048),"oak")
    for dx in (-.73,.73):
        m.blob((x+dx,1.35,z-1.02),(.061,.079,.062),"brass",segments=10,rings=5)
    for j in range(9):
        m.box((x,.707,z-.17+j*.136),(1.36,.005,.012),"linen")


def sofa(m,x,z,length=1.9,front=PI):
    def v(px,y,pz):
        xx,yy,zz=rotate_y((px,y,pz),front)
        return x+xx,yy,z+zz
    for dx in (-length*.38,length*.38):
        for dz in (-.26,.26):
            m.box(v(dx,.15,dz),(.10,.23,.09),"walnut",False,front)
    m.soft(v(0,.36,0),(length,.28,.77),"teal_leather",.118,front,True)
    m.soft(v(0,.68,-.317),(length,.61,.193),"teal_leather",.08,front,True)
    for dx in (-length/2+.083,length/2-.083):
        m.soft(v(dx,.615,.00),(.147,.36,.78),"teal_leather",.068,front)
        m.soft(v(dx*.53,.517,.033),(length*.40,.148,.577),"green_cloth",.063,front)
        m.blob(v(dx*.70,.737,-.14),(.19,.21,.082),"rouge_cloth" if dx<0 else "canvas",segments=12,rings=6,jitter=.07)


def miller(m):
    inner_wall(m,-.78,8.56,.43,"sage_plaster")
    sofa(m,2.41,3.17,2.65,PI)
    rug(m,(2.35,.017,1.46),2.30,2.58)
    radiator(m,4.15,1.19,-PI/2)
    picture(m,"town_print",4.20,1.84,.10,.71,.47,-PI/2)
    table(m,2.43,1.38,1.1,.68,.53,"walnut",.08,True)
    cup(m,2.19,.59,1.41,"porcelain")
    stacks(m,2.66,1.31,.20,.585,3,"paper")
    table(m,-2.33,.72,1.81,.79,.76)
    m.sign("family_photo",(-2.35,1.132,.44),.54,.325)
    m.anchor("photo",(-2.30,.981,.875))
    picture(m,"old_headland",-2.88,1.62,-.662,.48,.30)
    picture(m,"town_print",-2.04,1.70,-.662,.71,.47)
    chair(m,-2.10,1.55,PI*.81,"canvas",True)
    stovepipe(m,3.32,-.11)
    cabinet(m,1.74,-.53,.72,.39,.60,"sage_plaster")
    stacks(m,1.74,-.49,.19,.65,3)
    clock_dial(m,2.38,2.19,-.65,.21,time=3.15)
    plant(m,-3.24,2.66,size=1.20)
    cabinet(m,-3.13,-3.34,2.08,.63,.81,"cream_siding")
    bed(m,2.74,-2.43,"blanket")
    desk_lamp(m,-3.78,.873,-3.32)
    cup(m,-2.58,.876,-3.23,"ceramic_blue")
    m.sheet("post_letter",(-3.01,.873,-3.30),.287,.198,.09)
    for i in range(5):
        book(m,-3.17+i*.106,.882,-3.49,.061,.17+.023*math.sin(i),.119,"sea_green" if i%3 else "garnet")
    lamp(m,1.72,2.49,1.55,power=1.58)
    lamp(m,1.36,2.51,-2.34,power=1.23)


def enamel_sink(m,x,z):
    cabinet(m,x,z,1.41,.65,.86,"blue_siding","ivory")
    m.soft((x,.902,z),(.76,.043,.49),"chrome",.015)
    m.soft((x,.926,z),(.668,.026,.398),"deep_glass",.009)
    m.rope([(x-.05,.92,z-.22),(x-.05,1.18,z-.22),(x-.049,1.22,z-.15),
            (x-.05,1.20,z-.064)],.022,"brass",10)
    for dx in (-.17,.17):
        m.revolve((x+dx,.927,z-.206),[(0,.042),(.074,.023),(.081,.041)],"brass",11)
    for i in range(3):
        m.box((x+.497,.897,z+(i-1)*.105),(.179,.023,.021),"chrome")


def ward(m):
    inner_wall(m,-.39,9.26,0,"plaster")
    wall_panels(m,-4.61,2.76,1.07)
    wall_panels(m,-4.61,-1.61,1.35)
    radiator(m,-4.39,1.35,PI/2)
    cabinet(m,-3.91,-.04,.72,.43,.66,"walnut")
    m.soft((-3.92,.774,-.02),(.62,.17,.35),"deep_steel",.04)
    m.box((-3.94,.774,.168),(.39,.091,.024),"black")
    for j in range(6):
        m.box((-4.07+j*.049,.781,.184),(.018,.035,.011),"volt" if j%3 else "amber")
    rug(m,(-2.44,.016,1.19),2.43,2.39)
    table(m,-2.365,.73,2.16,1.02,.806,"walnut")
    tape_deck(m,-2.30,.857,.563,1.02,1)
    m.anchor("family",(-2.30,1.077,.85))
    desk_lamp(m,-3.14,.858,.58)
    cup(m,-1.64,.86,.75)
    stacks(m,-1.67,.36,.22,.856,4)
    m.sheet("radio_book",(-2.81,.866,.895),.26,.173,-.20)
    chair(m,-2.03,1.68,PI-.19,"green_cloth",True)
    # Listening headset, its cord and a wall chart behind the deck.
    arch=[(-2.72+.152*math.cos(q*PI/20),.891+.045*math.sin(q*PI/20),1.024+.136*math.sin(q*PI/20)) for q in range(21)]
    m.rope(arch,.013,"black",8)
    for dx in (-.164,.164):
        m.soft((-2.72+dx,.891,1.025),(.053,.067,.099),"aged_steel",.022)
    m.rope([(-2.859,.89,1.05),(-2.93,.891,.987),(-2.66,.88,.805),(-2.31,.91,.597)],.007,"tar",6)
    m.box((-2.71,1.702,-.283),(1.59,.95,.062),"cork")
    m.sign("chart",(-2.72,1.701,-.246),1.39,.779,frame=None)
    picture(m,"old_headland",-3.873,1.80,-.253,.48,.31)
    m.box((-2.168,1.409,-.248),(.228,.162,.014),"paper",False,.10)
    m.box((-3.253,1.528,-.251),(.233,.218,.011),"paper")
    clock_dial(m,-1.522,2.201,-.216,.170,time=4.16)
    for px in (-3.34,-2.11):
        m.blob((px,2.050,-.244),(.016,.014,.017),"brass",segments=8,rings=4)
    picture(m,"family_photo",2.18,1.72,-.28,.48,.30)
    picture(m,"old_headland",2.85,1.84,-.28,.64,.39)
    rug(m,(1.82,.019,1.77),2.31,2.42)
    sofa(m,2.79,3.09,2.19,PI)
    table(m,2.68,1.38,.94,.62,.498,"walnut")
    bottle(m,2.87,.553,1.40,"glass_green",.182)
    cup(m,2.42,.557,1.54,"ceramic_blue")
    m.box((2.67,.021,-2.09),(3.84,.024,3.38),"kitchen_tile")
    enamel_sink(m,3.40,-3.07)
    cabinet(m,2.17,-3.07,.92,.64,.86,"blue_siding","ivory")
    for px in (1.96,2.32):
        for zz in (-3.19,-2.95):
            m.revolve((px,.924,zz),[(0,.095),(.015,.096)],"coal",13)
    kettle(m,2.27,.943,-3.12,"ceramic_blue")
    m.box((3.46,1.97,-3.32),(1.36,.64,.37),"blue_siding")
    m.box((3.46,1.66,-3.31),(1.41,.048,.41),"oak")
    for dx in (-.346,.346):
        m.box((3.46+dx,1.97,-3.119),(.64,.58,.044),"blue_siding")
        m.box((3.46+dx,1.96,-3.093),(.51,.444,.018),"deep_glass")
        m.box((3.46+dx,1.96,-3.074),(.036,.45,.023),"oak")
        m.box((3.46+dx,1.96,-3.072),(.52,.030,.023),"oak")
    # A small crock and a rail of hanging utensils keep the sink in use.
    bottle(m,3.76,.936,-2.91,"glass_amber",.155)
    m.tube((1.48,1.56,-3.20),(2.57,1.56,-3.20),.017,"aged_steel",9)
    for i in range(3):
        px=1.65+i*.28
        m.tube((px,1.55,-3.19),(px,1.26,-3.173),.013,"brass",8)
        m.blob((px,1.27,-3.17),(.057,.093,.022),"chrome",segments=9,rings=6)
    table(m,-2.96,-2.23,1.65,.74,.765,"oak")
    chair(m,-3.77,-2.42,PI/2,"canvas",True)
    dish(m,-3.17,.816,-2.20,.129,"porcelain")
    bread(m,-2.66,.810,-2.24,True)
    hooks(m,-2.57,-3.58,"canvas")
    boot_pair(m,-1.61,-3.46)
    lamp(m,-1.88,2.48,1.20,power=1.67)
    lamp(m,2.04,2.51,1.73,power=1.12)
    lamp(m,1.42,2.48,-2.55,color="#f4dba8",power=1.30)


def clock_dial(m,x,y,z,r=0.37,key="ivory",time=4.87):
    m.revolve((x,y,z),[(0,r*1.045),(.03,r*1.11),(.062,r*1.05),(.069,r*.94)],
              "walnut",48,(0,0,1))
    m.revolve((x,y,z+.073),[(0,r*.934),(.011,r*.934)],key,48,(0,0,1))
    m.hoop((x,y,z+.085),r*.952,r*.029,"brass",segments=52)
    for k in range(60):
        a=TAU*k/60
        r0=r*(.702 if k%5==0 else .820)
        r1=r*.879
        p0=(x+math.sin(a)*r0,y+math.cos(a)*r0,z+.098)
        p1=(x+math.sin(a)*r1,y+math.cos(a)*r1,z+.098)
        m.beam(p0,p1,r*(.033 if k%5==0 else .0135),.014,"ink")
    for a,n in ((time*PI/6,.53),((time%1)*TAU,.75)):
        m.beam((x,y,z+.108),(x+math.sin(a)*r*n,y+math.cos(a)*r*n,z+.108),r*.061,.016,"ink")
    m.revolve((x,y,z+.112),[(0,r*.077),(.023,r*.055)],"brass",14,(0,0,1))


def mail_cubbies(m,x,y,z,width=3.27,columns=9,rows=5):
    h=rows*.267
    m.box((x,y+h/2,z),(width,h,.28),"fir")
    for i in range(rows+1):
        m.box((x,y+i*.267,z+.062),(width,.032,.365),"walnut")
    for k in range(columns+1):
        px=x+width*(k/columns-.5)
        m.box((px,y+h/2,z+.062),(.028,h+.024,.377),"oak")
    for col in range(columns):
        for row in range(rows):
            px=x+(col+.52-columns/2)*width/columns
            py=y+.032+row*.267
            m.box((px,py+.004,z+.25),(.079,.035,.007),"brass")
            if (col+2*row)%4:
                for j in range(2+(col+row)%3):
                    m.box((px+.011*math.cos(j),py+.033+.014*j,z+.137+.014*math.sin(j)),
                          (.191,.008,.157),"paper",False,.12*math.cos(j))
                m.box((px+.072,py+.05,z+.218),(.036,.042,.012),"garnet")


def postal(m):
    cabinet(m,-2.32,.43,3.47,.82,.90,"garnet","walnut")
    m.box((-2.32,.927,.85),(3.43,.026,.034),"brass")
    # Counter grille and oak standing shelf beneath the post windows.
    for i in range(13):
        x=-3.91+i*.259
        m.tube((x,1.18,.20),(x,2.11,.20),.012,"brass",7)
    for y in (1.18,2.10):
        m.box((-2.34,y,.20),(3.34,.061,.062),"walnut")
    mail_cubbies(m,-2.14,.94,-3.67)
    stacks(m,-2.77,.57,.288,.957,5)
    m.sheet("post_letter",(-1.93,.965,.62),.29,.19,.11)
    m.soft((-3.25,1.08,.58),(.41,.214,.321),"aged_steel",.038)
    m.revolve((-3.25,1.215,.58),[(0,.201),(.019,.207),(.032,.197)],"chrome",20)
    m.revolve((-3.25,1.123,.761),[(0,.077),(.011,.078)],"glass_amber",17,(0,0,1))
    clock_dial(m,.57,1.98,-3.70,.258,time=8.36)
    for j in range(2):
        crate(m,3.49-j*.69,0,-2.87,.58,.46,.32,"oak",True)
        m.box((3.49-j*.69,.41,-2.89),(.449,.231,.346),"paper",False,.23*j)
        m.box((3.49-j*.69,.531,-2.89),(.456,.007,.072),"cork",False,.23*j)
    hooks(m,3.72,-3.58,"blanket")
    bench(m,2.82,1.85,1.65)
    picture(m,"post_hours",2.56,1.76,3.60,.62,.43,PI)
    rug(m,(-.04,.019,2.57),1.38,1.55)
    lamp(m,-1.9,2.41,1.12,power=1.43)
    lamp(m,-1.7,2.43,-2.15,power=1.22)


def espresso(m,x,z):
    m.soft((x,1.088,z),(.84,.204,.51),"aged_steel",.045)
    m.soft((x,1.336,z-.09),(.76,.38,.32),"ivory",.071)
    m.soft((x,1.55,z-.11),(.78,.12,.385),"chrome",.049)
    m.box((x,1.182,z+.21),(.69,.041,.194),"chrome")
    for j in range(11):
        m.box((x-.29+j*.061,1.205,z+.20),(.014,.013,.175),"coal")
    for dx in (-.215,.215):
        m.tube((x+dx,1.32,z+.134),(x+dx,1.231,z+.173),.036,"chrome",11)
        m.tube((x+dx,1.289,z+.117),(x+dx,1.299,z+.371),.023,"walnut",10)
    m.hoop((x-.27,1.48,z+.083),.038,.008,"brass",segments=17)
    m.box((x+.24,1.478,z+.084),(.104,.031,.012),"glass_amber")
    for dx in (-.22,-.07,.087,.230):
        m.revolve((x+dx,1.608,z-.17),[(0,.043),(.058,.055),(.065,.054)],"porcelain",12)
    m.rope([(x+.40,1.39,z-.043),(x+.42,1.37,z+.17),(x+.39,1.28,z+.218)],.015,"chrome",8)


def dining_table(m,x,z,w=.91,cloth=False):
    table(m,x,z,w,.73,.741,"oak",soft=True)
    if cloth:
        m.box((x,.790,z),(.60,.015,.554),"lace")
        for zv in (-1,1):
            verts=[(x-.30,.790,z+zv*.274),(x+.30,.790,z+zv*.274),
                   (x+.278,.639,z+zv*.373),(x-.282,.661,z+zv*.369)]
            m.quad(verts if zv==1 else verts[::-1],"lace")
            m.quad(verts[::-1] if zv==1 else verts,"lace")
    cup(m,x-.18,.803,z-.17,"porcelain")
    cup(m,x+.21,.803,z+.17,"ceramic_blue" if cloth else "porcelain")
    m.revolve((x+.01,.801,z-.05),[(0,.033),(.016,.033),(.107,.022),(.115,.035)],"glass_amber",12)
    m.tube((x+.01,.91,z-.05),(x-.027,1.065,z-.056),.007,"leaf_dark",6)
    m.blob((x-.027,1.065,z-.056),(.041,.025,.035),"flower",segments=8,rings=4)


def cafe(m):
    # The centre aisle stays open between the door and Mara's table.
    m.box((0,-.003,0),(9.42,.021,8.04),"floor_tile")
    counter_z=-3.38
    cabinet(m,.27,counter_z,6.15,.83,.95,"garnet","walnut")
    m.box((.27,.249,counter_z+.519),(5.98,.061,.047),"brass")
    for i in range(10):
        m.box((-2.69+i*.655,.52,counter_z+.454),(.038,.68,.038),"brass")
    espresso(m,1.60,counter_z+.02)
    kettle(m,2.44,.996,counter_z,"porcelain")
    m.box((-1.39,1.237,counter_z+.09),(1.14,.49,.522),"walnut")
    m.box((-1.39,1.274,counter_z+.359),(1.04,.30,.034),"glass_amber")
    m.box((-1.39,1.464,counter_z+.06),(1.12,.046,.52),"chrome")
    for px in (-1.70,-1.36,-1.08):
        dish(m,px,1.487,counter_z+.081,.114)
        m.revolve((px,1.508,counter_z+.08),[(0,.088),(.089,.077),(.100,.071)],"pie",13)
        m.blob((px,1.589,counter_z+.077),(.058,.027,.059),"peel",segments=9,rings=4)
    picture(m,"cafe_menu",-.72,2.19,-3.95,1.32,.62)
    picture(m,"breakfast",1.35,2.24,-3.95,.71,.44)
    for i in range(5):
        bottle(m,-.61+i*.16,.991,counter_z-.12,"glass_amber" if i%2 else "glass_green",.15+.035*(i%3))
    stool(m,-2.07,-2.34,.55)
    stool(m,1.58,-2.39,.55)
    stool(m,2.69,-2.38,.55)
    for s in (-1,1):
        sofa(m,s*3.72,.28,2.20,-s*PI/2)
        for z in (1.66,-.73):
            dining_table(m,s*2.41,z,1.12,True)
            chair(m,s*1.53,z,PI/2 if s==-1 else -PI/2,"rouge_cloth",True)
        picture(m,"town_print",s*4.487,1.76,.619,.87,.47,-s*PI/2)
        plant(m,s*3.93,3.24,size=.93)
    lamp(m,-1.79,2.44,.93,power=1.66)
    lamp(m,1.76,2.45,.94,power=1.39)
    lamp(m,.12,2.46,-2.22,power=1.54)
    m.anchor("mara",(.26,.032,-.74))
    clock_dial(m,3.46,2.26,-3.91,.22,time=3.29)
    window_display(m,-2.94,3.42)
    window_display(m,2.94,3.42)


def study(m):
    for j in range(3):
        shelf(m,-3.05+j*2.95,-3.51,2.78,.66,2.36,True,21+7*j)
    shelf(m,-3.10,-.95,1.29,.58,2.26,True,47)
    shelf(m,3.10,-.95,1.29,.58,2.26,True,61)
    table(m,-2.28,.71,1.95,.96,.80,"walnut")
    tape_deck(m,-2.34,.851,.50,.73)
    m.box((-1.66,.858,.875),(.32,.025,.24),"oak",False,.20)
    m.sheet("chart",(-1.667,.877,.879),.279,.188,.20)
    desk_lamp(m,-2.97,.858,.54)
    m.anchor("bell",(-2.30,1.075,.77))
    chair(m,-2.41,1.57,PI,"canvas",True)
    table(m,2.35,.77,1.3,.95,.75,"oak")
    chair(m,2.13,1.49,PI,"canvas",True)
    desk_lamp(m,2.57,.801,.43)
    stacks(m,2.21,.84,.226,.799,5)
    picture(m,"old_headland",2.97,1.78,3.64,.58,.42,PI)
    picture(m,"town_print",-2.98,1.74,3.64,.68,.49,PI)
    rug(m,(0,.016,1.21),1.62,3.79)
    lamp(m,-1.67,2.44,1.04,power=1.49)
    lamp(m,1.60,2.46,-1.56,color="#d3e0cd",power=1.29)


def gear(m,x,y,z,r,teeth,key="brass"):
    m.revolve((x,y,z),[(0,r*.827),(.092,r*.845),(.141,r*.827)],key,teeth*2,(0,0,1))
    m.hoop((x,y,z+.157),r*.748,.024,"walnut")
    for i in range(teeth):
        a=i*TAU/teeth
        def p(radius,h):
            return (x+radius*math.sin(a),y+radius*math.cos(a),z+h)
        m.beam(p(r*.807,.070),p(r*.995,.070),TAU*r*.46/teeth,.147,key)
        if i%4==0:
            m.tube(p(r*.14,.16),p(r*.674,.16),r*.042,"aged_steel",7)
    m.revolve((x,y,z+.145),[(0,r*.153),(.164,r*.143),(.196,r*.11)],"aged_steel",16,(0,0,1))


def clockshop(m):
    m.box((0,.85,-3.36),(6.94,1.69,.62),"deep_steel",True)
    gear(m,-2.06,1.62,-2.92,.59,23)
    gear(m,-.92,1.46,-2.91,.545,22)
    gear(m,.24,1.70,-2.92,.63,23,"rust")
    gear(m,1.23,1.35,-2.91,.424,19)
    for x in (-3.61,3.49):
        m.tube((x,.12,-3.05),(x,2.70,-3.05),.106,"aged_steel",10)
        m.box((x,.71,-2.98),(.33,.132,.31),"brass")
    control_board(m,-2.55,.0,1.28)
    bench(m,2.83,1.49,1.6)
    picture(m,"clock_sign",-.2,2.47,-3.54,1.34,.40)
    lamp(m,-1.49,2.42,.55,power=1.44)
    lamp(m,1.69,2.47,-1.54,color="#bfcfbf",power=1.57)


def control_board(m,x,y,z):
    m.soft((x,y+.52,z),(.95,1.01,.65),"aged_steel",.039,solid=True)
    m.box((x,y+.89,z+.331),(.783,.17,.035),"deep_steel")
    for i in range(6):
        m.box((x-.30+i*.12,y+.91,z+.354),(.064,.027,.012),"signal" if i==1 else "volt")
    m.hoop((x,y+.64,z+.363),.107,.015,"brass")
    m.tube((x,y+.64,z+.383),(x+.051,y+.69,z+.380),.009,"chalk",6)


def repair_shop(m):
    cabinet(m,-2.70,-2.89,3.28,.75,.81,"blue_siding")
    m.box((-2.72,1.62,-3.12),(3.24,.98,.105),"cork")
    for i in range(9):
        x=-4.06+i*.329
        k=1.82+.07*math.sin(i*1.2)
        m.tube((x,k,-3.027),(x,k-.24-(i%3)*.051,-3.027),.022,"chrome",7)
        m.hoop((x,k,-3.001),.039+.007*(i%2),.009,"chrome",segments=13)
    table(m,2.18,-1.08,2.33,1.11,.823,"fir")
    m.soft((2.10,1.19,-1.05),(1.04,.57,.51),"deep_steel",.05)
    for i in range(9):
        m.box((2.11,1.21,-1.33+i*.06),(1.05,.434,.022),"aged_steel")
    m.tube((1.58,1.21,-1.05),(1.32,1.21,-1.05),.113,"chrome",12)
    m.hoop((2.70,1.20,-1.056),.17,.022,"rust","x")
    barrel(m,-3.69,0,.91,.28,.61,"aged_steel")
    crate(m,3.77,.0,2.17,.72,.60,.44,"oak",True)
    coil(m,3.65,.47,2.22,.24,.018,4)
    boots=-3.4
    boot_pair(m,boots,2.82)
    lamps = [(-1.90,2.46,1.1),(1.9,2.46,-.71)]
    for pos in lamps:
        lamp(m,*pos,power=1.42)


def awning(m,w,front,y,depth,color,shop):
    for x in (-w*.45,w*.45):
        m.rope([(x,y+.10,front),(x,y-.24,front+depth),(x,y-.36,front+depth+.036)],.028,"aged_steel",9)
        m.tube((x,y-.41,front),(x,y-.27,front+depth),.024,"brass",8)
    for i in range(19 if shop else 13):
        n=19 if shop else 13
        x0=(i/n-.5)*w
        x1=((i+1)/n-.5)*w
        mat=color if i%2==0 else "canvas"
        rows=[(front,y+.12),(front+depth*.28,y+.02),(front+depth*.62,y-.124),(front+depth,y-.222)]
        for (z0,y0),(z1,y1) in zip(rows,rows[1:]):
            p=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1)]
            m.quad(p[::-1],mat)
            m.quad(p,mat)
        c=(x0+x1)/2
        edge=[(x0,y-.227,front+depth),(x1,y-.227,front+depth),
              (x1-.01,y-.362,front+depth),(c,y-.396,front+depth+.022),(x0+.013,y-.365,front+depth)]
        m.add(edge,[(0,1,2,3,4),(4,3,2,1,0)],mat)
    m.tube((-w*.51,y-.227,front+depth),(w*.51,y-.227,front+depth),.030,"zinc",9)


def entrance_light(m,x,z):
    m.box((x,2.26,z),(.175,.247,.086),"deep_steel")
    m.rope([(x,2.26,z+.035),(x,2.36,z+.24),(x,2.31,z+.324),(x,2.17,z+.348)],.026,"aged_steel",9)
    m.revolve((x,2.11,z+.35),[(0,.128),(.056,.129),(.110,.068)],"zinc",14)
    m.revolve((x,1.993,z+.35),[(0,.059),(.039,.094),(.129,.094)],"glass_amber",12)
    m.light((x,2.005,z+.38),"#ffd09b",.85,4.60,False)


def window_shutters(m,windows,front,color):
    for center,width,low,top,style in windows:
        if style!="window":
            continue
        for side in (-1,1):
            sx=center+side*(width*.5+.24)
            ym=(top+low)/2
            m.box((sx,ym,front+.199),(.336,top-low+.023,.07),color,False,side*.136)
            for i in range(10):
                h=low+.075+i*(top-low-.08)/10
                m.box((sx,h,front+.242),(.278,.043,.032),color,False,side*.136)
            for z_side in (-1,1):
                m.box((sx-side*.15,ym+(top-low)*.30*z_side,front+.25),(.081,.037,.015),"aged_steel")


def housing(region):
    descriptors={
        "fisher":(9.1,8.1,3.04,2.36,"sea_green","plaster","roof_slate","fish_sign","board"),
        "miller":(8.76,8.69,2.98,2.09,"cream_siding","wallpaper","roof_russet","miller_sign","board"),
        "ward":(9.52,8.78,3.04,2.64,"ward_red","plaster","roof_slate","north_ward","board"),
        "post":(8.94,8.20,3.23,1.62,"brick","sage_plaster","zinc","post_sign","brick"),
        "cafe":(9.52,8.19,3.14,1.31,"garnet","sage_plaster","roof_russet","cafe_sign","board"),
        "library":(9.72,8.12,3.27,2.12,"blue_siding","plaster","roof_slate","library_sign","board"),
        "repair":(10.24,8.39,3.08,2.47,"olive_siding","plaster","zinc","repair_sign","batten"),
        "clock":(7.94,8.53,3.25,1.69,"brick_dark","plaster","roof_slate","clock_sign","brick"),
    }
    builders={"fisher":fisherman,"miller":miller,"ward":ward,"post":postal,"cafe":cafe,
              "library":study,"repair":repair_shop,"clock":clockshop}
    for key,values in descriptors.items():
        w,d,h,r,color,interior,tile,title,style=values
        south=key in ("post","cafe","library","repair")
        m=region.mesh(key.title(),DOORS[key],PI if south else 0)
        brick_foundation(m,w,d,"brick_dark" if key in ("clock","post") else "fieldstone")
        planks(m,w-.18,d-.16,key)
        window_type="shop" if south else "window"
        front=[(-w*.314,1.44 if not south else 2.26,.86 if not south else .59,2.28,window_type),
               (0,2.03 if key!="repair" else 2.38,0,2.21,"wide" if key=="repair" else "door"),
               (w*.314,1.42 if not south else 2.22,.87 if not south else .59,2.28,window_type)]
        if key=="clock":
            front=[(-2.44,1.34,1.11,2.28,"window"),(0,1.88,0,2.28,"door"),(2.43,1.26,1.11,2.28,"window")]
        back=[(-w*.31,1.18,.98,2.20,"window"),(w*.309,1.22,.92,2.16,"window")]
        if key=="ward":
            back.insert(1,(0,1.84,0,2.15,"door"))
        for rear in (False,True):
            wall(m,(0,0,-d/2 if rear else d/2),w,h,color,interior,back if rear else front,PI if rear else 0,style)
        for side in (-1,1):
            position=(side*w/2,0,0)
            openings=[(-d*.24,1.27,1.00,2.22,"window"),(d*.23,1.16,1.02,2.19,"window")]
            wall(m,position,d,h,color,interior,openings,side*PI/2,style)
            for zsign in (-1,1):
                z=zsign*(d/2+.016)
                m.box((side*(w/2+.035),h*.5,z),(.23,h+.026,.154),"ivory")
                m.box((side*(w/2+.112),.23,z),(.124,.35,.223),"fieldstone")
        if key=="post":
            post_roof(m,w,d,h)
        else:
            roof(m,w,d,h,r,tile,color,key!="clock",(w*.286,-d*.16) if key!="clock" else None)
        if key=="library":
            library_trim(m,w,d,h)
        if key=="ward":
            porch(m,w,d,h)
        elif key in ("post","cafe","library","repair"):
            feature="sea_green" if key=="cafe" else ("garnet" if key=="post" else "blue_siding")
            awning(m,w*.83,d/2+.14,2.64,.96,feature,True)
        else:
            window_shutters(m,front,d/2,"sea_green" if key=="miller" else "blue_siding")
            awning(m,2.63,d/2+.15,2.61,.76,color,False)
        title_height=3.38 if key=="post" else (2.88 if south or key=="ward" else 2.84)
        title_width=2.61 if key!="post" else 3.73
        m.sign(title,(0,title_height,d/2+.208),title_width,.46)
        for x in (-1.39,1.39):
            entrance_light(m,x,d/2+.154)
        paving(m,0,d/2+.45,2.32,1.17,.29)
        if key=="ward":
            paving(m,0,-d/2-.53,1.98,1.16,.27)
        for px in (-w*.42,w*.42):
            plant(m,px,d/2+1.14,size=.89 if key!="fisher" else .69,flower=key not in ("repair","clock","fisher"))
        if key=="clock":
            clock_tower(m,h,r,d,color)
        if key=="miller":
            dormer(m,1.79,h+r*.43,d*.06,"cream_siding")
        if key=="fisher":
            dormer(m,-2.00,h+r*.34,-d*.15,"sea_green")
        builders[key](m)


def paving(m,x,z,w,d,step=.36):
    cols=math.ceil(w/step)
    rows=math.ceil(d/step)
    for a in range(cols):
        for b in range(rows):
            xx=x+(a+.5-cols*.5)*w/cols
            zz=z+(b+.5-rows*.5)*d/rows
            material="cobble" if (a+2*b)%5 else "fieldstone"
            m.box((xx,.016+.010*math.sin(3*a+b),zz),(w/cols-.020,.043,d/rows-.02),material,False,.020*math.cos(b*2+a))


def porch(m,w,d,h):
    z=d/2+.95
    w2=w*.42
    for x in (-w2/2,w2/2):
        m.box((x,1.26,z),(.125,2.50,.131),"ivory")
        m.box((x,.112,z),(.193,.19,.195),"fieldstone")
        m.box((x,2.345,z),(.160,.113,.168),"ivory")
        m.beam((x,2.03,z),(x*.66,2.481,z),.09,.081,"ivory")
    m.box((0,2.51,z),(w2+.25,.164,.145),"ivory")
    for j in range(13):
        x=-w2*.52+j*w2*1.04/12
        m.beam((x,2.55,z+.12),(x,2.719,d/2-.019),.286,.071,"roof_slate")
    m.box((0,.019,z-.35),(w2+.30,.087,1.48),"parquet")
    for sign in (-1,1):
        for i in range(4):
            x=sign*(w2*.47-.122)
            zz=z-.10-.241*i
            m.box((x,.385,zz),(.061,.72,.071),"ivory")
        m.box((sign*w2*.47,.74,z-.48),(.095,.094,.955),"oak")


def dormer(m,x,y,z,color):
    sign=1 if x>0 else -1
    m.box((x,y+.45,z),(.81,.78,1.08),color)
    m.box((x+sign*.425,y+.44,z),(.088,.62,.68),"ivory")
    m.box((x+sign*.471,y+.44,z),(.025,.506,.56),"glass_green")
    m.box((x+sign*.488,y+.44,z),(.024,.497,.037),"ivory")
    m.box((x+sign*.488,y+.44,z),(.027,.042,.541),"ivory")
    for side in (-1,1):
        for j in range(8):
            xx=x-.476+j*.146
            m.beam((xx,y+.817,z+side*.67),(xx,y+1.12,z),.15,.062,"zinc")


def clock_tower(m,base,rise,d,paint):
    shaft=base+rise-.22
    for s in (-1,1):
        x=s*1.59
        m.box((x,shaft+.88,0),(.26,2.8,3.13),"brick_dark")
        m.box((0,shaft+.88,x),(3.45,2.80,.26),paint)
        m.box((0,shaft+2.42,x),(3.70,.245,.424),"ivory")
    m.box((0,shaft-.29,0),(3.75,.238,3.77),"fieldstone")
    m.box((0,shaft+2.52,0),(3.73,.21,3.72),"zinc")
    clock_dial(m,0,shaft+.83,1.747,.891,time=3.28)
    for x in (-1.33,1.33):
        m.box((x,shaft+.705,1.77),(.144,2.03,.098),"ivory")
    for j in range(5):
        m.box((0,shaft+1.98+j*.121,1.748),(1.14,.075,.073),"walnut")
    ring=[]
    for i in range(4):
        a=PI/4+i*PI/2
        ring.append((math.cos(a)*2.81,shaft+2.61,math.sin(a)*2.81))
    top=(0,shaft+4.63,0)
    for i in range(4):
        m.add([ring[i],ring[(i+1)%4],top],[(1,0,2)],"roof_slate")
        m.beam(ring[i],top,.069,.089,"zinc")
    m.tube((0,shaft+4.61,0),(0,shaft+5.05,0),.041,"brass",12,.36)


def railing(m,x,z,length,direction=1,paint="sea_green",solid=True):
    end=x+length if direction==1 else z+length
    leg_count=max(2,round(length/1.35)+1)
    for j in range(leg_count):
        at=j*length/(leg_count-1)
        xx=x+at if direction==1 else x
        zz=z if direction==1 else z+at
        m.box((xx,.48,zz),(.127,.96,.127),paint)
        m.box((xx,.953,zz),(.16,.093,.16),"oak")
    n=math.ceil(length/.163)
    for i in range(n):
        a=(i+.5)*length/n
        xx=x+a if direction==1 else x
        zz=z if direction==1 else z+a
        m.box((xx,.46,zz),(.059,.79+.09*math.sin(i),.061),paint)
    for y in (.283,.786):
        center=((x+end)/2,y,z) if direction==1 else (x,y,(z+end)/2)
        dims=(length,.076,.078) if direction==1 else (.078,.076,length)
        m.box(center,dims,paint)
    if solid:
        m.collision(((x+end)/2,.45,z) if direction==1 else (x,.45,(z+end)/2),
                    (length,.90,.115) if direction==1 else (.115,.90,length))


def planter(m,x,z,width=1.22,d=.69,key="sea_green",seed=33):
    rng=random.Random(seed)
    m.box((x,.235,z),(width,.47,d),key,True)
    m.box((x,.482,z),(width+.058,.078,d+.055),"oak")
    m.box((x,.53,z),(width-.076,.021,d-.075),"moss")
    for i in range(max(3,round(width/.31))):
        q=(i/(max(3,round(width/.31))-1)-.5)*(width-.24)
        leaves(m,x+q,.535,z+rng.uniform(-.10,.10),rng.uniform(.53,.92),rng,True)


def mail_pillar(m,x,z):
    m.revolve((x,0,z),[(0,.19),(.11,.19),(.16,.155),(1.17,.153),(1.24,.200),(1.35,.19),(1.398,.058)],"garnet",25)
    m.revolve((x,.042,z),[(0,.205),(.06,.205)],"fieldstone",22)
    m.revolve((x,1.270,z),[(0,.204),(.036,.204)],"brass",25)
    m.box((x,1.098,z+.146),(.28,.072,.057),"black")
    m.box((x,.654,z+.147),(.22,.49,.027),"garnet")
    m.box((x,.762,z+.17),(.125,.084,.012),"ivory")
    m.collision((x,.69,z),(.36,1.375,.33))


def bicycle(m,x,z,yaw=.0,paint="sea_green"):
    def tr(v):
        a,b,c=rotate_y(v,yaw)
        return (a+x,b,c+z)
    for u in (-.53,.54):
        p=tr((u,.356,0))
        ax="z" if abs(math.cos(yaw))>.8 else "x"
        m.hoop(p,.338,.026,"tire",ax,30)
        m.hoop(p,.306,.009,"chrome",ax,30)
        for j in range(16):
            a=j*TAU/16
            q=(u+.300*math.sin(a),.356+.300*math.cos(a),0)
            m.tube(p,tr(q),.0058,"chrome",5)
        m.tube(tr((u,.356,-.067)),tr((u,.356,.072)),.027,"aged_steel",10)
    for a,b in (((-.53,.36,0),(-.239,.78,0)),((-.239,.78,0),(.23,.775,0)),
                ((.23,.775,0),(.014,.325,0)),((.014,.325,0),(-.239,.78,0)),
                ((.014,.325,0),(-.53,.36,0)),((.23,.775,0),(.54,.356,0))):
        m.tube(tr(a),tr(b),.023,paint,9)
    m.hoop(tr((.014,.325,-.023)),.084,.011,"chrome",segments=17)
    m.tube(tr((-.239,.78,0)),tr((-.24,.897,0)),.023,"chrome",8)
    m.soft(tr((-.247,.924,0)),(.241,.051,.091),"teal_leather",.018,yaw)
    m.tube(tr((.23,.775,0)),tr((.188,.970,0)),.021,"chrome",8)
    m.rope([tr((.112,.970,-.199)),tr((.188,.972,-.152)),tr((.188,.973,0)),
            tr((.188,.971,.146)),tr((.112,.970,.204))],.016,"chrome",8)
    for side in (-1,1):
        m.tube(tr((.115,.971,side*.186)),tr((.077,.971,side*.229)),.027,"tire",9)
    m.collision((x,.48,z),(1.31,.95,.25),yaw)


def pole(m,x,z,height=6.6):
    m.revolve((x,-.04,z),[(0,.145),(.44,.118),(height,.070)],"fir",13)
    m.box((x,height-.45,z),(1.41,.17,.15),"walnut")
    for u in (-.61,.0,.61):
        m.revolve((x+u,height-.37,z),[(0,.050),(.045,.065),(.089,.048),(.133,.055),(.151,.029)],"porcelain",12)
    m.box((x,.70,z+.105),(.137,.236,.073),"aged_steel")


def cable_runs(m,x0,step,n,z,y=6.38):
    for i in range(n):
        x1=x0+i*step
        pole(m,x1,z,y+.23)
        if i==n-1:
            return
        for dx in (-.61,.0,.61):
            curve=[]
            for j in range(15):
                t=j/14
                curve.append((x1+step*t+dx,y+.22-2.31*t*(1-t)+.039*math.sin(2*PI*t),z))
            m.rope(curve,.018,"black",7)


def streetlight(m,x,z,yaw):
    m.revolve((x,.0,z),[(0,.187),(.102,.187),(.189,.136),(.41,.103),(.48,.071),(3.30,.060)],"deep_steel",14)
    sx,_,sz=rotate_y((.72,0,0),yaw)
    m.rope([(x,3.30,z),(x+sx*.16,3.655,z+sz*.16),(x+sx*.46,3.716,z+sz*.46),
            (x+sx*.83,3.64,z+sz*.83),(x+sx,3.537,z+sz)],.043,"aged_steel",9)
    lx,lz=x+sx,z+sz
    m.revolve((lx,3.302,lz),[(0,.123),(.121,.158),(.17,.141),(.23,.069),(.265,.035)],"zinc",15)
    m.revolve((lx,3.247,lz),[(0,.066),(.087,.134),(.152,.134)],"glass_amber",15)
    m.light((lx,3.202,lz),"#ffd298",1.48,8.7,False)
    m.collision((x,1.55,z),(.21,3.1,.21))


def drain(m,x,z,wide=.50,depth=.36):
    m.box((x,.032,z),(wide,.019,depth),"aged_steel")
    m.box((x,.043,z),(wide-.055,.01,depth-.049),"black")
    for i in range(8):
        m.box((x+(i-3.5)*(wide-.062)/8,.050,z),(.018,.013,depth-.055),"aged_steel")
    for s in (-1,1):
        m.box((x,.053,z+s*depth*.36),(wide-.049,.012,.027),"deep_steel")


def pier(m,x,z,width,length):
    for i in range(math.ceil(length/.212)):
        zz=z-i*.213
        m.box((x,.02+.006*math.sin(i),zz),(width,.104,.204),"driftwood")
        for dx in (-width*.36,width*.36):
            m.blob((x+dx,.077,zz),(.012,.004,.010),"rust",segments=6,rings=3)
    m.collision((x,-.047,z-length*.5+.15),(width,.094,length+.40))
    for side in (-1,1):
        xx=x+side*(width*.48)
        m.box((xx,-.21,z-length*.5),(.221,.336,length),"walnut")
        for j in range(1,5):
            zz=z-j*length/5
            m.box((xx,-.67,zz),(.23,1.75,.24),"driftwood")
            m.box((xx,.118,zz),(.27,.066,.274),"zinc")
    for dx in (-width*.31,width*.31):
        at=(x+dx,.067,z-length+.62)
        m.revolve(at,[(0,.118),(.095,.10),(.32,.092),(.393,.14),(.414,.12)],"wet_iron",13)
        m.collision((at[0],.25,at[2]),(.21,.42,.21))


def shoreline(m):
    # Granite seawall, two landing stages, a winch, fish trays and safety gear.
    for left,right in [(-40.05,-22.49),(-18.10,15.37),(18.54,40.05)]:
        railing(m,left,-23.62,right-left,1,"fir")
    m.box((0,-.52,-23.77),(78,1.08,1.04),"fieldstone")
    for i in range(106):
        x=-38.3+i*.725
        if abs(x+20.30)>2.19 and abs(x-16.95)>1.58:
            m.box((x,.116,-23.78),(.70,.174,.76),"fieldstone",False,.035*math.sin(i*1.8))
        m.box((x,-.21,-24.36),(.63,.37,.27),"wet_stone",False,.042*math.cos(i*1.7))
    for x,length,width in [(-20.3,7.47,4.38),(16.95,5.50,3.16)]:
        pier(m,x,-23.07,width,length)
        for side in (-1,1):
            railing(m,x+side*width*.49,-length-23.05,length-.46,2,"fir")
        railing(m,x-width*.5,-length-23.05,width,1,"fir")
        coil(m,x-.62,.093,-length-21.95,.31,.025)
        for j in range(3):
            crate(m,x+.84,.073,-24.39-j*.61,.61,.43,.28,"driftwood",True)
    for x in range(-35,38,4):
        m.revolve((x,.03,-22.54),[(0,.112),(.07,.105),(.377,.069),(.420,.121),(.451,.086)],"wet_iron",13)
        m.collision((x,.256,-22.54),(.213,.453,.213))
    x,z=-16.8,-21.96
    m.box((x,.184,z),(.78,.35,.91),"fieldstone",True)
    m.tube((x-.411,.532,z),(x+.411,.532,z),.116,"deep_steel",14)
    for a in (-.31,.31):
        m.tube((x+a,.532,z),(x+a+.035,.532,z),.242,"rust",16)
        m.hoop((x+a,.532,z),.218,.036,"aged_steel","x")
    for i in range(9):
        m.hoop((x-.224+i*.055,.532,z),.138,.026,"rope","x")
    m.tube((x+.399,.535,z),(x+.63,.542,z),.041,"chrome",11)
    for side in (-1,1):
        barrel(m,29.79+side*.39,0,-20.9,.269,.68,"walnut")
    m.sign("pager",(35.32,1.10,-22.07),.74,.44,PI)
    m.box((35.32,.49,-22.07),(.10,.98,.10),"fir")


def public_realm(region):
    m=region.mesh("Straße, Gehwege und Gärten")
    m.box((0,-.23,0),(81,.46,48),"sand",True)
    m.box((0,.009,0),(81,.018,8.4),"asphalt")
    for s in (-1,1):
        railing(m,s*40,-23.6,47.4,2,"olive_siding")
    railing(m,-40,23.8,80,1,"olive_siding")
    for s in (-1,1):
        m.box((0,.023,s*5.32),(80.22,.046,2.36),"cobble")
        for i in range(117):
            x=-39.7+i*.68
            m.box((x,.056,s*4.28),(.658,.112,.225),"fieldstone",False,.024*math.sin(i))
        for x in (-34.3,-15.95,.34,15.63,34.58):
            drain(m,x,s*3.93)
        for x in (-33,-18,0,17,34):
            streetlight(m,x,s*5.82,0 if s==-1 else PI)
        for x in (-17.31,15.79,34.15):
            bench(m,x,s*5.75,1.73,"oak" if s<0 else "driftwood")
        for x in (-34.15,-18.52,-1.22,15.72,33.55):
            m.box((x,-.003,s*12.98),(3.6,.031,12.28),"moss")
            railing(m,x-1.56,s*7.21,2.85,1,"sea_green" if s<0 else "ivory")
            railing(m,x-1.65,(-15.55 if s<0 else 7.20),8.16,2,"olive_siding")
    for j in range(33):
        x=-39.17+j*2.40
        for k in range(7):
            px=x+.091*k+.18
            m.box((px,.021,.029),(.079,.003,.07),"chalk",False,.064*math.cos(k*j))
    for x,z,yaw in [(-15.55,5.44,.05),(2.96,-5.77,.0),(15.8,6.12,-.06)]:
        bicycle(m,x,z,yaw,"garnet" if x>0 else "sea_green")
    for j,x in enumerate([-29.42,-20.02,-12.53,-4.27,3.03,12.03,28.97]):
        planter(m,x,-6.57,1.25,.56,"sea_green" if j%2 else "olive_siding",36+j)
    for j,x in enumerate([-28.81,-20.82,-13.23,-4.92,3.06,12.6,21.10]):
        planter(m,x,6.19,1.15,.50,"garnet" if j%2 else "sea_green",70+j)
    mail_pillar(m,-27.47,5.38)
    cable_runs(m,-35.8,16.85,5,6.23)
    for i in range(5):
        x=-27.81+i*.43
        crate(m,x,0,-18.56,.39,.38,.30,"fir",True)
        if i<4:
            fish(m,x-.12,.151,-18.55,1.0,-.14)
    for x,z in [(-29.89,-7.35),(-21.07,-9.07),(10.49,-17.85),(28.41,6.35),(29.57,6.62)]:
        barrel(m,x,0,z,.23,.58)
        coil(m,x+.21,.018,z-.21,.19,.017,3)
    crate(m,-22.24,.03,-6.16,.49,.59,.34,"walnut",True)
    crate(m,-21.78,.03,-6.37,.47,.435,.28,"oak",True)
    crate(m,28.37,.03,6.41,.589,.53,.35,"fir",True)
    for j in range(6):
        crate(m,-25.6+j*.42,.031,-18.67,.377,.53,.391,"oak",solid=False)
        if j%2: bottle(m,-25.6+j*.42,.08,-18.62,"glass_amber",.254)
    # A trolley, side entrance and the service alley's paving mats.
    for x in (-32.01,-16.68,15.57,34.47):
        paving(m,x,-12.82,1.23,11.03,.51)
    for x in (-33.17,-17.11,-.29,15.38,32.67):
        paving(m,x,12.73,1.34,10.91,.47)
    m.sign("post_hours",(-26.43,1.41,6.71),.49,.36,PI)
    m.box((-26.43,.61,6.71),(.085,1.25,.116),"walnut")
    shore_details(m)
    shoreline(m)
    landscape(region)


def tree(m,x,z,height,rnd):
    side=rnd.uniform(-.32,.32)
    m.tube((x,-.21,z),(x+side,height,z+.14),.184,"bark",11,.12)
    m.collision((x,1.31,z),(.32,2.62,.32))
    for i in range(9):
        t=.24+i*.079
        y=height*t
        a=TAU*(i*.38197%1)
        cx,cz=x+side*t,z+t*.14
        s=(1-t)*height*.30
        tips=(cx+s*math.cos(a),y+.12,cz+s*math.sin(a))
        m.tube((cx,y,cz),tips,.048,"fir",7,.27)
        for j in range(3):
            v=j*.30+.29
            m.blob((cx+(tips[0]-cx)*v,y+height*.035,cz+(tips[2]-cz)*v),
                (s*.5*(1-v)+.39,height*.091,s*.53*(1-v)+.37),
                ("leaf_dark","leaf","moss_green")[(i+j)%3],rnd,10,5,.12)
    m.blob((x+side,height*.91,z+.12),(.48,height*.195,.54),"leaf_dark",rnd,11,6,.13)


def grass(m, x,y,z,rnd, size=.5):
    for j in range(7):
        h=rnd.uniform(.23,.53)*size
        a=rnd.uniform(0,TAU)
        ax,az=math.cos(a),math.sin(a)
        x0=x+rnd.uniform(-.13,.13)*size
        z0=z+rnd.uniform(-.13,.13)*size
        width=rnd.uniform(.013,.031)*size
        verts=[(x0-az*width,y,z0+ax*width),(x0+az*width,y,z0-ax*width),
               (x0+ax*h*.61,y+h,z0+az*h*.61)]
        m.add(verts,[(0,1,2),(2,1,0)],("leaf","leaf_light","moss_green")[j%3])


def landscape(region):
    rng=random.Random(9847)
    cliff=region.mesh("Felsufer und Brandung")
    for i in range(23):
        x=-67+i*5.91
        z=-33.9+rng.uniform(-6.8,-.0)
        h=rng.uniform(.50,2.16)+max(0,abs(x)-30)*.15
        cliff.blob((x,-1.20,z),(6.74,1.3+h,4.58),"cliff",rng,13,7,.19)
        for j in range(3):
            cliff.blob((x+rng.uniform(-2.9,2.9),rng.uniform(-1.2,.1),z+1.9+j*1.6),
                      (rng.uniform(.88,2.61),rng.uniform(.38,1.22),rng.uniform(.83,2.11)),
                      "wet_stone" if j%2 else "fieldstone",rng,10,6,.18)
    for x in (-43,41):
        for j in range(5):
            cliff.blob((x+(.4 if x<0 else -.4)*j,1.23+j*.38,-2.7-j*4.12),
                (rng.uniform(3.69,5.90),rng.uniform(2.69,4.08),3.78),
                "cliff" if j%2 else "fieldstone",rng,12,6,.22)
    garden=region.mesh("Gärten, Küstenwald und Gräser")
    for i in range(22):
        tree(garden,-55+i*5.2,24.7+rng.uniform(-.9,8.6),rng.uniform(4.69,8.71),rng)
    for x in (-39.38,38.13):
        for i in range(3):
            tree(garden,x+rng.uniform(-1.30,1.30),-8.3+i*6.41,rng.uniform(4.3,7.1),rng)
    for i in range(-38,37,2):
        grass(garden,i,.019,-22.03+rng.uniform(-.16,.84),rng,rng.uniform(.51,1.7))
    for x in (-34.0,-17.5,-1.1,14.8,34.2):
        for side in (-1,1):
            for k in range(15):
                xx=x+rng.uniform(-1.5,1.5)
                zz=side*rng.uniform(7.65,20.67)
                grass(garden,xx,.025,zz,rng,rng.uniform(.56,1.78))
                if k<4:
                    garden.blob((xx,.172,zz),(.54,.32,.62),("leaf","leaf_dark","moss_green")[k%3],rng,9,5,.12)
    for i in range(31):
        grass(garden,-38+i*2.6,.003,22.6+rng.uniform(-.66,.58),rng)


def gauge_box(m,x,z,anchor):
    # All three connections share the foundry shell. Labels on the street identify each switch.
    m.box((x,.106,z),(1.23,.208,.77),"fieldstone",True)
    m.soft((x,.539,z),(.97,.92,.61),"aged_steel",.058,solid=True)
    m.box((x,.988,z),(.996,.114,.697),"sand_enamel")
    m.box((x,.715,z+.317),(.798,.33,.057),"deep_steel")
    m.box((x-.196,.772,z+.357),(.346,.192,.032),"glass_amber")
    for j in range(9):
        xx=x-.335+j*.032
        m.box((xx,.776,z+.377),(.009,.072 if j%3==0 else .045,.008),"amber")
    m.beam((x-.197,.735,z+.391),(x-.297,.811,z+.394),.015,.012,"ivory")
    for i in range(4):
        for j in range(4):
            m.box((x+.087+i*.079,.735+j*.044,z+.358),(.057,.026,.011),"coal")
    for j in (-1,1):
        m.revolve((x+j*.35,.548,z+.323),[(0,.046),(.033,.041)],"brass",12,(0,0,1))
    m.hoop((x,.54,z+.328),.091,.015,"chrome")
    m.rope([(x-.443,.56,z-.086),(x-.65,.51,z-.091),(x-.73,.20,z-.111),(x-.75,.043,z-.44)],
           .037,"wet_iron",9)
    m.anchor(anchor,(x,.76,z+.41))


def overturned(m,x,z,yaw):
    group=m.region.mesh("Umgestürzte Kiste",(x,.030,z),yaw)
    # Slats lie against the ground and stay out of the road's escape line.
    for i in range(5):
        group.box((-.53+.19*i,.046,.053),(.164,.075,.74),"driftwood",False,.028*math.sin(i))
    group.beam((-.53,.034,.41),(.43,.255,.44),.12,.066,"fir")
    group.beam((-.51,.079,-.31),(.512,.038,-.32),.096,.066,"fir")
    coil(group,.16,.097,.09,.183,.015,4,"net")


def emergency(m,x,z,flare):
    m.revolve((x,.005,z),[(0,.123),(.043,.119),(.15,.082),(.164,.068)],"wet_iron",14)
    m.revolve((x,.167,z),[(0,.066),(.080,.055),(.111,.046)],"amber",14)
    m.hoop((x,.269,z),.061,.009,"chrome","y")
    m.box((x,.313,z),(.112,.029,.085),"aged_steel")
    if flare:
        m.light((x,.29,z),"#edab62",.91,3.5,False)


def storm():
    region=Set("sturm")
    m=region.mesh("Nasse Geröllspuren und Relais")
    gauge_box(region.mesh("Relais der Küstenpost",(-25,0,5.10),PI),0,0,"post")
    gauge_box(m,8.92,-5.76,"ward")
    gauge_box(m,25,-5.75,"clock")
    gauge_box(m,25,-18.38,"tower")
    for i,(x,z) in enumerate([(18.53,-6.46),(14.08,-6.56),(7.74,-6.01),
                            (7.89,-15.77),(8.37,-18.66),(13.98,-18.67),(19.79,-18.72),(24.45,-18.66)]):
        emergency(m,x,z,True)
        if i in (0,3,7):
            m.light((x-.15,.81,z+.52),"#d7a16f",.52,3.08,False)
    for i,(x,z) in enumerate([(11.5,-4.9),(20.47,-4.88),(25.25,3.92),(-21.79,4.29),
                            (-29.2,-4.96),(11.13,-19.75),(34.08,-5.21)]):
        overturned(m,x,z,1.83*math.sin(i*1.2))
        m.blob((x+.70,.017,z+.09),(.93,.035,1.73),"wet_stone",segments=11,rings=4,jitter=.29)
    for side in (-1,1):
        x=17.0
        z=side*4.69
        m.box((x,.307,z),(.59,.59,.61),"fieldstone",True)
        m.revolve((x,.58,z),[(0,.181),(.093,.184),(.119,.109),(.95,.093),(1.07,.11)],"wet_iron",16)
        m.revolve((x,1.66,z),[(0,.085),(.145,.085)],"signal",13)
        m.light((x-.2,1.75,z),"#ec7257",1.0,4.5,False)
    gate=region.mesh("HighWaterGate",(17,1.225,0))
    gate.box((0,-.121,0),(.155,1.72,8.66),"deep_steel")
    for i in range(18):
        z=-4.10+i*.48
        gate.box((-.108,-.071,z),(.124,1.64,.062),"wet_iron")
        gate.beam((-.132,.88,z-.23),(-.132,.72,z+.067),.139,.042,"hazard")
        if i%3==0:
            gate.box((-.159,.39,z),(.042,.164,.27),"glass_amber")
    for y in (-.83,.916):
        gate.box((0,y,0),(.306,.193,8.93),"aged_steel")
    gate.sign("pager",(-.219,.308,0),1.08,.55,-PI/2)
    return region


def build():
    shore=Set("ufer")
    housing(shore)
    public_realm(shore)
    return shore,storm()


def post_roof(m,w,d,h):
    # A low masonry parapet, four courses of trim and a central stepped crest.
    m.box((0,h+.075,0),(w+.28,.20,d+.28),"zinc")
    for side in (-1,1):
        z=side*(d*.5+.131)
        m.box((0,h+.308,z),(w+.25,.56,.31),"brick")
        m.box((0,h+.64,z),(w+.36,.103,.37),"fieldstone")
        for j in range(23):
            x=(j-11)*w/24
            m.box((x,h+.512,z+side*.174),(.075,.098,.063),"ivory")
        m.box((0,h+.893,z),(3.20,.46,.322),"brick")
        m.box((0,h+1.142,z),(3.47,.091,.40),"fieldstone")
        m.box((0,h+1.22,z),(2.26,.112,.366),"fieldstone")
    for side in (-1,1):
        m.box((side*w*.506,h+.305,0),(.26,.55,d+.34),"brick")
        m.box((side*w*.506,h+.613,0),(.34,.095,d+.39),"fieldstone")


def library_trim(m,w,d,h):
    z=d*.5+.165
    for x in (-w*.455,-w*.124,w*.124,w*.455):
        m.box((x,h*.52,z),(.178,h*.91,.17),"ivory")
        m.box((x,.25,z+.02),(.282,.42,.214),"fieldstone")
        m.box((x,h-.36,z+.023),(.30,.128,.25),"walnut")
        for j in (-1,0,1):
            m.box((x+j*.046,1.62,z+.09),(.015,2.18,.025),"oak")
    m.box((0,h-.085,z),(w,.101,.13),"ivory")


def radiator(m,x,z,yaw=0):
    def loc(u,y,v):
        xx,yy,zz=rotate_y((u,y,v),yaw)
        return (x+xx,yy,z+zz)
    for i in range(10):
        u=(i-4.5)*.106
        m.soft(loc(u,.391,0),(.081,.511,.153),"sand_enamel",.035,yaw)
        m.box(loc(u,.37,.072),(.041,.374,.025),"aged_steel",False,yaw)
    for side in (-1,1):
        m.tube(loc(side*.464,.57,-.009),loc(side*.599,.57,-.009),.047,"aged_steel",9)
        m.tube(loc(side*.557,.543,-.009),loc(side*.557,.027,-.009),.033,"copper",8)
        m.hoop(loc(side*.54,.61,-.01),.048,.011,"brass","y",13)
    m.collision((x,.39,z),(1.04,.54,.20),yaw)


def wall_panels(m,x,z,w):
    for j in range(9):
        zz=z-w*.5+(j+.5)*w/9
        m.box((x,.375,zz),(.034,.59,w/9-.009),"sage_plaster")
        m.box((x+.026,.383,zz),(.026,.461,w/9-.042),"sea_green")
    m.box((x+.024,.691,z),(.067,.082,w+.032),"walnut")


def fisherman_tools(m,x,z):
    panel_y=1.82
    m.box((x,panel_y,z),(.92,.67,.061),"cork")
    for i in range(4):
        dx=(i-1.5)*.193
        m.tube((x+dx,panel_y+.117,z+.043),(x+dx,panel_y-.179,z+.043),.020,"chrome",7)
        m.soft((x+dx,panel_y-.15,z+.089),(.044,.12,.044),"walnut",.018)
    m.hoop((x-.27,panel_y+.134,z+.045),.061,.012,"aged_steel",segments=16)
    m.hoop((x+.24,panel_y+.134,z+.045),.059,.009,"chrome",segments=16)


def window_display(m,x,z):
    m.box((x,.545,z),(1.94,.11,.34),"walnut")
    for i in range(2):
        pos_x=x-.47+.84*i
        dish(m,pos_x,.612,z,.161)
        bread(m,pos_x,.653,z,False)
        bottle(m,pos_x+.28,.617,z-.11,"glass_amber",.21)
    m.sign("breakfast",(x,.75,z+.108),.34,.17)


def shore_details(m):
    # Sidewalk service: two café tables, a chalkboard, parcels and garden implements.
    for i,x in enumerate((-12.48,-5.41)):
        z=6.22
        table(m,x,z,.66,.57,.692,"oak",.10*(-1)**i,True)
        cup(m,x-.14,.75,z-.042,"porcelain")
        chair(m,x-.66 if i==0 else x+.66,z,.12 if i==0 else PI*.72,"canvas",True)
        bottle(m,x+.121,.751,z+.138,"glass_amber",.14)
    m.sign("cafe_menu",(-6.94,.76,5.56),.53,.51,PI*.81)
    m.beam((-6.97,.493,5.57),(-7.00,.056,5.46),.07,.065,"walnut")
    m.beam((-6.89,.492,5.61),(-6.66,.056,5.92),.07,.065,"walnut")
    for px in (-30.15,3.35):
        plant(m,px,-7.51,size=.83)
    # A path of repaired cobbles and old patches in the salt-damaged road.
    rnd=random.Random(1418)
    for x,z in [(-30.25,2.48),(-26.0,-1.14),(-18.23,3.42),(-9.93,-3.12),
                (-2.01,2.54),(7.94,-1.37),(17.46,2.72),(28.15,-2.74),(33.24,1.93)]:
        pts=[(x+math.cos(TAU*i/11)*rnd.uniform(.49,1.29),.019,z+math.sin(TAU*i/11)*rnd.uniform(.22,.62))
             for i in range(11)]
        m.add(pts,[tuple(reversed(range(11)))],"dust")
        path=[]
        for k in range(9):
            path.append((x-.78+k*.183,.024,z-.13+.118*math.sin(k*1.64)))
        m.rope(path,.008,"tar",5)
    for x,z in [(-31.3,-19.8),(-15.00,-19.1),(3.84,-21.05),(18.2,-21.4),(31.00,-19.9)]:
        paving(m,x,z,2.16,1.07,.41)
    hooks(m,-34.08,-20.6,"blanket")
    for i in range(2):
        net_panel(m,-23.25-i*1.67,1.65,-19.20,1.54,1.19,.17,9,11)
        for side in (-1,1):
            x=-23.25-i*1.67+side*.71
            m.box((x,.89,-19.20),(.102,1.78,.099),"driftwood")
