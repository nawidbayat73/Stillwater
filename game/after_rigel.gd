extends Node3D

signal returned

const TITLES := ["IV · Beneath the Tide", "V · Platform 6", "VI · The Other Shore", "VII · The Last Tide"]
const AMBER := Color("#d7b185")
const TEAL := Color("#99c5b9")
const SLATE := Color("#44585c")
const WOOD := Color("#695048")
const STEEL := Color("#38565a")
const ShoreArtwork = preload("res://shore_art.gd")
const SAVE := "user://last_tide_restored.cfg"

var base
var coast: RefCounted
var shore_art := ShoreArtwork.new()
var area: Node3D
var body: CharacterBody3D
var camera: Camera3D
var torch: SpotLight3D
var light: DirectionalLight3D
var world_env: Environment
var layer: CanvasLayer
var hud: Label
var heading: Label
var hud_box: PanelContainer
var prompt_box: PanelContainer
var subtitle_box: PanelContainer
var footage: Control
var prompt: Label
var subtitle: Label
var panel: PanelContainer
var crosshair: Label
var audio: AudioStreamPlayer3D
var phase_label: Label3D
var phase_lamps: Array[OmniLight3D]=[]
var phase_colors: Array[Color]=[]
var film_target: Node3D
var film_start:=Vector3.ZERO
var film_time:=0.0
var ending_camera: Camera3D
var ending_id := ""
var ending_elapsed := 0.0
var ending_light: OmniLight3D
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
	var frame:=Control.new()
	layer.add_child(frame)
	frame.mouse_filter=Control.MOUSE_FILTER_IGNORE
	frame.theme=base.interface.root.theme
	frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	hud_box=PanelContainer.new()
	frame.add_child(hud_box)
	hud_box.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
	hud_box.offset_left=34
	hud_box.offset_top=29
	hud_box.mouse_filter=Control.MOUSE_FILTER_IGNORE
	hud_box.add_theme_stylebox_override("panel",panel_style(Color(.054,.082,.097,.87),3))
	var column:=VBoxContainer.new()
	hud_box.add_child(column)
	column.mouse_filter=Control.MOUSE_FILTER_IGNORE
	column.add_theme_constant_override("separation",3)
	heading=make_label(column,load("res://assets/ui/PlexMono.ttf"),13,Color("#dbad7f"))
	hud=make_label(column,load("res://assets/ui/Barlow.ttf"),17,Color("#e6e2d3"))

	prompt_box=PanelContainer.new()
	frame.add_child(prompt_box)
	base.interface.anchor(prompt_box,Vector4(.40,.5,.60,.5),Vector4(0,32,0,62))
	prompt_box.add_theme_stylebox_override("panel",panel_style(Color(.055,.087,.095,.86)))
	prompt_box.mouse_filter=Control.MOUSE_FILTER_IGNORE
	prompt=make_label(prompt_box,load("res://assets/ui/Barlow.ttf"),17,Color("#ece4ce"))
	prompt.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	prompt_box.hide()

	crosshair=make_label(frame,load("res://assets/ui/PlexMono.ttf"),13,Color("#ddd9c5"))
	base.interface.anchor(crosshair,Vector4(.5,.5,.5,.5),Vector4(-3,-8,3,7))
	crosshair.text="·"

	subtitle_box=PanelContainer.new()
	frame.add_child(subtitle_box)
	base.interface.anchor(subtitle_box,Vector4(.155,1,.845,1),Vector4(0,-111,0,-30))
	subtitle_box.add_theme_stylebox_override("panel",panel_style(Color(.028,.046,.052,.91)))
	subtitle_box.mouse_filter=Control.MOUSE_FILTER_IGNORE
	subtitle=make_label(subtitle_box,load("res://assets/ui/Barlow.ttf"),20,Color("#e7e1d4"))
	subtitle.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	subtitle.vertical_alignment=VERTICAL_ALIGNMENT_CENTER
	subtitle.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	subtitle_box.hide()

	footage=Control.new()
	frame.add_child(footage)
	footage.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	footage.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var top: ColorRect=base.interface.color_box(footage,Color("#101819"),Vector4(0,0,1,.095))
	top.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var lower: ColorRect=base.interface.color_box(footage,Color("#101819"),Vector4(0,.925,1,1))
	lower.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var code:=make_label(footage,load("res://assets/ui/PlexMono.ttf"),14,Color("#d7debd"))
	base.interface.anchor(code,Vector4(.05,.045,.86,.088))
	code.text="●   P6-08   /   17.11.1998   /   BEOBACHTUNG"
	footage.hide()

func make_label(parent: Control,font: Font,size: int,color: Color) -> Label:
	var label:=Label.new()
	parent.add_child(label)
	label.add_theme_font_override("font",font)
	label.add_theme_font_size_override("font_size",size)
	label.add_theme_color_override("font_color",color)
	label.mouse_filter=Control.MOUSE_FILTER_IGNORE
	return label

func panel_style(color: Color,left_border := 0) -> StyleBoxFlat:
	var style:=StyleBoxFlat.new()
	style.bg_color=color
	style.border_width_left=left_border
	style.border_color=Color("#b38a65")
	style.content_margin_left=13
	style.content_margin_right=13
	style.content_margin_top=6
	style.content_margin_bottom=7
	return style

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

func lamp(at: Vector3, tint: Color, energy := 1.4, reach := 7.5) -> OmniLight3D:
	box(at+Vector3(0,.2,0),Vector3(.45,.10,.20),tint,false,null,.9)
	var node:=OmniLight3D.new()
	area.add_child(node)
	node.position=at
	node.light_color=tint
	node.light_energy=energy
	node.omni_range=reach
	return node

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
	var prop: Node3D=base.world.place(id,pos,yaw,solid,scale_factor,area)
	for part in prop.get_children():
		if part is MeshInstance3D and part.mesh==base.world.meshes[id]:
			coast.apply_to(part,id,solid)
	return prop

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
	var face:=Node3D.new()
	area.add_child(face)
	face.position=pos
	shore_art.attach("instruments",face,false)
	plaque(title,pos+Vector3(0,1.37,.18),24)
	plate(id,pos+Vector3(0,1.02,.482),hint)

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
	phase_lamps.clear()
	phase_colors.clear()
	footage.hide()
	hud_box.show()
	prompt_box.hide()
	subtitle_box.hide()
	subtitle_left=0.0
	crosshair.show()
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
	camera.far=95
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
	coast.dress_figure(actor)
	actor.pose("idle",.74)
	return actor

func cave() -> void:
	set_atmosphere()
	world_env.ambient_light_color=Color("#9fb1a8")
	world_env.ambient_light_energy=.40
	world_env.fog_density=.027
	world_env.fog_light_color=Color("#405655")
	light.light_energy=.31
	var kit:=shore_art.attach("chapter4",area,true)
	scene_data.front=moveable(kit,"TideGate",Vector3(7.1,2.25,.23))
	scene_data.shutter=moveable(kit,"PressureGate",Vector3(7.1,2.60,.27))
	scene_data.water=water(Vector3(0,-.08,-33.9),Vector2(6.7,20.6),true)
	control("ebb",Vector3(2.45,0,7.5),"ROTER PEGEL","Auf Ebbe warten")
	plaque("GEZEITENTOR  /  P–2",Vector3(-2.47,2.96,4.15),27)
	control("inlet",Vector3(-4.65,0,-10.78),"A / ZULAUF","Zulaufventil bedienen")
	control("bypass",Vector3(-2.64,0,-10.78),"B / UMLAUF","Umlaufventil bedienen")
	control("pump",Vector3(-.69,0,-10.78),"C / START","Pumpe P-2 starten")
	control("cave_spool",Vector3(4.25,0,-1.17),"PUMPENBUCH","Pumpenbuch und Spule ansehen")
	var first_part:=area.get_child_count()
	control("receiver",Vector3(-.25,0,-18),"FUNKUMSETZER","Auf Maras Stimme antworten")
	scene_data.receiver_group=area.get_children().slice(first_part)
	scene_data.double=figure(Vector3(-2.52,.03,-20.2),true,0)
	control("cave_end",Vector3(0,0,-43.7),"PLATFORM 6","Druckschleuse betreten")
	shore_art.play_loop(area,"coast",Vector3(2,0,-25),-22)
	if task>=1:
		scene_data.front.position.y=3.88
	if task>=3:
		scene_data.shutter.position.y=1.29
		scene_data.water.position.y=.62
		remove_receiver()

func moveable(kit: Node3D, id: String, size: Vector3) -> Node3D:
	var result:=kit.find_child(id,true,false) as Node3D
	shore_art.add_colliders(result,[[0.0,0.0,0.0,size.x,size.y,size.z,0.0]])
	return result

func station() -> void:
	set_atmosphere()
	var kit:=shore_art.attach("chapter5",area,false)
	for part in kit.get_children():
		if part is OmniLight3D:
			phase_lamps.append(part)
			phase_colors.append(part.light_color)
	var sides:=[["SICHERHEIT","BIOLOGIE","GENERATOR","ARCHIV 08","BEOBACHTUNG"],["UNTERKUNFT","SIGNALFORSCHUNG","SERVER","WASSERKONTROLLE","LAGER"]]
	for i in 5:
		var z:=5.7-i*9.0
		for side in [-1,1]:
			var caption:String=sides[0 if side==-1 else 1][i]
			plaque(caption,Vector3(side*2.531,2.52,z),24,-side*PI/2)
	scene_data.rubble=moveable(kit,"CollapsedBulkhead",Vector3(5.39,2.50,.75))
	control("coupler",Vector3(-5.57,0,5.77),"PHASENKOPPLER","Tragbaren Koppler aufnehmen")
	control("phase",Vector3(1.40,0,-4.6),"ZEITPHASE","Zwischen 1998 und 2026 wechseln")
	control("phase",Vector3(1.4,0,-28.65),"ZEITPHASE","Zwischen 1998 und 2026 wechseln")
	phase_label=plaque("2026",Vector3(0,2.74,-7.51),37)
	control("archive",Vector3(-5.67,0,-21.64),"DAS BAND VON 1998","Archivaufnahme ansehen")
	control("server_spool",Vector3(5.69,0,-12.64),"RÜCKLAUFKOPIE","Zweite Spur sichern")
	control("station_end",Vector3(0,0,-42.8),"CONTAINMENT","Eindämmungsschleuse öffnen")
	update_phase_visuals()

func update_phase_visuals() -> void:
	phase_label.text="17.11.1998" if past else "18.11.2026"
	var rubble:Node3D=scene_data.rubble
	rubble.position.y=5 if past else 1.25
	world_env.ambient_light_color=Color("#b8b2a4") if past else Color("#84aeb0")
	world_env.ambient_light_energy=.52 if past else .40
	world_env.fog_light_color=Color("#6d6861") if past else Color("#789496")
	light.light_energy=.26 if past else .16
	for i in phase_lamps.size():
		phase_lamps[i].light_color=phase_colors[i].lerp(Color("#edbb80"),.62) if past else phase_colors[i]

func shore(storm: bool) -> void:
	world_env=shore_art.atmosphere(storm)
	camera.environment=world_env
	camera.far=180
	light.rotation_degrees=Vector3(-25,-121,0)
	light.light_color=Color("#91afbf") if storm else Color("#ffe5c4")
	light.light_energy=.35 if storm else .92
	light.directional_shadow_max_distance=71
	light.directional_shadow_mode=DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	light.shadow_bias=.085
	light.shadow_normal_bias=.90
	body.position=Vector3(-32.25,.10,1.60)
	body.rotation.y=-PI/2-.13

	var waterfront:=shore_art.attach("ufer",area,storm)
	if waterfront==null:
		say_line("Die Uferstraße konnte nicht geladen werden.",8)
		return
	shore_art.water(area,Vector3(0,-.32,-69),Vector2(245,95),storm)
	old_mesh("trawler",Vector3(-25.62,-.49,-29.37),-.17,.73,false)
	old_mesh("lighthouse",Vector3(28.02,1.15,-41.93),.11,.99,false)
	shore_art.play_loop(area,"coast",Vector3(-11,.6,-23.2),-21 if storm else -25)
	if storm:
		shore_art.play_loop(area,"rain",Vector3(3,3,0),-24)
	var van:=old_mesh("minivan",Vector3(-36.31,.025,3.26),-PI/2,.88,true)
	van.name="Lieferwagen"
	if storm:
		var overlay_set:=shore_art.attach("sturm",area,true)
		if overlay_set==null:
			say_line("Die Flutkulisse konnte nicht geladen werden.",8)
			return
		scene_data.street_water=shore_art.water(area,Vector3(0,-.12,0),Vector2(79,8.3),true,true)
		for relay in [["post","Küstenpost",1],["ward","Haus Ward",2],["clock","Uhrwerk",3]]:
			var position:=shore_art.point_at("sturm",relay[0])
			plate(relay[0],position,"Relais %d schließen"%relay[2],Vector3(.86,.67,.48))
			var post: bool = relay[0]=="post"
			plaque("%02d   %s"%[relay[2],str(relay[1]).to_upper()],position+Vector3(0,.45,.19 if post else -.19),
				23,PI if post else 0.0)
		var tower:=shore_art.point_at("sturm","tower")
		plate("tower",tower,"In die Lichtkammer hinabsteigen",Vector3(.94,.79,.55))
		plaque("BLACKCLIFF  /  W–06",tower+Vector3(0,.47,-.16),27)
		var gate:=overlay_set.find_child("HighWaterGate",true,false) as Node3D
		scene_data.roadblock=gate
		shore_art.add_colliders(gate,[[0.0,0.0,0.0,.66,2.45,9.20,0.0]])
		gate.position.y=-3.0
		scene_data.guard=figure(Vector3(16.4,.05,-1.3),true,-PI/2)
		scene_data.guard.hide()
		if task==3:
			surge=0
			gate.position.y=1.225
			scene_data.guard.show()
	else:
		var entries := {
			"log": "Netzmacherbuch lesen",
			"photo": "Familienfoto betrachten",
			"family": "Maras Küchenband abspielen",
			"bell": "Glockenspur anhören"
		}
		for id: String in entries:
			plate(id,shore_art.point_at("ufer",id),entries[id],Vector3(.71,.50,.53))
		var mara:=figure(shore_art.point_at("ufer","mara"),false,PI)
		shore_art.add_colliders(mara,[[0.0,.85,0.0,.44,1.7,.34,0.0]])
		plate("mara",mara.position+Vector3(0,1,-.32),"Mit Mara sprechen",Vector3(.72,1.7,.59))
		for i in 3:
			scene_data["resident"+str(i)]=figure(Vector3(-26+i*16,.11,-4.2+i*2),false,PI/2)

func core() -> void:
	set_atmosphere(false,true)
	world_env.ambient_light_color=Color("#91acaa")
	world_env.ambient_light_energy=.35
	world_env.fog_density=.025
	world_env.fog_light_color=Color("#455e62")
	body.position=Vector3(0,.1,8.8)
	var kit:=shore_art.attach("chapter7",area,true)
	scene_data.outer_ring=kit.find_child("FieldOuter",true,false)
	scene_data.inner_ring=kit.find_child("FieldInner",true,false)
	ending_light=lamp(Vector3(0,2.95,-1.81),TEAL,2.27,10)
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
	heading.text=TITLES[chapter].to_upper()
	hud.text=goal

func shore_count() -> int:
	return int(finds.has("log"))+int(finds.has("photo"))+int(finds.has("family"))

func say_line(what: String, duration := 5.0) -> void:
	subtitle.text=what
	subtitle_left=duration
	subtitle_box.visible=bool(base.preferences.settings.subtitles)

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
				update_phase_visuals()
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
	var actor:=figure(Vector3(-5.73,0,-24.01),false,-.38)
	actor.pose("listen",.72)
	film=Camera3D.new()
	area.add_child(film)
	film.position=Vector3(-6.19,1.63,-22.55)
	film.fov=65
	film_start=film.position
	film_target=actor
	film_time=0.0
	film.environment=world_env
	film.look_at(actor.global_position+Vector3(0,1.23,0))
	hud_box.hide()
	prompt_box.hide()
	crosshair.hide()
	footage.show()
	film.make_current()
	played=true
	say_line("P6-08  /  17.11.1998\nDer erwachsene Mann trägt Elias’ Jacke. Er klopft zweimal und blickt in die Kamera.",8.5)
	play_sound("tracking",actor.global_position,-2)
	await get_tree().create_timer(8.5).timeout
	if not is_instance_valid(film): return
	film.queue_free()
	film=null
	actor.queue_free()
	footage.hide()
	hud_box.show()
	crosshair.show()
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
	title.add_theme_font_override("font",load("res://assets/ui/InstrumentSerif.ttf"))
	title.text=heading
	title.modulate=AMBER
	title.add_theme_font_size_override("font_size",45)
	column.add_child(title)
	var text:=Label.new()
	text.add_theme_font_override("font",load("res://assets/ui/Barlow.ttf"))
	text.add_theme_font_size_override("font_size",21)
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
	if is_instance_valid(ending_camera):
		ending_camera.queue_free()
		ending_camera=null
		ending_id=""
		finish_title=""
		camera.make_current()
		ending_light.light_color=TEAL
		ending_light.light_energy=2.27
		scene_data.outer_ring.show()
		scene_data.inner_ring.show()
		scene_data.inner_ring.scale=Vector3.ONE
		hud_box.show()
		crosshair.show()
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
	ending_camera=Camera3D.new()
	ending_camera.environment=world_env
	ending_camera.fov=63
	area.add_child(ending_camera)
	ending_camera.make_current()
	ending_id=id
	ending_elapsed=0.0
	prompt_box.hide()
	hud_box.hide()
	crosshair.hide()
	subtitle_box.hide()
	play_sound("rv_unlock" if id=="last" else "rv_shift",area.to_global(Vector3(0,2,-2)),-9)
	update_ending(0.0)
	overlay(ending[0],ending[1],[["Andere Entscheidung",dismiss],["Hauptmenü",func() -> void: returned.emit()]])
	panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	panel.offset_left=28
	panel.offset_right=535
	panel.offset_top=-232
	panel.offset_bottom=-22

func update_ending(delta: float) -> void:
	ending_elapsed+=delta
	var fade:=smoothstep(0.0,3.7,ending_elapsed)
	var start:=Vector3(-5.83,2.45,6.05)
	var finish:=Vector3(-5.09,2.25,4.53)
	var focus:=Vector3(.63,2.40,-2.46)
	var outer: Node3D=scene_data.outer_ring
	var inner: Node3D=scene_data.inner_ring
	match ending_id:
		"last":
			ending_light.light_color=TEAL.lerp(Color("#9b8d79"),fade)
			ending_light.light_energy=lerpf(2.27,.22,fade)
			inner.scale=Vector3.ONE*lerpf(1.0,.13,fade)
			outer.visible=fade<.95
			inner.visible=fade<.88
		"rising":
			start=Vector3(-6.03,2.05,5.42)
			finish=Vector3(-5.20,1.95,4.22)
			ending_light.light_color=TEAL.lerp(Color("#ff915c"),fade)
			ending_light.light_energy=lerpf(2.27,5.1,fade)
			inner.scale=Vector3.ONE*lerpf(1.0,1.17,fade)
			outer.rotation.z=clock*.24+ending_elapsed*.33
		"first":
			start=Vector3(-5.34,2.38,4.84)
			finish=Vector3(-5.99,2.40,3.95)
			ending_light.light_color=TEAL.lerp(Color("#c9f3df"),fade)
			ending_light.light_energy=lerpf(2.27,3.43,fade)
			outer.rotation.z=lerpf(clock*.24,.0,fade)
	inner.rotation.y=clock*.52+ending_elapsed*.19*(1.0-fade)
	ending_camera.position=start if base.preferences.settings.reduced else start.lerp(finish,fade)
	ending_camera.look_at(area.to_global(focus))

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
	elif event.is_action_pressed("interact"):
		act(aim)
	elif event.is_action_pressed("torch"):
		torch.visible=not torch.visible

func restart() -> void:
	dismiss()
	task=0
	finds.clear()
	build(0)

func _physics_process(delta: float) -> void:
	if body==null or is_instance_valid(panel) or is_instance_valid(film): return
	var direction:=Input.get_vector("left","right","forward","back")
	var speed:=4.4 if Input.is_action_pressed("sprint") else 2.64
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
	prompt_box.visible=actions.has(aim)
	prompt.text=("%s   ·   "%base.preferences.key_labels.interact+actions[aim]) if actions.has(aim) else ""

func _process(delta: float) -> void:
	if is_instance_valid(ending_camera):
		update_ending(delta)
		return
	if area==null or is_instance_valid(panel): return
	clock+=delta
	subtitle_left-=delta
	subtitle_box.visible=subtitle_left>0 and bool(base.preferences.settings.subtitles)
	if is_instance_valid(film) and is_instance_valid(film_target):
		film_time+=delta
		if not base.preferences.settings.reduced:
			film.position=film_start.lerp(Vector3(-6.22,1.59,-22.76),smoothstep(.2,7.9,film_time))
			film.look_at(film_target.global_position+Vector3(0,1.28,0))
		if film_time>3.4:
			film_target.pose("turn",.69)
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
		if absf(body.position.x-7)<1.30 and body.position.z< -15.40 and body.position.z> -17.2:
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
