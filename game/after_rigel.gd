extends Node3D

signal returned

const TITLES := ["IV · Beneath the Tide", "V · Platform 6", "VI · The Other Shore", "VII · The Last Tide"]
const AMBER := Color("#d7b185")
const TEAL := Color("#99c5b9")
const SLATE := Color("#44585c")
const WOOD := Color("#695048")
const STEEL := Color("#38565a")
const SAVE := "user://last_tide_restored.cfg"

var base
var area: Node3D
var body: CharacterBody3D
var camera: Camera3D
var torch: SpotLight3D
var light: DirectionalLight3D
var world_env: Environment
var layer: CanvasLayer
var hud: Label
var prompt: Label
var subtitle: Label
var panel: PanelContainer
var crosshair: Label
var audio: AudioStreamPlayer3D
var phase_label: Label3D
var chapter := 0
var task := 0
var badges := {}
var finds := {}
var digits := [0,0,0]
var scene_data := {}
var actions := {}
var aim := ""
var clock := 0.0
var subtitle_left := 0.0
var past := false
var finish_title := ""
var wet := false
var surge := -1.0
var played := false
var film: Camera3D
var story_index := 0
var escaped_ward := false

func _ready() -> void:
	make_player()
	make_hud()
	var slot := ConfigFile.new()
	if slot.load(SAVE)==OK:
		chapter=clampi(int(slot.get_value("campaign","chapter",0)),0,3)
		task=int(slot.get_value("campaign","task",0))
		finds=slot.get_value("campaign","finds",{})
	build(chapter)

func make_player() -> void:
	body=CharacterBody3D.new()
	add_child(body)
	body.collision_layer=2
	body.floor_snap_length=.25
	var hit:=CollisionShape3D.new()
	var capsule:=CapsuleShape3D.new()
	capsule.radius=.26
	capsule.height=1.72
	hit.shape=capsule
	hit.position.y=.86
	body.add_child(hit)
	camera=Camera3D.new()
	body.add_child(camera)
	camera.position.y=1.57
	camera.fov=74
	camera.far=95
	camera.make_current()
	torch=SpotLight3D.new()
	camera.add_child(torch)
	torch.light_color=Color("#e5e0c3")
	torch.light_energy=1.72
	torch.spot_range=15
	torch.spot_angle=35
	audio=AudioStreamPlayer3D.new()
	add_child(audio)

func make_hud() -> void:
	layer=CanvasLayer.new()
	layer.layer=22
	add_child(layer)
	hud=Label.new()
	layer.add_child(hud)
	hud.position=Vector2(34,24)
	hud.add_theme_font_size_override("font_size",18)
	hud.modulate=TEAL
	prompt=Label.new()
	layer.add_child(prompt)
	prompt.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	prompt.offset_left=-280
	prompt.offset_right=280
	prompt.offset_top=37
	prompt.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	prompt.modulate=AMBER
	crosshair=Label.new()
	layer.add_child(crosshair)
	crosshair.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	crosshair.offset_top=-13
	crosshair.offset_left=-4
	crosshair.text="·"
	subtitle=Label.new()
	layer.add_child(subtitle)
	subtitle.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	subtitle.offset_left=100
	subtitle.offset_right=-100
	subtitle.offset_top=-102
	subtitle.offset_bottom=-23
	subtitle.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	subtitle.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	for label in [hud,prompt,subtitle]:
		label.add_theme_color_override("font_outline_color",Color("#111817"))
		label.add_theme_constant_override("outline_size",9)
	subtitle.add_theme_font_size_override("font_size",21)

func surface(color: Color, emission := 0.0, rough := .75) -> StandardMaterial3D:
	var paint:=StandardMaterial3D.new()
	paint.albedo_color=color
	paint.roughness=rough
	if emission>0:
		paint.emission_enabled=true
		paint.emission=color
		paint.emission_energy_multiplier=emission
	return paint

func shape(mesh: PrimitiveMesh, pos: Vector3, color: Color, glow := 0.0, root: Node3D = null) -> MeshInstance3D:
	var item:=MeshInstance3D.new()
	item.mesh=mesh
	item.material_override=surface(color,glow)
	(root if root else area).add_child(item)
	item.position=pos
	return item

func box(pos: Vector3, size: Vector3, color: Color, solid := false, root: Node3D = null, glow := 0.0) -> MeshInstance3D:
	var mesh:=BoxMesh.new()
	mesh.size=size
	var item:=shape(mesh,pos,color,glow,root)
	if solid:
		var wall:=StaticBody3D.new()
		item.add_child(wall)
		var hit:=CollisionShape3D.new()
		var volume:=BoxShape3D.new()
		volume.size=size
		hit.shape=volume
		wall.add_child(hit)
	return item

func pipe(a: Vector3, b: Vector3, radius: float, color: Color, glow := 0.0) -> MeshInstance3D:
	var mesh:=CylinderMesh.new()
	mesh.top_radius=radius
	mesh.bottom_radius=radius
	mesh.radial_segments=10
	mesh.height=a.distance_to(b)
	var item:=shape(mesh,(a+b)*.5,color,glow)
	var up:=(b-a).normalized()
	var right:=Vector3.FORWARD.cross(up).normalized() if absf(up.z)<.98 else Vector3.UP.cross(up).normalized()
	item.basis=Basis(right,up,right.cross(up))
	return item

func ring(at: Vector3, radius: float, width: float, color: Color, glow := 0.0) -> MeshInstance3D:
	var mesh:=TorusMesh.new()
	mesh.inner_radius=radius-width
	mesh.outer_radius=radius+width
	mesh.rings=32
	mesh.ring_segments=10
	var item:=shape(mesh,at,color,glow)
	item.rotation.x=PI/2
	return item

func plaque(caption: String, at: Vector3, point_size := 34, yaw := 0.0) -> Label3D:
	var text:=Label3D.new()
	area.add_child(text)
	text.position=at
	text.rotation.y=yaw
	text.text=caption
	text.font_size=point_size
	text.pixel_size=.005
	text.outline_size=6
	text.modulate=AMBER
	return text

func lamp(at: Vector3, tint: Color, energy := 1.4, reach := 7.5) -> void:
	box(at+Vector3(0,.2,0),Vector3(.45,.10,.20),tint,false,null,.9)
	var node:=OmniLight3D.new()
	area.add_child(node)
	node.position=at
	node.light_color=tint
	node.light_energy=energy
	node.omni_range=reach

func set_atmosphere(day := false, storm := false) -> void:
	var env:=Environment.new()
	var sky:=Sky.new()
	var paint:=ProceduralSkyMaterial.new()
	paint.sky_top_color=Color("#668b9d") if day else Color("#0b1923")
	paint.sky_horizon_color=Color("#c4bda4") if day else Color("#29414e")
	paint.ground_horizon_color=paint.sky_horizon_color
	sky.sky_material=paint
	env.sky=sky
	env.background_mode=Environment.BG_SKY
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color("#dfd8b9") if day else Color("#9cb7b7")
	env.ambient_light_energy=.62 if day else .31
	env.fog_enabled=true
	env.fog_density=.007 if day else (.027 if storm else .018)
	env.fog_light_color=paint.sky_horizon_color.darkened(.22)
	env.fog_sky_affect=.23
	world_env=env
	camera.environment=env
	light.light_energy=1.15 if day else .22
	light.light_color=Color("#ffdcaa") if day else Color("#8db9c8")

func old_mesh(id: String, pos: Vector3, yaw := 0.0, scale_factor := 1.0, solid := true) -> Node3D:
	return base.world.place(id,pos,yaw,solid,scale_factor,area)

func plate(id: String, pos: Vector3, caption: String, size := Vector3(.85,.62,.40)) -> void:
	var use:=Area3D.new()
	area.add_child(use)
	use.position=pos
	use.collision_layer=4
	use.collision_mask=0
	use.monitoring=false
	use.monitorable=false
	var hit:=CollisionShape3D.new()
	var volume:=BoxShape3D.new()
	volume.size=size
	hit.shape=volume
	use.add_child(hit)
	use.set_meta("action",id)
	actions[id]=caption

func control(id: String, pos: Vector3, title: String, hint: String) -> void:
	box(pos+Vector3(0,.45,0),Vector3(.98,.9,.64),STEEL,true)
	box(pos+Vector3(0,1.01,0),Vector3(1.06,.29,.74),SLATE)
	box(pos+Vector3(0,1.02,.38),Vector3(.62,.13,.025),TEAL,false,null,.65)
	for i in 3:
		box(pos+Vector3(-.28+i*.28,.90,.38),Vector3(.08,.06,.025),AMBER,false,null,.55)
	plaque(title,pos+Vector3(0,1.37,.18),24)
	plate(id,pos+Vector3(0,1.02,.48),hint)

func door(at: Vector3, width: float, height: float, depth: float, paint: Color, turn := false) -> void:
	# A walkable opening occupies the middle of the wall.
	var size:=Vector3((width-1.8)*.5,height,depth)
	for sign_value in [-1,1]:
		var side:=float(sign_value)*(width+1.8)*.25
		box(at+Vector3(0,height*.5,side) if turn else at+Vector3(side,height*.5,0),Vector3(depth,height,size.x) if turn else size,paint,true)
	box(at+Vector3(0,(height+2.13)*.5,0),Vector3(depth,height-2.13,1.8) if turn else Vector3(1.8,height-2.13,depth),paint,true)

func build(index: int) -> void:
	if is_instance_valid(area):
		remove_child(area)
		area.free()
	area=Node3D.new()
	add_child(area)
	light=DirectionalLight3D.new()
	area.add_child(light)
	light.rotation_degrees=Vector3(-40,-47,0)
	light.shadow_enabled=true
	light.directional_shadow_max_distance=42
	actions.clear()
	scene_data.clear()
	past=false
	wet=false
	surge=-1.0
	played=false
	story_index=0
	clock=0.0
	badges.clear()
	escaped_ward=false
	finish_title=""
	digits=[0,0,0]
	chapter=index
	body.position=Vector3(0,.10,10)
	body.rotation=Vector3.ZERO
	body.velocity=Vector3.ZERO
	camera.rotation=Vector3.ZERO
	camera.make_current()
	torch.show()
	match index:
		0: cave()
		1: station()
		2: shore(false)
		3:
			if task>=4: core()
			else: shore(true)
	hud_refresh()
	Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
	save()

func water(at: Vector3, size: Vector2, storm: bool) -> MeshInstance3D:
	var mesh:=PlaneMesh.new()
	mesh.size=size
	mesh.subdivide_width=30
	mesh.subdivide_depth=30
	var sheet:=shape(mesh,at,SLATE)
	var water_material:=ShaderMaterial.new()
	water_material.shader=preload("res://restored_water.gdshader")
	water_material.set_shader_parameter("movement",.7 if storm else .0)
	sheet.material_override=water_material
	return sheet

func figure(at: Vector3, drowned: bool, yaw: float) -> Node3D:
	var actor: Node3D=load("res://scripts/figure.gd").new()
	area.add_child(actor)
	actor.position=at
	actor.rotation.y=yaw
	actor.build(drowned,Color("#a66456"))
	actor.pose("idle",.74)
	return actor

func cave() -> void:
	set_atmosphere()
	box(Vector3(0,-.25,-17),Vector3(17,.50,59),Color("#343936"),true)
	for side in [-1,1]:
		box(Vector3(side*7.9,2.3,-17),Vector3(.6,5,60),SLATE,true)
		for i in 22:
			var z:=11-i*2.63
			var height:=1.17+.51*sin(i*2.37)
			var mesh:=SphereMesh.new()
			mesh.radial_segments=9
			mesh.rings=5
			var rock:=shape(mesh,Vector3(side*(7.7+height*.19),height,z),Color("#3e4640").darkened(.08+.06*cos(i)))
			rock.scale=Vector3(3.1,3.3+height,3.9)
			rock.rotation.z=sin(i)*.21
			if i%3==0:
				box(Vector3(side*6.1,1.92,z),Vector3(.25,3.84,.32),WOOD)
				pipe(Vector3(side*5.9,.75,z),Vector3(side*5.9,.75,z-7.89),.145,Color("#845741"))
			if i%2==0:
				rock=shape(mesh,Vector3(side*2.92,4.12+height*.28,z),Color("#393e38"))
				rock.scale=Vector3(5.8,2.60,4.43)
	box(Vector3(0,2.4,12),Vector3(17,4.8,.42),SLATE,true)
	box(Vector3(0,2.4,-46),Vector3(17,4.8,.42),SLATE,true)
	for z in [6,-2,-11,-20,-31,-41]:
		box(Vector3(0,3.70,z),Vector3(12.35,.25,.36),WOOD)
		lamp(Vector3(4.6,2.32,z),AMBER,1.8)
	for i in 62:
		box(Vector3(4.82,.085,-2.4-i*.66),Vector3(2.50,.17,.61),WOOD.lightened(.03*sin(i)))
		if i%5==0:
			box(Vector3(6.01,.65,-2.4-i*.66),Vector3(.13,1.3,.15),STEEL)
			box(Vector3(6.01,1.27,-3.72-i*.66),Vector3(.095,.09,3.3),STEEL,false,null,.13)
	box(Vector3(4.82,.076,-22.44),Vector3(2.50,.15,41.17),WOOD,true)
	scene_data.water=water(Vector3(0,-.08,-28),Vector2(6.7,31),true)
	scene_data.front=box(Vector3(0,1.13,3.87),Vector3(7.1,2.25,.23),STEEL,true)
	for x in [-5.85,5.85]:
		box(Vector3(x,2,3.87),Vector3(4.60,4,.35),SLATE,true)
	control("ebb",Vector3(2.45,0,7.5),"ROTER PEGEL","Auf Ebbe warten")
	plaque("GEZEITENTOR  /  P-2",Vector3(-2.47,2.55,4.15))
	for i in 2:
		var x:float=-4.63+i*2.02
		pipe(Vector3(x,.65,-11.99),Vector3(x,.65,-13.55),.46,STEEL)
		for j in 8:
			pipe(Vector3(x,.65,-12-j*.18),Vector3(x,.65,-12.06-j*.18),.52,Color("#716756"))
		ring(Vector3(x,1.25,-12),.23,.035,Color("#ab6750"))
	control("inlet",Vector3(-4.65,0,-10.78),"A / ZULAUF","Zulaufventil bedienen")
	control("bypass",Vector3(-2.64,0,-10.78),"B / UMLAUF","Umlaufventil bedienen")
	control("pump",Vector3(-.69,0,-10.78),"C / START","Pumpe P-2 starten")
	control("cave_spool",Vector3(4.25,0,-1.17),"PUMPENBUCH","Pumpenbuch und Spule ansehen")
	var first_part:=area.get_child_count()
	control("receiver",Vector3(-.25,0,-18),"FUNKUMSETZER","Auf Maras Stimme antworten")
	scene_data.receiver_group=area.get_children().slice(first_part)
	scene_data.shutter=box(Vector3(0,3.91,-22.4),Vector3(7.1,2.61,.28),STEEL,true)
	box(Vector3(-5.61,1.7,-22.4),Vector3(4,3.4,.32),SLATE,true)
	scene_data.double=figure(Vector3(-2.52,.03,-20.2),true,0)
	control("cave_end",Vector3(0,0,-43.7),"PLATFORM 6","Druckschleuse betreten")
	if task>=1: scene_data.front.position.y=3.88
	if task>=3:
		scene_data.shutter.position.y=1.29
		scene_data.water.position.y=.62
		remove_receiver()

func station() -> void:
	set_atmosphere()
	box(Vector3(0,-.21,-16),Vector3(19.2,.42,58),SLATE,true)
	box(Vector3(0,3.36,-16),Vector3(19.2,.24,58),Color("#273336"),true)
	for x in [-9.52,9.52]:
		box(Vector3(x,1.65,-16),Vector3(.35,3.3,58),STEEL,true)
		pipe(Vector3(x*.96,2.7,12),Vector3(x*.96,2.7,-44),.18,Color("#785946"))
	for z in [12.4,-44.7]:
		box(Vector3(0,1.65,z),Vector3(19.2,3.3,.35),STEEL,true)
	var sides:=[["SICHERHEIT","BIOLOGIE","GENERATOR","ARCHIV 08","BEOBACHTUNG"],["UNTERKUNFT","SIGNALFORSCHUNG","SERVER","WASSERKONTROLLE","LAGER"]]
	for i in 5:
		var z:=5.7-i*9.0
		for side in [-1,1]:
			door(Vector3(side*2.70,0,z),9.0,3.3,.25,STEEL,true)
			box(Vector3(side*6.08,1.55,z-4.5),Vector3(6.83,3.1,.23),STEEL,true)
			var caption:String=sides[0 if side==-1 else 1][i]
			plaque(caption,Vector3(side*2.54,2.52,z),27,-side*PI/2)
			lamp(Vector3(side*6.25,2.65,z),AMBER if i%2 else TEAL,2.2,7)
			for j in 3:
				var x:float=side*(5.03+j*1.39)
				box(Vector3(x,.46,z-2.85),Vector3(1.13,.92,.72),STEEL,true)
				box(Vector3(x,.99,z-3.11),Vector3(.69,.29,.21),TEAL,false,null,.52)
				for k in 3:
					box(Vector3(x-.31+k*.31,1.22,z-3.14),Vector3(.095,.25,.10),Color("#576e67").lightened(.1*k),false,null,.09*k)
				if i==2 and side==1:
					for k in 7:
						box(Vector3(x,.36+k*.235,z+2.84),Vector3(1.07,.21,.59),Color("#203331"),k==0)
						box(Vector3(x+.36,.36+k*.235,z+2.53),Vector3(.12,.038,.02),TEAL,false,null,1.3)
		lamp(Vector3(0,2.9,z),TEAL,2.35,8.0)
		box(Vector3(0,.01,z),Vector3(1.3,.015,.20),Color("#ad8051"))
	scene_data.rubble=box(Vector3(0,1.25,-8.02),Vector3(5.39,2.50,.75),Color("#3e4843"),true)
	var root:Node3D=scene_data.rubble
	for j in 11:
		var fragment:=box(Vector3(-2.38+j*.48,.09*cos(j),.46),Vector3(.76,1.49,.81),SLATE,false,root)
		fragment.rotation.z=.4*sin(j)
	control("coupler",Vector3(-5.57,0,5.77),"PHASENKOPPLER","Tragbaren Koppler aufnehmen")
	control("phase",Vector3(1.40,0,-4.6),"ZEITPHASE","Zwischen 1998 und 2026 wechseln")
	control("phase",Vector3(1.4,0,-28.65),"ZEITPHASE","Zwischen 1998 und 2026 wechseln")
	phase_label=plaque("2026",Vector3(0,2.72,-7.51),39)
	control("archive",Vector3(-5.67,0,-21.64),"DAS BAND VON 1998","Archivaufnahme ansehen")
	control("server_spool",Vector3(5.69,0,-12.64),"RÜCKLAUFKOPIE","Zweite Spur sichern")
	control("station_end",Vector3(0,0,-42.8),"CONTAINMENT","Eindämmungsschleuse öffnen")

func shore(storm: bool) -> void:
	set_atmosphere(not storm,storm)
	body.position=Vector3(-30,.1,.9)
	body.rotation.y=-PI/2
	box(Vector3(0,-.24,0),Vector3(81,.48,48),Color("#515a4e"),true)
	box(Vector3(0,.012,0),Vector3(81,.024,8.25),Color("#3a4444"))
	for side in [-1,1]:
		box(Vector3(0,.047,side*5.30),Vector3(81,.1,2.41),Color("#75807a"))
		box(Vector3(side*40,1.69,0),Vector3(.8,3.4,48),Color("#49564b"),true)
		box(Vector3(0,1.69,side*23.8),Vector3(80,3.4,.38),Color("#49564b"),true)
		for i in 6:
			old_mesh("street_lamp",Vector3(-33+i*13.2,.02,side*5.8),0,1.0,false)
	for i in 33:
		box(Vector3(-39+i*2.4,.031,0),Vector3(.86,.014,.085),Color("#a99777"))
		old_mesh("cliff_1",Vector3(-43+i*2.88,-.4,-27.4-.7*sin(i)),i*.38,1.1,false)
	for i in 19:
		old_mesh("fir_0",Vector3(-46+i*5,-.10,27+4*cos(i)),i*.40,1.2,false)
	water(Vector3(0,-.19,-43),Vector2(160,39),storm)
	old_mesh("trawler",Vector3(-21,-.12,-33),-.26,.74,false)
	old_mesh("lighthouse",Vector3(34,0,-39),0,1.0,false)
	for i in 3:
		var x:= -25.0+i*16
		home(Vector3(x,0,-11),0,i)
		home(Vector3(x,0,11),PI,i+3)
	var clockhouse:=Vector3(25,0,-11)
	home(clockhouse,0,6)
	pipe(clockhouse+Vector3(0,3,0),clockhouse+Vector3(0,7.8,0),1.29,SLATE)
	ring(clockhouse+Vector3(0,6.7,1.32),.74,.05,AMBER,.5)
	pipe(clockhouse+Vector3(0,6.7,1.38),clockhouse+Vector3(-.48,6.94,1.38),.034,AMBER)
	if storm:
		scene_data.street_water=water(Vector3(0,-.12,0),Vector2(79,8.3),true)
		control("post",Vector3(-25,0,5.1),"1 / KÜSTENPOST","Relais 1 schließen")
		control("ward",Vector3(7,0,-5.7),"2 / HAUS WARD","Relais 2 schließen")
		control("clock",Vector3(25,0,-5.75),"3 / UHRWERK","Relais 3 schließen")
		scene_data.roadblock=box(Vector3(17,-3,0),Vector3(.64,2.45,10.65),SLATE,true)
		scene_data.guard=figure(Vector3(16.4,.05,-1.3),true,-PI/2)
		scene_data.guard.hide()
		for p in [Vector3(7,.05,-15.6),Vector3(7,.05,-18.4),Vector3(14,.05,-18.4),Vector3(21,.05,-18.4)]:
			box(p,Vector3(.27,.08,.50),AMBER,false,null,1.35)
		if task==3:
			surge=0
			scene_data.roadblock.position.y=1.225
			scene_data.guard.show()
		control("tower",Vector3(25,0,-18.38),"BLACKCLIFF","In die Lichtkammer hinabsteigen")
	else:
		var mara:=figure(Vector3(-8.42,.04,11.65),false,PI)
		plate("mara",mara.position+Vector3(0,1,-.31),"Mit Mara sprechen",Vector3(.72,1.7,.56))
		for i in 3:
			scene_data["resident"+str(i)]=figure(Vector3(-26+i*16,.11,-4.2+i*2),false,PI/2)

func home(at: Vector3, yaw: float, kind: int) -> void:
	var house:=Node3D.new()
	area.add_child(house)
	house.position=at
	house.rotation.y=yaw
	var house_colors:=[Color("#4d7471"),Color("#a49678"),Color("#805448"),Color("#787960"),Color("#875d51"),Color("#4c6e71"),Color("#607277")]
	var title:String=["FISCHER & SÖHNE","HAUS MILLER","HAUS WARD","KÜSTENPOST","CAFÉ MORGENROT","LESESAAL","UHRWERK WEST"][kind]
	var color:Color=house_colors[kind]
	box(Vector3(0,-.01,0),Vector3(9.6,.10,8.0),WOOD,true,house)
	for s in [-1,1]:
		box(Vector3(s*4.7,1.48,0),Vector3(.22,2.96,8),color,true,house)
		box(Vector3(s*2.82,1.48,3.92),Vector3(3.78,2.96,.22),color,true,house)
		if kind==2:
			box(Vector3(s*2.82,1.48,-3.92),Vector3(3.78,2.96,.22),color,true,house)
		box(Vector3(s*2.81,1.67,4.06),Vector3(1.38,1.12,.10),Color("#a7a487"),false,house)
		box(Vector3(s*2.81,1.67,4.127),Vector3(1.19,.92,.045),Color("#394e50"),false,house,.12)
		box(Vector3(s*2.81,1.67,4.16),Vector3(.046,1.02,.05),Color("#ac9d7c"),false,house)
		box(Vector3(s*2.81,1.67,4.16),Vector3(1.25,.04,.05),Color("#ac9d7c"),false,house)
		var roof_panel:=box(Vector3(s*2.35,3.81,0),Vector3(5.03,.16,8.68),Color("#354a50"),false,house)
		roof_panel.rotation.z=-s*.34
		for j in 12:
			box(Vector3(s*2.81,.15+j*.232,4.03),Vector3(3.69,.032,.025),color.darkened(.22),false,house)
		for j in 9:
			var batten:=box(Vector3(s*2.34,3.92,-4.21+j*.98),Vector3(4.94,.07,.062),Color("#46585b"),false,house)
			batten.rotation.z=-s*.34
	box(Vector3(0,2.60,3.92),Vector3(1.95,.73,.22),color,true,house)
	if kind==2:
		box(Vector3(0,2.60,-3.92),Vector3(1.95,.73,.22),color,true,house)
	else:
		box(Vector3(0,1.48,-3.92),Vector3(9.45,2.96,.22),color,true,house)
	for z in [-3.92,3.92]:
		var gable:=PrismMesh.new()
		gable.size=Vector3(9.49,1.63,.18)
		shape(gable,Vector3(0,3.78,z),color.darkened(.15),0,house)
	box(Vector3(0,2.95,0),Vector3(9.39,.13,7.85),WOOD,false,house)
	box(Vector3(2.85,4.26,-1.65),Vector3(.52,1.43,.54),Color("#705a50"),false,house)
	box(Vector3(2.85,5.0,-1.65),Vector3(.64,.12,.68),SLATE,false,house)
	for x in [-2.30,2.44]:
		var table_z:=-1.47 if (kind==2 and x>0) else .73
		box(Vector3(x,.82,table_z),Vector3(1.56,.13,.94),WOOD,true,house)
		for dx in [-.64,.64]:
			for dz in [-.34,.34]:
				box(Vector3(x+dx,.39,table_z+dz),Vector3(.095,.78,.095),WOOD,false,house)
		box(Vector3(x+.56,.94,table_z-.21),Vector3(.22,.12,.25),SLATE,false,house)
	for x in [-3.53,3.53]:
		for j in 3:
			box(Vector3(x,.34+j*.56,-2.98),Vector3(1.59,.069,.52),WOOD,false,house)
			for t in 6:
				box(Vector3(x-.65+t*.21,.52+j*.56,-2.96),Vector3(.14,.25+.04*cos(t),.24),house_colors[(j+t+kind)%house_colors.size()],false,house)
	var anchor:=house.to_global(Vector3(0,2.57,4.09))-area.global_position
	plaque(title,anchor,30,yaw)
	lamp(house.to_global(Vector3(.06,2.55,-.42))-area.global_position,AMBER,.98,6.4)
	if chapter==2 and kind in [0,1,2,5]:
		var id:String=["log","photo","family","unused","unused","bell"][kind]
		var local:=house.to_global(Vector3(-2.30,.99,.85))-area.global_position
		box(local,Vector3(.43,.09,.35),AMBER,false,null,.3)
		plate(id,local+Vector3(0,.12,0),["Netzmacherbuch lesen","Familienfoto betrachten","Maras Küchenband abspielen","","","Glockenspur anhören"][kind])

func core() -> void:
	set_atmosphere(false,true)
	body.position=Vector3(0,.1,8.8)
	var basalt:=Color("#263a3b")
	box(Vector3(0,-.19,0),Vector3(21,.38,24),basalt,true)
	for side in [-1,1]:
		box(Vector3(side*10.46,4,0),Vector3(.41,8,24),basalt,true)
		box(Vector3(0,4,side*11.77),Vector3(21,8,.44),basalt,true)
	for i in 22:
		var a:=TAU*i/22.0
		var floor_point:=Vector3(sin(a)*9.7,.02,cos(a)*9.7)
		var roof_point:=Vector3(sin(a)*4.3,6.2+sin(a*3)*1.12,cos(a)*4.3)
		pipe(floor_point,roof_point,.22,STEEL)
		pipe(roof_point,Vector3(0,7.4,0),.075,TEAL,.55)
	scene_data.outer_ring=ring(Vector3(0,2.65,-1.82),2.06,.10,TEAL,1.9)
	scene_data.inner_ring=ring(Vector3(0,2.65,-1.82),1.62,.07,AMBER,1.4)
	lamp(Vector3(0,2.95,-1.81),TEAL,3.1,11)
	figure(Vector3(2.48,.04,4.78),true,-.43)
	control("last",Vector3(-4.34,0,1.19),"DÄMPFUNG","Die Grenze schließen")
	control("rising",Vector3(4.34,0,1.19),"KOPPLUNG","Mara herüberholen")
	for i in 3:
		var pos:=Vector3(-3.44+i*1.54,0,-6.7)
		control("digit"+str(i),pos,"SPUR "+str(i+1),"Ziffer weiterdrehen")
		scene_data["value"+str(i)]=plaque("0",pos+Vector3(0,1.76,.18),39)
	control("first",Vector3(1.61,0,-6.7),"NULLSIGNAL","Ursprungssignal senden")
	control("echo",Vector3(4.7,0,-6.7),"ECHOARCHIV","Aufgezeichnete Spuren nachschlagen")
	say_line("Mara? · Elias. Komm näher. Öffne die Grenze nur dieses eine Mal.",6)

func hud_refresh() -> void:
	var goal := ""
	match chapter:
		0:
			goal=["Am roten Pegel auf Ebbe warten.","Pumpenbuch rechts lesen. Zulauf schließen, Umlauf öffnen, Pumpe starten.","Den Funkumsetzer vor dem Schott untersuchen.","Rechts über den Holzsteg zur Druckschleuse."][clampi(task,0,3)]
		1:
			goal=["Den Phasenkoppler in der Sicherheitszentrale links holen.","Vor dem Einsturz auf 1998 wechseln. Hinter dem Gang liegt das Archiv links.","An der hinteren Säule auf 2026 wechseln. Zur Eindämmungsschleuse am Gangende."][clampi(task,0,2)]
		2:
			goal="Fischerhaus, Haus Miller und Haus Ward durchsuchen. Funde: %d/3."%[shore_count()] if shore_count()<3 else "Mara im Café Morgenrot treffen. Mit E das Gespräch fortsetzen."
		3:
			goal=["Relais 1 vor der Küstenpost schließen.","Relais 2 vor Haus Ward schließen.","Relais 3 vor dem Uhrwerk schließen.","Durch den Hinterausgang von Haus Ward. Am Kai rechts zum Turm.","Im Kern die Grenze schließen, öffnen oder mit dem Nullsignal stabilisieren."][clampi(task,0,4)]
	hud.text=TITLES[chapter]+"\n"+goal

func shore_count() -> int:
	return int(finds.has("log"))+int(finds.has("photo"))+int(finds.has("family"))

func say_line(what: String, duration := 5.0) -> void:
	subtitle.text=what
	subtitle_left=duration

func play_sound(id: String, at: Vector3, volume := -6.0) -> void:
	var path:="res://assets/audio/"+id+".wav"
	if ResourceLoader.exists(path):
		audio.global_position=at
		audio.stream=load(path)
		audio.volume_db=volume
		audio.play()

func save() -> void:
	var slot:=ConfigFile.new()
	slot.set_value("campaign","chapter",chapter)
	slot.set_value("campaign","task",task)
	slot.set_value("campaign","finds",finds)
	slot.save(SAVE)

func advance() -> void:
	task=0
	build(chapter+1)

func remove_receiver() -> void:
	for target in scene_data.receiver_group:
		if is_instance_valid(target): target.queue_free()
	var debris:=box(Vector3(-.24,.27,-18),Vector3(.86,.28,.56),Color("#76564b"))
	debris.rotation.z=-.3
	lamp(Vector3(-.27,.38,-17.78),Color("#cf7050"),.83,3.5)

func act(id: String) -> void:
	if id.is_empty(): return
	play_sound("switch",body.global_position,-13)
	match id:
		"ebb":
			if task==0:
				task=1
				scene_data.front.position.y=3.91
				say_line("Gezeitenpegel · Ebbe. Der Eingang ist frei.")
		"cave_spool":
			finds.hydro=true
			say_line("Pumpenbuch · Zulauf zu. Umlauf auf. Dann START. Auf dem Hydrofon sind drei Schläge zu hören.",9)
		"inlet","bypass":
			if task==1:
				badges[id]=not badges.get(id,false)
				say_line(("Zulauf geschlossen." if badges[id] else "Zulauf geöffnet.") if id=="inlet" else ("Umlauf geöffnet." if badges[id] else "Umlauf geschlossen."))
		"pump":
			if task==1:
				if badges.get("inlet",false) and badges.get("bypass",false):
					task=2
					play_sound("rv_unlock",body.global_position)
					say_line("Stimme aus dem Umsetzer · Elias? Ich warte hinter dem Schott. Antworte mir.",7)
					play_sound("rv_intro_mara",area.to_global(Vector3(0,.9,-18)),-1)
				else: say_line("Pumpe verriegelt · Zulauf schließen und Umlauf öffnen.",6)
		"receiver":
			if task==2 and surge<0:
				surge=0
				say_line("Zwei Schläge. Dann ein Schritt direkt neben dem Umsetzer.",2.5)
		"cave_end":
			if task==3: advance()
			else: say_line("Die Druckschleuse ist verriegelt. Der Umsetzer vor dem Schott empfängt einen Ruf.")
		"coupler":
			if task==0:
				task=1
				say_line("Phasenkoppler aufgenommen. Das blaue Pult im Hauptgang lässt sich jetzt bedienen.")
		"phase":
			if task>=1:
				past=not past
				phase_label.text="17.11.1998" if past else "18.11.2026"
				var rubble:Node3D=scene_data.rubble
				rubble.position.y=5 if past else 1.25
				light.light_color=AMBER if past else TEAL
				world_env.ambient_light_color=AMBER if past else TEAL
				play_sound("rv_shift",body.global_position)
				say_line("Nachtschicht · 17. November 1998" if past else "Evakuiert · 18. November 2026")
			else: say_line("Der tragbare Phasenkoppler liegt in der Sicherheitszentrale.")
		"archive":
			if past and not played: archive_scene()
			elif not past: say_line("In dieser Phase ist die Videoquelle beschädigt.")
		"server_spool":
			if past:
				finds.reverse=true
				say_line("Rücklaufkopie · Ein Puls. Zweite Ziffer: 1.")
			else: say_line("In der Gegenwart sind die Datenträger leer.")
		"station_end":
			if task>=2 and not past: advance()
			else: say_line("Archivband sichern und die Zeitsperre auf 2026 einstellen.")
		"log","photo","family","bell":
			finds[id]=true
			var clue:Dictionary={
				"log":"Netzmacherbuch · Derselbe Mann kam am Mittwoch zurück. Er war viel älter, knotete aber genau wie Elias.",
				"photo":"Familienfoto · Derselbe Mann im Hintergrund trägt auf drei verschieden alten Bildern dieselbe geflickte Jacke.",
				"family":"Küchenband · Zwischen zwei Wörtern knarrt der Stuhl. Das Geräusch war auch auf dem Funkspruch vom Boot.",
				"bell":"Ungeschnittene Spur · Sechs Glockenschläge. Dritte Ziffer: 6."}
			say_line(clue[id],8)
			if id=="family": play_sound("rv_intro_mara",body.global_position)
		"mara": talk()
		"post","ward","clock":
			if task==["post","ward","clock"].find(id):
				task+=1
				if task==3:
					surge=0
					scene_data.roadblock.position.y=1.225
					scene_data.guard.show()
					play_sound("horn",body.global_position,-3)
					say_line("Elias · Er sperrt die Straße. Hinter dem Haus Ward leuchten die Markierungen zum Kai.",8)
				else: say_line("Relais %d geschlossen."%task)
			else: say_line("Schaltfolge · Post, Haus Ward, Uhrwerk.")
		"tower":
			if task==3 and escaped_ward:
				task=4
				build(chapter)
			else: say_line("Folge nach den drei Relais den Markierungen durch Haus Ward.")
		"echo":
			var missing: Array[String]=[]
			for field in ["hydro","reverse","bell"]:
				if not finds.has(field): missing.append(field)
			if missing.is_empty():
				say_line("Echos · Höhle: drei Schläge. Server: ein Rücklaufpuls. Lesesaal: sechs Glockenschläge.",9)
			else:
				var names := {"hydro":"Hydrofon in der Höhle", "reverse":"Server in Platform 6", "bell":"Glockenspur im Lesesaal"}
				var options: Array=[]
				for field in missing:
					options.append([names[field],listen_echo.bind(field)])
				options.append(["Zurück",dismiss])
				overlay("Echoarchiv","Sichere eine der verpassten Aufnahmen.",options)
		"last","rising":
			confirm(id)
		"first":
			if digits==[3,1,6] and finds.has("hydro") and finds.has("reverse") and finds.has("bell"): confirm(id)
			else: say_line("Kein Gleichlauf. Die drei Ziffern ergeben sich aus den Spuren im Echoarchiv.")
		_:
			if id.begins_with("digit"):
				var n:=int(id.right(1))
				digits[n]=(digits[n]+1)%10
				scene_data["value"+str(n)].text=str(digits[n])
	save()
	hud_refresh()

func listen_echo(field: String) -> void:
	dismiss()
	finds[field]=true
	var messages: Dictionary = {"hydro":"Hydrofon · Drei Schläge.", "reverse":"Rücklaufkopie · Ein Puls.", "bell":"Uhrband · Sechs Glockenschläge."}
	play_sound("tracking",body.global_position)
	say_line(messages[field],8)
	save()

func talk() -> void:
	if shore_count()<3:
		say_line("Mara · Sieh dir erst die Erinnerungen in den drei Häusern an. Dann kann ich es dir erklären.",7)
		return
	var lines:=[
		"Mara · Du klopfst noch immer zweimal. Das hast du auch beim letzten Mal getan, als du nach mir gesucht hast.",
		"Mara · The Drowned bist du, Elias. Älter. In seiner Zeit wollte er mich retten. Die Struktur verband sich mit ihm. Seine Gestalt ging verloren. Seine Erinnerungen blieben.",
		"Elias · Er hat den Umsetzer zerstört. Sekunden später war der Gang unter Wasser. Er hat mich gerade noch vor der Druckwelle gerettet.",
		"Mara · Den Funkspruch auf deinem Boot habe ich nie gesendet. Die Struktur hat meine Stimme aus deinen Erinnerungen nachgebildet.",
		"Mara · Sie braucht dich auf beiden Seiten, um die Grenze ganz zu öffnen. Wenn die Straße untergeht, nimm den Hinterausgang von Haus Ward und geh am Kai zum Leuchtfeuer."]
	if story_index>=lines.size():
		advance()
	else:
		say_line(lines[story_index],19)
		story_index+=1

func archive_scene() -> void:
	var actor:=figure(Vector3(-7.59,0,-23.73),false,.21)
	actor.pose("listen",.72)
	film=Camera3D.new()
	area.add_child(film)
	film.position=Vector3(-6.49,1.49,-20.97)
	film.environment=world_env
	film.look_at(actor.global_position+Vector3(0,1.21,0))
	film.make_current()
	played=true
	say_line("P6-08  /  17.11.1998\nDer erwachsene Mann trägt Elias’ Jacke. Er klopft zweimal und blickt in die Kamera.",8.5)
	play_sound("tracking",actor.global_position,-2)
	await get_tree().create_timer(8.5).timeout
	if not is_instance_valid(film): return
	film.queue_free()
	film=null
	actor.queue_free()
	camera.make_current()
	task=2
	hud_refresh()
	save()
	say_line("Elias · Am siebzehnten November 1998 war ich ein Baby.",7)

func overlay(heading: String, contents: String, buttons: Array) -> void:
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
	panel=PanelContainer.new()
	layer.add_child(panel)
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left=-274
	panel.offset_top=-132
	var style:=StyleBoxFlat.new()
	style.bg_color=Color("#101c20")
	style.content_margin_left=28
	style.content_margin_right=28
	style.content_margin_top=21
	style.content_margin_bottom=24
	panel.add_theme_stylebox_override("panel",style)
	var column:=VBoxContainer.new()
	column.custom_minimum_size.x=495
	column.add_theme_constant_override("separation",12)
	panel.add_child(column)
	var title:=Label.new()
	title.text=heading
	title.modulate=AMBER
	title.add_theme_font_size_override("font_size",32)
	column.add_child(title)
	var text:=Label.new()
	text.text=contents
	text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	column.add_child(text)
	for item in buttons:
		var button:=Button.new()
		button.text=item[0]
		button.custom_minimum_size.y=39
		column.add_child(button)
		button.pressed.connect(item[1])

func dismiss() -> void:
	if is_instance_valid(panel): panel.queue_free()
	panel=null
	Input.mouse_mode=Input.MOUSE_MODE_CAPTURED

func confirm(id: String) -> void:
	overlay("Die Entscheidung","Willst du diese Schaltung auslösen?",
		[["Auslösen",func() -> void: dismiss(); epilogue(id)],["Zurück",dismiss]])

func epilogue(id: String) -> void:
	var endings:Dictionary={
		"last":["The Last Light","Elias schließt die Grenze. Stillwater erlischt. Mara bleibt auf der anderen Seite. Ein Schiff empfängt Wochen später Elias’ Stimme auf Kanal 16."],
		"rising":["The Rising Tide","Mara steigt hinter Elias ins Boot. Am Morgen melden sich in einer anderen Küstenstadt alle Funkgeräte zugleich."],
		"first":["The First Signal","Das Ursprungssignal kehrt zu seiner Quelle zurück. Stillwater erwacht. Auf dem Strandfoto entdecken Elias und Mara hinter sich eine dritte Gestalt."]}
	var ending:Array=endings[id]
	finish_title=ending[0]
	finds["ending_"+id]=true
	save()
	overlay(ending[0],ending[1],[["Andere Entscheidung",func() -> void: finish_title=""; dismiss()],["Hauptmenü",func() -> void: returned.emit()]])

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode==KEY_ESCAPE:
		if is_instance_valid(panel):
			finish_title=""
			dismiss()
		else:
			overlay("Pause",TITLES[chapter],[["Fortsetzen",dismiss],["Die neuen Kapitel neu beginnen",restart],["Hauptmenü",func() -> void: returned.emit()]])
		get_viewport().set_input_as_handled()
		return
	if is_instance_valid(panel) or is_instance_valid(film): return
	if event is InputEventMouseMotion and Input.mouse_mode==Input.MOUSE_MODE_CAPTURED:
		body.rotate_y(-event.relative.x*.0026)
		camera.rotation.x=clampf(camera.rotation.x-event.relative.y*.0026,-1.46,1.46)
	elif event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode==KEY_E: act(aim)
		if event.physical_keycode==KEY_F: torch.visible=not torch.visible

func restart() -> void:
	dismiss()
	task=0
	finds.clear()
	build(0)

func _physics_process(delta: float) -> void:
	if body==null or is_instance_valid(panel) or is_instance_valid(film): return
	var direction:=Vector2(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),
		float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W))).limit_length()
	var speed:=4.4 if Input.is_physical_key_pressed(KEY_SHIFT) else 2.64
	var move:=body.basis*Vector3(direction.x,0,direction.y)*speed
	body.velocity.x=move.x
	body.velocity.z=move.z
	body.velocity.y-=delta*17
	body.move_and_slide()
	if body.position.y< -3:
		body.position=Vector3(0,.15,9)
		body.velocity=Vector3.ZERO
	var ray:=PhysicsRayQueryParameters3D.create(camera.global_position,camera.global_position-camera.global_basis.z*3.5,5)
	ray.collide_with_areas=true
	ray.exclude=[body.get_rid()]
	var target:=get_world_3d().direct_space_state.intersect_ray(ray)
	aim=""
	if not target.is_empty() and target.collider.has_meta("action"): aim=target.collider.get_meta("action")
	prompt.text=("E  ·  "+actions[aim]) if actions.has(aim) else ""

func _process(delta: float) -> void:
	if area==null or is_instance_valid(panel): return
	clock+=delta
	subtitle_left-=delta
	subtitle.visible=subtitle_left>0
	if chapter==0 and surge>=0 and task==2:
		var previous:=surge
		surge+=delta
		var actor:Node3D=scene_data.double
		actor.position=Vector3(-2.52,.03,-20.2).lerp(Vector3(-1.10,.03,-18.32),smoothstep(0,1.03,surge))
		actor.pose("walk" if surge<.95 else "startle",.78)
		if previous<=1.05 and surge>1.05:
			remove_receiver()
			play_sound("rv_gear",actor.global_position,-2)
		scene_data.shutter.position.y=lerpf(3.91,1.29,smoothstep(1.0,1.7,surge))
		scene_data.water.position.y=lerpf(-.08,.73,smoothstep(1.7,2.8,surge))
		if surge>2.9:
			task=3
			hud_refresh()
			save()
			say_line("Elias · Er hat das Gerät zerschlagen. Das Schott hat die Welle vom Stollen ferngehalten.",7)
	if chapter==2:
		for i in 3:
			var actor:Node3D=scene_data["resident"+str(i)]
			var phase:=sin(clock*.21+i)
			actor.position.x=-26+i*16+phase*3.4
			actor.rotation.y=PI*.5 if cos(clock*.21+i)>0 else -PI*.5
			actor.pose("walk",.58)
	if chapter==3 and scene_data.has("street_water") and task==3:
		surge+=delta
		if absf(body.position.x-7)<1.25 and body.position.z< -14.2 and body.position.z> -17.2:
			escaped_ward=true
		scene_data.street_water.position.y=minf(.51,-.09+surge*.014)
		if surge>58 and body.position.z> -15 and not wet:
			wet=true
			escaped_ward=true
			body.position=Vector3(7,.13,-16.86)
			say_line("Elias · Jemand hat mich am Ärmel aufs Trockene gezogen. Zwei Schläge aus der Dunkelheit.",7)
	if scene_data.has("inner_ring"):
		scene_data.inner_ring.rotation.y=clock*.52
		scene_data.outer_ring.rotation.z=clock*.24
