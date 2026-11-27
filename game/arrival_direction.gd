extends Node
## Stage the original boat sequence and dress chapters I–III without replacing their puzzles.

const Artwork=preload("res://shore_art.gd")
const SKY=preload("res://landfall_sky.gdshader")
const WATER=preload("res://landfall_water.gdshader")

var game: Node
var art:=Artwork.new()
var installed := {}
var harbor_env: Environment
var hill_env: Environment
var ship_env: Environment
var opener: Camera3D
var title_layer: CanvasLayer
var titles: Control
var title_small: Label
var title_main: Label
var title_where: Label
var marker: OmniLight3D
var radio_hint: Callable
var dock_hint: Callable
var was_at_sea := false
var reveal_clock := -1.0
var after_dock := -1.0
var last_mode := ""
var deck := Node3D.new()

func mount(host: Node) -> void:
	game=host
	add_child(deck)
	deck.name="LandfallCameras"
	harbor_env=atmosphere(Color("#9daeb8"),Color("#607d89"),.56,.011)
	hill_env=atmosphere(Color("#aabbbd"),Color("#728791"),.49,.009)
	ship_env=atmosphere(Color("#8a9da7"),Color("#596f76"),.53,.010)
	installed["launch"]=art.attach("launch",game.arrival.launch,false)
	installed["landfall"]=art.attach("landfall",game.world,false)
	installed["chapter1"]=art.attach("chapter1",game.world,false)
	make_arrival_markers()
	create_overlay()
	opener=Camera3D.new()
	opener.environment=harbor_env
	opener.cull_mask=game.player.camera.cull_mask
	opener.fov=71.0
	opener.far=game.player.camera.far
	deck.add_child(opener)
	game.menu_camera.environment=harbor_env
	game.player.camera.environment=harbor_env
	var water: ShaderMaterial=game.world.water.material_override
	water.shader=WATER
	water.set_shader_parameter("deep",Color("#284a54"))
	water.set_shader_parameter("horizon",Color("#6a8184"))
	hint_the_receiver()

func atmosphere(ambient: Color,fog: Color,energy: float,density: float) -> Environment:
	var env:=Environment.new()
	var sky:=Sky.new()
	var mat:=ShaderMaterial.new()
	mat.shader=SKY
	sky.sky_material=mat
	sky.radiance_size=Sky.RADIANCE_SIZE_64
	env.sky=sky
	env.background_mode=Environment.BG_SKY
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=ambient
	env.ambient_light_energy=energy
	env.reflected_light_source=Environment.REFLECTION_SOURCE_SKY
	env.fog_enabled=true
	env.fog_density=density
	env.fog_light_color=fog
	env.fog_light_energy=.87
	env.fog_sky_affect=.17
	env.adjustment_enabled=true
	env.adjustment_brightness=1.05
	env.adjustment_saturation=.88
	env.adjustment_contrast=1.055
	return env

func add_point(parent: Node3D, at: Vector3, tint: Color, energy: float, radius: float) -> OmniLight3D:
	var fixture:=OmniLight3D.new()
	fixture.position=at
	fixture.light_color=tint
	fixture.light_energy=energy
	fixture.omni_range=radius
	fixture.omni_attenuation=1.29
	parent.add_child(fixture)
	return fixture

func make_arrival_markers() -> void:
	marker=add_point(game.arrival.launch,Vector3(0,1.16,1.92),Color("#eab37b"),0.0,3.6)
	add_point(game.world,Vector3(25.82,1.21,-15.37),Color("#f27658"),2.05,10.8)
	add_point(game.world,Vector3(18.22,2.17,-14.84),Color("#ffbf87"),1.48,7.55)
	add_point(game.world,Vector3(11.14,2.03,-14.12),Color("#f8c48e"),.94,6.75)
	# A restrained, feathered reflection tells the player which pier owns the red lamp.
	var water_glow:=MeshInstance3D.new()
	var plate:=QuadMesh.new()
	plate.size=Vector2(1.95,13.5)
	water_glow.mesh=plate
	water_glow.rotation.x=-PI/2
	water_glow.position=Vector3(31.88,.142,-15.45)
	water_glow.rotation.y=PI/2
	var warm:=ShaderMaterial.new()
	warm.shader=preload("res://dock_light.gdshader")
	water_glow.material_override=warm
	water_glow.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	water_glow.layers=1
	water_glow.hide()
	game.world.add_child(water_glow)
	installed["reflection"]=water_glow

func hint_the_receiver() -> void:
	var receiver: Area3D=game.world.targets.intro_receiver
	var dock: Area3D=game.world.targets.intro_dock
	radio_hint=receiver.hint
	dock_hint=dock.hint
	receiver.hint=radio_text
	dock.hint=dock_text

func radio_text() -> String:
	return "Maras Funkspruch abhören" if not str(radio_hint.call()).is_empty() else ""

func dock_text() -> String:
	return "Festmachen und an Land gehen" if not str(dock_hint.call()).is_empty() else ""

func create_overlay() -> void:
	title_layer=CanvasLayer.new()
	title_layer.layer=19
	add_child(title_layer)
	titles=Control.new()
	title_layer.add_child(titles)
	titles.mouse_filter=Control.MOUSE_FILTER_IGNORE
	titles.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	titles.hide()
	title_small=game.interface.label(titles,"KAPITEL I",15,Color("#d5a381"),load("res://assets/ui/PlexMono.ttf"))
	title_main=game.interface.label(titles,"Der letzte Funkspruch",55,Color("#ece4ca"),load("res://assets/ui/InstrumentSerif.ttf"))
	title_where=game.interface.label(titles,"NORDKAI  /  STILLWATER",13,Color("#b2b5ab"),load("res://assets/ui/PlexMono.ttf"))
	for pair in [[title_small,0,26],[title_main,26,101],[title_where,103,134]]:
		var label: Label=pair[0]
		label.mouse_filter=Control.MOUSE_FILTER_IGNORE
		game.interface.anchor(label,Vector4(.06,.66,.93,.66),Vector4(0,pair[1],0,pair[2]))
		label.add_theme_color_override("font_outline_color",Color("#1d272e"))
		label.add_theme_constant_override("outline_size",7)

func _input(event: InputEvent) -> void:
	if reveal_clock<0.0:
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("forward"):
		finish_intro(true)

func _process(delta: float) -> void:
	if not is_instance_valid(game) or not game.world.visible:
		if reveal_clock>=0.0:
			finish_intro(false)
		titles.hide()
		return
	var mode:=str(game.game_mode)
	var original_scene: bool=game.arrival.is_open and mode=="play"
	var stage:=int(game.progress.stage)
	var at: Vector3=game.player.global_position
	var chapter:=int(game.current_chapter())
	look_and_lighting(mode,chapter,stage,at)
	var had_boat:=was_at_sea
	if original_scene:
		if not had_boat:
			if not game.arrival.heard and last_mode not in ["journal","pause","settings"]:
				begin_intro()
		tick_intro(delta)
		boats_objective()
	elif reveal_clock>=0.0:
		finish_intro(false)
	if had_boat and not game.arrival.is_open and mode=="play":
		after_dock=0.0
		game.interface.say("Elias","Ich bin am Nordkai. Nora wollte an der Straßensperre auf mich warten.",6.2)
		game.interface.reveal(.86,.56)
	if mode=="play" and not original_scene and stage==0 and after_dock>=0.0:
		after_dock+=delta
		var town_hint: String="Über den Steg an Land. An der Küstenstraße links zur Straßensperre."
		if at.x<8.8:
			town_hint="Folge der Küstenstraße nach Süden und sprich mit Nora an der Sperre."
		game.interface.objective.text=town_hint
	was_at_sea=original_scene
	last_mode=mode

func look_and_lighting(mode: String,chapter: int,stage: int,at: Vector3) -> void:
	if stage>=7 or at.z< -40 and at.x>8.8:
		if not installed.has("chapter2"):
			installed["chapter2"]=art.attach("chapter2",game.world,true)
	if stage>=11 or at.x>52:
		if not installed.has("chapter3"):
			installed["chapter3"]=art.attach("chapter3",game.world,true)
			installed["medic"]=art.attach("rigel_medic",game.world,true)
	if installed.has("medic") and is_instance_valid(installed.medic):
		installed.medic.visible=game.world.rigel.echo
	var env:=ship_env if chapter==3 and at.x>55 else (hill_env if chapter==2 and at.z< -37 else harbor_env)
	game.player.camera.environment=env
	game.menu_camera.environment=ship_env if mode=="finish" and chapter==3 else (hill_env if mode=="finish" and chapter==2 else harbor_env)
	game.world.upper_sky.light_color=Color("#8faebb") if chapter==3 else Color("#a3b8c4")
	game.world.upper_sky.light_energy=.62 if chapter==3 else .79
	installed.reflection.visible=game.arrival.is_open
	installed.reflection.position.y=game.world.water.position.y+.13
	installed.reflection.position.x=31.11
	# The marker belongs to the bow and lights only when the crossing is finished.
	marker.light_energy=1.7 if game.arrival.ready_to_dock() else .0

func begin_intro() -> void:
	if game.preferences.settings.reduced:
		point_at_receiver()
		game.interface.say("Elias","Mara ist seit Jahren verschwunden. Heute Nacht kam eine Nachricht in ihrer Stimme.",5.8)
		return
	reveal_clock=0.0
	opener.make_current()
	titles.show()
	game.interface.reveal(1.36,.91)
	game.interface.say("Elias","Mara ist seit Jahren verschwunden. Heute Nacht kam eine Nachricht in ihrer Stimme.",5.8)
	frame_intro(0.0)

func frame_intro(t: float) -> void:
	var cam: Camera3D=game.player.camera
	var blend:=smoothstep(.07,1.0,t)
	var receiver: Vector3=game.world.targets.intro_receiver.global_position
	var bay:=Vector3(21.0,1.07,-14.59)
	opener.global_position=cam.global_position+Vector3(.39,.31,.35)*(1.0-blend)
	opener.look_at(bay.lerp(receiver,blend*.93))
	opener.fov=lerpf(69.0,cam.fov,blend)
	titles.modulate.a=smoothstep(.055,.33,t)*(1.0-smoothstep(.64,1.0,t))

func tick_intro(delta: float) -> void:
	if reveal_clock<0.0:
		return
	if game.arrival.heard:
		finish_intro(false)
		return
	reveal_clock+=delta
	frame_intro(clampf(reveal_clock/3.25,0.0,1.0))
	if reveal_clock>=3.25:
		finish_intro(true)

func finish_intro(look: bool) -> void:
	reveal_clock=-1.0
	titles.hide()
	if game.arrival.is_open and opener.current:
		if look and game.game_mode=="play":
			point_at_receiver()
		game.player.camera.make_current()

func point_at_receiver() -> void:
	var receiver: Node3D=game.world.targets.intro_receiver
	var player: Node3D=game.player
	var camera: Camera3D=game.player.camera
	var d: Vector3=receiver.global_position-camera.global_position
	player.rotation.y=atan2(-d.x,-d.z)
	camera.rotation.x=atan2(d.y,Vector2(d.x,d.z).length())

func boats_objective() -> void:
	if game.arrival.ready_to_dock():
		game.interface.objective.text="Anleger erreicht. Schau zum beleuchteten Tau am Bug und mache fest."
	elif game.arrival.heard:
		game.interface.objective.text="Das rote Hafenlicht zeigt den Anleger. Hör den Funkspruch zu Ende."
	else:
		game.interface.objective.text="Prüfe Maras Nachricht am beleuchteten Empfänger vor dir."
