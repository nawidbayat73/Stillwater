extends RefCounted
## Load the authored waterfront meshes while keeping the same chapter interactions.

const DIRECTORY := "res://scenery/"
const SKY := preload("res://shore_sky.gdshader")
const WATER := preload("res://shore_water.gdshader")

var models := {}
var layouts := {}

func load_set(id: String) -> bool:
	if models.has(id):
		return true
	var state := GLTFState.new()
	var document := GLTFDocument.new()
	var code := document.append_from_file(DIRECTORY+id+".glb",state)
	if code != OK:
		push_error("Stillwater: "+id+" konnte nicht geladen werden: "+error_string(code))
		return false
	var model := document.generate_scene(state,0,false,true)
	if model == null:
		return false
	var layout: Variant = JSON.parse_string(FileAccess.get_file_as_string(DIRECTORY+id+".json"))
	if not layout is Dictionary:
		model.free()
		push_error("Stillwater: Layout fehlt für "+id)
		return false
	var scene := PackedScene.new()
	var result := scene.pack(model)
	model.free()
	if result != OK:
		push_error("Stillwater: Szene konnte nicht gespeichert werden: "+error_string(result))
		return false
	models[id]=scene
	layouts[id]=layout
	return true

func attach(id: String, area: Node3D, night: bool) -> Node3D:
	if not load_set(id):
		return null
	var model: Node3D = models[id].instantiate()
	model.name="Sturm" if id=="sturm" else "Uferstrasse"
	area.add_child(model)
	var layout: Dictionary=layouts[id]
	add_colliders(model,layout.colliders)
	for recipe: Array in layout.lamps:
		var fixture:=OmniLight3D.new()
		fixture.position=Vector3(recipe[0],recipe[1],recipe[2])
		fixture.light_color=Color(recipe[3])
		fixture.light_energy=float(recipe[4])*(.92 if night else .62)
		fixture.omni_range=recipe[5]
		fixture.omni_attenuation=1.24
		fixture.shadow_enabled=recipe[6]
		fixture.distance_fade_enabled=true
		fixture.distance_fade_begin=17.0
		fixture.distance_fade_length=8.0
		fixture.distance_fade_shadow=10.0
		fixture.shadow_bias=.10
		fixture.shadow_normal_bias=.82
		model.add_child(fixture)
	return model

func add_colliders(model: Node3D, recipes: Array) -> void:
	var static_body:=StaticBody3D.new()
	static_body.name="Kollision"
	static_body.collision_layer=1
	static_body.collision_mask=0
	model.add_child(static_body)
	for recipe: Array in recipes:
		var volume:=BoxShape3D.new()
		volume.size=Vector3(recipe[3],recipe[4],recipe[5])
		var hit:=CollisionShape3D.new()
		hit.shape=volume
		hit.position=Vector3(recipe[0],recipe[1],recipe[2])
		hit.rotation.y=float(recipe[6])
		static_body.add_child(hit)

func point_at(id: String, marker: String) -> Vector3:
	var xyz: Array = layouts[id].anchors[marker]
	return Vector3(xyz[0],xyz[1],xyz[2])

func atmosphere(storm: bool) -> Environment:
	var result:=Environment.new()
	var dome:=Sky.new()
	dome.radiance_size=Sky.RADIANCE_SIZE_64
	var material:=ShaderMaterial.new()
	material.shader=SKY
	material.set_shader_parameter("storm",storm)
	dome.sky_material=material
	result.sky=dome
	result.background_mode=Environment.BG_SKY
	result.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	result.reflected_light_source=Environment.REFLECTION_SOURCE_DISABLED
	result.ambient_light_color=Color("#a4bac2") if storm else Color("#d0d8d4")
	result.ambient_light_energy=.47 if storm else .60
	result.fog_enabled=true
	result.fog_light_color=Color("#4b6370") if storm else Color("#b1b9a9")
	result.fog_light_energy=.86
	result.fog_density=.017 if storm else .0047
	result.fog_sky_affect=.10
	result.adjustment_enabled=true
	result.adjustment_brightness=.97 if storm else .99
	result.adjustment_contrast=1.055
	result.adjustment_saturation=.85 if storm else .96
	return result

func water(parent: Node3D, at: Vector3, size: Vector2, storm: bool, street := false) -> MeshInstance3D:
	var node:=MeshInstance3D.new()
	var mesh:=PlaneMesh.new()
	mesh.size=size
	mesh.subdivide_width=90 if street else 110
	mesh.subdivide_depth=24 if street else 45
	node.mesh=mesh
	var material:=ShaderMaterial.new()
	material.shader=WATER
	material.set_shader_parameter("wind",1.0 if storm else .24)
	material.set_shader_parameter("street",street)
	node.material_override=material
	node.position=at
	parent.add_child(node)
	return node

func play_loop(parent: Node3D, track: String, at: Vector3, volume: float) -> void:
	var path := "res://assets/audio/"+track+".ogg"
	if not ResourceLoader.exists(path):
		return
	var player:=AudioStreamPlayer3D.new()
	var sound:=load(path).duplicate() as AudioStreamOggVorbis
	if sound==null:
		player.free()
		return
	sound.loop=true
	player.stream=sound
	player.position=at
	player.unit_size=15
	player.max_distance=69
	player.volume_db=volume
	parent.add_child(player)
	player.play()
