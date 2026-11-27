extends SceneTree
## Verify the opening using the actual receiver, mooring target and walking controls.

var host: Node
var game: Node

func _initialize() -> void:
	call_deferred("run")

func frames(n: int) -> void:
	for i in n:
		await physics_frame

func expect(ok: bool, name: String) -> bool:
	if ok:
		print("PASS ",name)
	else:
		printerr("FAIL ",name," / ",game.player.global_position," / ",game.interface.objective.text)
		quit(1)
	return ok

func input(action: StringName, pressed: bool) -> void:
	var event:=InputEventAction.new()
	event.action=action
	event.pressed=pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func target() -> String:
	var current: Area3D=game.player.current_target()
	return current.action_id if is_instance_valid(current) else ""

func aim(point: Vector3) -> void:
	var offset: Vector3=point-game.player.camera.global_position
	game.player.rotation.y=atan2(-offset.x,-offset.z)
	game.player.camera.rotation.x=atan2(offset.y,Vector2(offset.x,offset.z).length())

func walk(destination: Vector2) -> bool:
	game.player.camera.rotation.x=0.0
	input(&"forward",true)
	for i in 1200:
		var at: Vector3=game.player.global_position
		var distance:=destination-Vector2(at.x,at.z)
		if distance.length()<.20:
			input(&"forward",false)
			await frames(3)
			return true
		game.player.rotation.y=atan2(-distance.x,-distance.y)
		await physics_frame
	input(&"forward",false)
	return false

func run() -> void:
	host=load("res://main.tscn").instantiate()
	root.add_child(host)
	game=host.original
	game.start_new()
	await frames(10)
	if not expect(host.direction.opener.current,"The story starts with the harbor view"): return
	await frames(200)
	if not expect(game.player.camera.current and target()=="intro_receiver","Control returns with the receiver under the reticle (hit "+target()+")"): return
	if not expect("Empfänger" in game.interface.objective.text,"The first objective names the receiver"): return
	input(&"interact",true)
	await frames(2)
	input(&"interact",false)
	if not expect(game.arrival.heard,"The player's interact input starts Mara’s message"): return
	await frames(965)
	if not expect(game.arrival.ready_to_dock(),"The crossing arrives at the lit pier"): return
	aim(game.world.targets.intro_dock.global_position)
	await frames(3)
	if not expect(target()=="intro_dock","The bow rope is in interaction range (hit "+target()+")"): return
	input(&"interact",true)
	await frames(2)
	input(&"interact",false)
	if not expect(not game.arrival.is_open and "Straßensperre" in game.interface.objective.text,"Disembarkation places Elias on the pier and points to Nora"): return
	for point in [Vector2(18.85,-14.42),Vector2(18.76,-15.15),Vector2(15.44,-15.15),Vector2(6.02,-15.15),
			Vector2(1.34,-15.10),Vector2(1.24,8.07),Vector2(1.86,17.82)]:
		if not expect(await walk(point),"Walk toward Nora via "+str(point)): return
	aim(game.world.targets.mira_talk.global_position)
	await frames(3)
	if not expect(target()=="mira_talk","Nora can be reached on foot from the boat (hit "+target()+")"): return
	input(&"interact",true)
	await frames(3)
	input(&"interact",false)
	if not expect(int(game.progress.stage)>0 or game.game_mode!="play" or game.interface.subtitle_panel.visible,"Interact starts the scene with Nora"): return
	quit()
