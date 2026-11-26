extends SceneTree
## Walk the furnished streets and trigger the chapter through the player's real input.

var game: Node
var level: Node
var count := 0
var failed := false

func _initialize() -> void:
	call_deferred("run")

func frames(n: int) -> void:
	for i in n:
		await physics_frame

func expect(ok: bool, what: String) -> bool:
	count+=1
	if ok:
		print("PASS ",what)
	else:
		failed=true
		printerr("FAIL ",what)
	return ok

func key(code: int, pressed: bool) -> void:
	var event:=InputEventKey.new()
	event.physical_keycode=code
	event.pressed=pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func walk(goal: Vector2, max_frames := 1150) -> bool:
	key(KEY_W,true)
	key(KEY_SHIFT,true)
	level.camera.rotation.x=0
	var reached:=false
	for i in max_frames:
		var pos: Vector3=level.body.position
		var delta:=goal-Vector2(pos.x,pos.z)
		if delta.length()<.19:
			reached=true
			break
		level.body.rotation.y=atan2(-delta.x,-delta.y)
		await physics_frame
	key(KEY_W,false)
	key(KEY_SHIFT,false)
	await frames(4)
	if not reached:
		printerr("Stopped at ",level.body.position," trying to reach ",goal)
	return reached

func route(name: String, points: Array) -> bool:
	for target: Vector2 in points:
		if not await walk(target):
			return expect(false,name)
	return expect(true,name)

func use(marker: String, target: Vector3) -> bool:
	level.camera.look_at(level.to_global(target),Vector3.UP)
	await frames(5)
	if not expect(level.aim==marker,"Aim at "+marker+" (hit "+level.aim+")"):
		return false
	key(KEY_E,true)
	await frames(3)
	key(KEY_E,false)
	return true

func visit(marker: String, points: Array) -> bool:
	if not await route("Reach "+marker,points):
		return false
	return await use(marker,level.shore_art.point_at("ufer",marker))

func go_shore() -> bool:
	if not await visit("log",[Vector2(-25,.35),Vector2(-25,-8.61),Vector2(-25.38,-9.15)]): return false
	if not await visit("photo",[Vector2(-25,-8.12),Vector2(-25,-4.48),Vector2(-9,-4.48),Vector2(-9,-8.70),Vector2(-9.55,-9.16)]): return false
	if not await visit("family",[Vector2(-9,-8.12),Vector2(-9,-4.42),Vector2(7,-4.42),Vector2(7,-8.48),Vector2(7,-9.62)]): return false
	if not await visit("bell",[Vector2(7,-8.08),Vector2(7,-3.42),Vector2(7,8.60),Vector2(7.28,9.12)]): return false
	if not expect(level.shore_count()==3 and level.finds.get("bell",false),"All three memories and the library recording collected"): return false
	if not await route("Enter café",[Vector2(7,8.02),Vector2(7,4.46),Vector2(-9,4.46),Vector2(-9,8.84),Vector2(-9.20,9.95)]): return false
	var talk: Vector3=level.shore_art.point_at("ufer","mara")+Vector3(0,1,-.32)
	for line in 6:
		if not await use("mara",talk): return false
	return expect(level.chapter==3 and level.task==0,"The café conversation leads to the storm")

func go_storm() -> bool:
	for row in [
		["post",[Vector2(-25,1.48),Vector2(-25,3.88)]],
		["ward",[Vector2(-25,.25),Vector2(8.92,.25),Vector2(8.92,-3.85)]],
		["clock",[Vector2(8.92,-3.38),Vector2(25,-3.38),Vector2(25,-4.02)]],
	]:
		var marker: String=row[0]
		if not await route("Reach relay "+marker,row[1]): return false
		if not await use(marker,level.shore_art.point_at("sturm",marker)): return false
	if not expect(level.task==3 and level.scene_data.roadblock.position.y>0,"Relays shut the flood barrier"): return false
	if not await route("Walk through Ward and out its rear door",[
		Vector2(23.38,-4.0),Vector2(22.87,-6.46),Vector2(14.10,-6.45),Vector2(13.59,-4.90),
		Vector2(9.97,-4.87),Vector2(7.25,-4.96),Vector2(7,-8.02),
		Vector2(7,-10.5),Vector2(7,-13.18),Vector2(7,-16.22)]): return false
	if not expect(level.escaped_ward,"The rear exit is recognised"): return false
	if not await route("Walk to the tower along the quay",[Vector2(7,-17.12),Vector2(23.06,-17.15),Vector2(25,-17.03)]): return false
	if not await use("tower",level.shore_art.point_at("sturm","tower")): return false
	return expect(level.task==4 and level.scene_data.has("outer_ring"),"The route reaches the lighthouse")

func run() -> void:
	game=load("res://main.tscn").instantiate()
	root.add_child(game)
	game.open_late()
	level=game.current
	level.task=0
	level.build(2)
	await frames(9)
	if not await go_shore() or not await go_storm():
		quit(1)
		return
	level.task=0
	level.build(2)
	level.body.position=Vector3(-20.34,.12,-20.0)
	await frames(8)
	await route("The west pier is walkable",[Vector2(-20.34,-23.38),Vector2(-20.34,-26.95)])
	expect(level.body.is_on_floor(),"The pier has continuous collision")
	print(count," waterfront checks.")
	quit(1 if failed else 0)
