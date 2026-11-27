extends RefCounted
## Replace the original coast props in place, keeping their routes and attached interactions.

const Artwork=preload("res://shore_art.gd")
const ROCKS: Dictionary={
	"cliff_0":"cliff_0", "cliff_1":"cliff_1", "cliff_2":"cliff_2",
	"bc_shelter_rock_0":"cliff_0", "bc_shelter_rock_1":"cliff_1", "bc_shelter_rock_2":"cliff_2",
}
const PROPS_WITH_BODIES: Array[String]=[
	"bc_diesel","bc_drive_box","bc_console","bc_path_marker","sign_stand","street_lamp","power_pole",
	"cabinet","cable_cabinet","radio_console","harbor_crane","barrel","bc_oil_drum","crate",
	"pallet","rope_reel","bollard","fish_boxes","container","fence","rail","minivan",
]
const PROFILE: Dictionary={
	"wood":["timber","#9b805e",.91,.72], "paint_blue":["siding","#688590",.56,.78],
	"paint_cream":["siding","#d5c6a8",.56,.78], "paint_red":["siding","#914e3e",.56,.83],
	"zinc":["corrugated","#7c8a8c",.47,.58], "rust":["metal","#966c57",.67,.67],
	"concrete":["plaster","#8f9290",.49,.91], "plaster":["plaster","#c4b9a0",.43,.91],
	"stone":["stone","#7a7965",.37,.88], "basalt":["stone","#5e6a67",.35,.82],
	"earth":["sand","#7b7865",.45,.93], "gravel":["sand","#999380",.70,.92],
	"asphalt":["road","#535957",.24,.84], "cloth":["leather","#a49b80",1.10,.87],
	"cliff_lime":["brick","#ddd1b9",.43,.87], "cliff_rust":["metal","#934f41",.58,.67],
	"steel":["metal","#8a9795",.75,.57], "bronze":["metal","#977c56",.65,.61],
	"oxide":["metal","#86594b",.51,.67], "ship_panel":["metal","#58736f",.43,.61],
	"ship_wall":["metal","#a2a9a1",.35,.64], "ship_deck":["metal","#646f6e",.60,.62],
}

var art:=Artwork.new()
var models: Dictionary={}
var photos: Dictionary={}
var materials: Dictionary={}
var rock_points: Dictionary={}

func install(world: Node3D) -> void:
	if art.load_set("coastal_props"):
		var library: PackedScene=art.models["coastal_props"]
		var contents:=library.instantiate()
		for view: MeshInstance3D in contents.find_children("*","MeshInstance3D",true,false):
			models[str(view.name)]=view.mesh
		contents.free()
	var mesh_ids: Dictionary={}
	for id: String in world.meshes:
		var mesh: Mesh=world.meshes[id]
		mesh_ids[mesh]=id
		refinish(mesh,id)
	for view: MeshInstance3D in world.find_children("*","MeshInstance3D",true,false):
		var id: String=mesh_ids.get(view.mesh,"")
		if not id.is_empty():
			apply_to(view,id,id!="rv_launch")
	art.attach("coastal_street",world,true)

func apply_to(view: MeshInstance3D,id: String,solid: bool) -> void:
	var old:=view.get_aabb()
	var local:=view.transform
	var parent:=view.get_parent() as Node3D
	var replacement: Mesh=models.get(ROCKS.get(id,id))
	if replacement:
		fit(view,replacement,old,local)
	if not solid:
		return
	if id.begins_with("fir_") and replacement:
		var far:=MeshInstance3D.new()
		parent.add_child(far)
		fit(far,models[id+"_distance"],old,local)
		far.visibility_range_begin=32.0
		view.visibility_range_end=32.0
		var trunk:=CylinderShape3D.new()
		trunk.radius=.28
		trunk.height=2.92
		# Recover the actual trunk centre after fitting the irregular crown to the old footprint.
		add_body(parent,trunk,Transform3D(Basis.IDENTITY,view.transform*Vector3(0,1.46,0)))
	elif ROCKS.has(id) and replacement:
		if not rock_points.has(replacement):
			var extracted:=replacement.create_convex_shape(true,true)
			rock_points[replacement]=extracted.points if extracted else PackedVector3Array()
		var points: PackedVector3Array=rock_points[replacement].duplicate()
		if not points.is_empty():
			for i in points.size():
				points[i]=view.transform*points[i]
			var hull:=ConvexPolygonShape3D.new()
			hull.points=points
			var original_body:=collision_body(parent)
			if original_body:
				original_body.collision_layer=0
			add_body(parent,hull,Transform3D.IDENTITY)
	elif id=="trawler" and replacement:
		add_box(parent,AABB(Vector3(-1.19,.64,-2.54),Vector3(2.38,1.77,2.53)),view.transform)
		add_box(parent,AABB(Vector3(-1.42,.06,-3.76),Vector3(2.84,.67,6.48)),view.transform)
	elif id in PROPS_WITH_BODIES and not collision_body(parent):
		var area:=old
		if id in ["street_lamp","power_pole","sign_stand"]:
			# Only the upright posts reach the ground under the light or the sign.
			area=AABB(Vector3(-.14,0,-.14),Vector3(.28,minf(old.size.y,2.2),.28))
		add_box(parent,area,local)

func fit(view: MeshInstance3D,replacement: Mesh,old: AABB,local: Transform3D) -> void:
	var bounds:=replacement.get_aabb()
	var resize: Vector3=old.size/bounds.size
	view.transform=local*Transform3D(Basis.from_scale(resize),old.position-bounds.position*resize)
	view.mesh=replacement

func collision_body(parent: Node3D) -> StaticBody3D:
	for node in parent.get_children():
		if node is StaticBody3D and node.collision_layer&1:
			return node
	return null

func add_box(parent: Node3D,bounds: AABB,local: Transform3D) -> void:
	var volume:=BoxShape3D.new()
	volume.size=bounds.size.max(Vector3(.072,.072,.072))*local.basis.get_scale().abs()
	add_body(parent,volume,Transform3D(local.basis.orthonormalized(),local*bounds.get_center()))

func add_body(parent: Node3D,shape: Shape3D,at: Transform3D) -> void:
	var obstacle:=StaticBody3D.new()
	obstacle.name="SolidProp"
	obstacle.collision_layer=1
	obstacle.collision_mask=0
	parent.add_child(obstacle)
	var hit:=CollisionShape3D.new()
	hit.transform=at
	hit.shape=shape
	obstacle.add_child(hit)

func photograph(id: String) -> Texture2D:
	if not photos.has(id):
		var image:=Image.load_from_file("res://finish/"+id+".jpg")
		if image==null or image.is_empty():
			return null
		image.generate_mipmaps(id.ends_with("_n"))
		photos[id]=ImageTexture.create_from_image(image)
	return photos[id]

func dress_figure(actor: Node3D) -> void:
	for view: MeshInstance3D in actor.find_children("*","MeshInstance3D",true,false):
		for i in view.mesh.get_surface_count():
			var fabric:=view.get_active_material(i) as StandardMaterial3D
			if not fabric or fabric.resource_name not in ["cloth","slicker","rubber","moss","skin"]:
				continue
			var key: Array=[fabric.resource_name,fabric.albedo_color,fabric.roughness,fabric.metallic]
			if not materials.has(key):
				var coating:=fabric.duplicate() as StandardMaterial3D
				var surface: String="leather" if fabric.resource_name in ["cloth","slicker","rubber"] else "bark"
				coating.albedo_texture=photograph(surface)
				coating.normal_texture=photograph(surface+"_n")
				coating.normal_enabled=true
				coating.normal_scale=.31 if surface=="leather" else .53
				coating.uv1_scale=Vector3(2.0,2.0,1.0)
				materials[key]=coating
			view.set_surface_override_material(i,materials[key])

func refinish(mesh: Mesh,id: String) -> void:
	for index in mesh.get_surface_count():
		var source:=mesh.surface_get_material(index) as StandardMaterial3D
		if not source:
			continue
		var name:=source.resource_name
		if not PROFILE.has(name):
			continue
		var settings: Array=PROFILE[name]
		var key:=str(source.get_instance_id())
		# Deck paint uses a weathered steel photograph. Keep trim distinct from the tower masonry.
		if id.begins_with("rv_") and name in ["paint_blue","paint_cream","paint_red"]:
			key+="_marine"
			settings=["metal",settings[1],.52,.70]
		if not materials.has(key):
			var albedo:=photograph(settings[0])
			var normal:=photograph(settings[0]+"_n")
			if not albedo or not normal:
				continue
			var finish:=source.duplicate() as StandardMaterial3D
			finish.albedo_color=Color(settings[1])
			finish.albedo_texture=albedo
			# The original kit already has meter-scale unwraps. Keep their directional grain.
			var repeat:=1.55*float(settings[2])
			finish.uv1_scale=Vector3(repeat,repeat,1.0)
			finish.normal_enabled=true
			finish.normal_texture=normal
			finish.normal_scale=.46 if settings[0] in ["plaster","metal"] else .67
			finish.roughness=settings[3]
			finish.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
			materials[key]=finish
		mesh.surface_set_material(index,materials[key])
