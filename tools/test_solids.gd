extends SceneTree
## Use the same movement inputs as a player, including crossing doors after opening them.

var host: Node
var original: Node
var later: Node
var checks:=0
var failures:=0

func _initialize() -> void:
	call_deferred("run")

func frames(count: int) -> void:
	for i in count:
		await physics_frame

func key(action: StringName, pressed: bool) -> void:
	var event:=InputEventAction.new()
	event.action=action
	event.pressed=pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func expect(ok: bool, details: String) -> void:
	checks+=1
	if ok:
		print("PASS ",details)
	else:
		failures+=1
		printerr("FAIL ",details)

func walk(body: CharacterBody3D,start: Vector3,goal: Vector3,blocked: bool,label: String) -> void:
	var delta:=goal-start
	var forward:=Vector3(delta.x,0,delta.z).normalized()
	var yaw:=atan2(-forward.x,-forward.z)
	if body==original.player:
		original.player.reset(start,yaw,0.0)
	else:
		body.position=start
		body.velocity=Vector3.ZERO
		body.rotation.y=yaw
	await frames(5)
	var actual:=body.position
	key(&"forward",true)
	key(&"sprint",true)
	var traveled:=0.0
	var hit:=false
	for i in 160:
		await physics_frame
		traveled=(body.position-actual).dot(forward)
		for j in body.get_slide_collision_count():
			var normal:=body.get_slide_collision(j).get_normal()
			hit=hit or normal.dot(forward)<-.33
		if traveled>=delta.length()-.15:
			break
	key(&"forward",false)
	key(&"sprint",false)
	await frames(3)
	var intact:=body.position.y>start.y-.9
	var success:=intact and (traveled>.22 and traveled<delta.length()-.18 and hit if blocked else traveled>=delta.length()-.15)
	expect(success,"%s, player moved %.2f m of %.2f m with side contact %s, stopped at %s"%
		[label,traveled,delta.length(),hit,body.position])

func run() -> void:
	host=load("res://main.tscn").instantiate()
	root.add_child(host)
	original=host.original
	original.start_new()
	original.arrival.hear_signal()
	original.arrival.elapsed=16.0
	original.arrival.tick(.01)
	original.arrival.land()
	await frames(8)
	original.set_process(false)
	var player: CharacterBody3D=original.player
	expect(host.coast.models.has("minivan") and host.coast.models.has("cliff_0") and host.coast.models.has("fir_0_distance"),
		"The fitted prop library loaded")
	await walk(player,Vector3(-2.80,.12,7.00),Vector3(-7.05,.12,7.00),true,"I · fisher house wall")
	await walk(player,Vector3(-2.80,.12,8.30),Vector3(-6.34,.12,8.30),true,"I · closed front door")
	original.world.doors.house.set_open(true,true)
	await walk(player,Vector3(-2.80,.12,8.30),Vector3(-6.34,.12,8.30),false,"I · open front door")
	await walk(player,Vector3(-4.39,.12,16.97),Vector3(-4.39,.12,18.49),true,"I · stacked fish crates")
	await walk(player,Vector3(2.64,.12,20.99),Vector3(5.13,.12,20.99),true,"I · delivery van")
	await walk(player,Vector3(-12.93,.12,-37.02),Vector3(-15.81,.12,-37.02),true,"I · coastal boulder")
	await walk(player,Vector3(23.25,.12,-14.34),Vector3(23.25,.12,-11.77),true,"I · pier railing")
	await walk(player,Vector3(40.02,5.43,-52.72),Vector3(40.02,5.43,-55.40),true,"II · keeper’s house wall")
	await walk(player,Vector3(36.62,5.43,-52.92),Vector3(36.62,5.43,-55.21),true,"II · locked keeper door")
	await walk(player,Vector3(67.94,2.62,-25.28),Vector3(70.51,2.62,-25.28),true,"III · RIGEL cargo container")
	await walk(player,Vector3(76.58,5.46,-41.60),Vector3(76.58,5.46,-43.50),true,"III · closed bridge door")
	host.open_late()
	later=host.current
	var walker: CharacterBody3D=later.body
	await frames(9)
	await walk(walker,Vector3(0,.10,7.6),Vector3(0,.10,2.3),true,"IV · closed tide gate")
	later.act("ebb")
	await walk(walker,Vector3(0,.10,6.5),Vector3(0,.10,2.3),false,"IV · open tide gate")
	await walk(walker,Vector3(4.86,.11,-17.04),Vector3(6.79,.11,-17.04),true,"IV · walkway handrail")
	later.task=1
	later.build(1)
	await frames(7)
	await walk(walker,Vector3(0,.10,-4.8),Vector3(0,.10,-10.45),true,"V · collapsed bulkhead in 2026")
	later.act("phase")
	await walk(walker,Vector3(0,.10,-4.8),Vector3(0,.10,-10.45),false,"V · intact passage in 1998")
	await walk(walker,Vector3(-1.45,.10,-1.37),Vector3(-4.30,.10,-1.37),true,"V · laboratory partition")
	later.task=0
	later.build(2)
	await frames(7)
	await walk(walker,Vector3(9.99,.1,-5.66),Vector3(9.99,.1,-8.62),true,"VI · front wall and window of house Ward")
	await walk(walker,Vector3(-20.97,.10,-6.17),Vector3(-22.35,.10,-6.17),true,"VI · curbside freight")
	later.task=3
	later.build(3)
	await frames(9)
	await walk(walker,Vector3(14.68,.10,.16),Vector3(18.78,.10,.16),true,"VII · closed flood barrier")
	later.task=4
	later.build(3)
	await frames(7)
	await walk(walker,Vector3(0,.10,3.20),Vector3(0,.10,-1.84),true,"VII · resonator guardrail")
	print(checks," collision checks, ",failures," failures.")
	quit(1 if failures>0 else 0)
