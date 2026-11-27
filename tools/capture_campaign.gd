extends SceneTree
## Capture the actual executable at the entrance, chapter landmarks, and before the final choice.

var game: Node
var original: Node
var late: Node
var review_camera: Camera3D
var directory: String

func _initialize() -> void:
	call_deferred("run")

func shot(name: String, frames := 3) -> void:
	for i in frames:
		await RenderingServer.frame_post_draw
	var result:=root.get_texture().get_image().save_jpg(directory.path_join(name+".jpg"),.93)
	if result!=OK:
		printerr(name," ",error_string(result))
	else:
		print(name)

func original_view(name: String, eye: Vector3, target: Vector3, env: Environment, fov := 70.0) -> void:
	review_camera.environment=env
	review_camera.global_position=eye
	review_camera.look_at(target)
	review_camera.fov=fov
	review_camera.make_current()
	await shot(name)

func later_view(name: String, eye: Vector3, target: Vector3, fov := 70.0, torch := false) -> void:
	late.body.position=eye-Vector3.UP*1.57
	late.camera.look_at(late.to_global(target))
	late.camera.fov=fov
	late.torch.visible=torch
	await shot(name)

func run() -> void:
	var args:=OS.get_cmdline_user_args()
	if args.size()!=1:
		quit(1)
		return
	directory=args[0]
	DirAccess.make_dir_recursive_absolute(directory)
	root.size=Vector2i(1280,800)
	game=load("res://main.tscn").instantiate()
	root.add_child(game)
	original=game.original
	original.start_new()
	original.interface.fade.color.a=0.0
	for i in 23: await RenderingServer.frame_post_draw
	await shot("00-kapitelbeginn")
	game.direction.reveal_clock=-1.0
	original.interface.hide()
	game.direction.titles.hide()
	game.direction.look_and_lighting("play",1,0,Vector3(43,0,-14.59))
	review_camera=Camera3D.new()
	root.add_child(review_camera)
	await original_view("01-auf-see",Vector3(43.19,1.48,-14.36),Vector3(23,.14,-14.91),game.direction.harbor_env,67)
	game.direction.point_at_receiver()
	var radio: Vector3=original.world.targets.intro_receiver.global_position
	await original_view("02-empfaenger",original.player.camera.global_position+Vector3(.18,-.13,.12),radio,game.direction.harbor_env,59)
	original.arrival.hear_signal()
	original.arrival.elapsed=15.1
	original.arrival.tick(.01)
	original.arrival.land()
	await original_view("03-landgang",Vector3(25.32,2.01,-14.14),Vector3(16.05,.86,-14.35),game.direction.harbor_env,76)
	await original_view("04-kuestenstrasse",Vector3(1.63,1.91,12.90),Vector3(-5.15,1.29,6.78),game.direction.harbor_env)
	game.direction.look_and_lighting("play",2,10,Vector3(28,1,-49.0))
	await original_view("05-blackcliff",Vector3(30.38,9.45,-44.60),Vector3(43.72,9.21,-53.67),game.direction.hill_env,66)
	await original_view("06-funkwarte",Vector3(50.71,2.54,-33.92),Vector3(52.29,2.01,-35.40),game.direction.hill_env,76)
	game.direction.look_and_lighting("play",3,13,Vector3(70,4,-44))
	await original_view("07-rigel",Vector3(57.26,4.19,-31.3),Vector3(75.0,4.44,-36.5),game.direction.ship_env,76)
	await original_view("08-bruecke",Vector3(75.18,6.96,-43.51),Vector3(74.02,6.54,-48.05),game.direction.ship_env,85)
	await original_view("09-laderaum",Vector3(73.47,1.67,-18.74),Vector3(75.38,1.15,-14.60),game.direction.ship_env,70)
	game.open_late()
	late=game.current
	late.layer.hide()
	late.set_physics_process(false)
	late.task=1
	late.build(0)
	await later_view("10-gezeitenstollen",Vector3(2.02,1.79,-4.89),Vector3(-.63,1.65,-19.2),75,true)
	late.task=0
	late.build(1)
	await later_view("11-platform6",Vector3(-.43,1.57,8.97),Vector3(.68,1.62,-8.07),73)
	await later_view("12-biologielabor",Vector3(-4.08,1.69,-2.50),Vector3(-6.35,1.16,-6.32),77)
	late.task=1
	late.act("phase")
	late.act("archive")
	late.layer.show()
	await create_timer(2.0).timeout
	await shot("13-archiv-1998",4)
	await create_timer(6.6).timeout
	late.layer.hide()
	late.task=0
	late.build(2)
	await later_view("14-andere-kueste",Vector3(-30.62,2.06,2.51),Vector3(4,2.55,-5.9),72)
	await later_view("15-haus-ward",Vector3(7.01,1.57,-7.50),Vector3(4.57,1.10,-10.55),78)
	await later_view("16-cafe",Vector3(-9.39,1.66,7.88),Vector3(-8.75,1.37,13.20),79)
	late.task=3
	late.build(3)
	late.clock=23.5
	late.surge=29.0
	await later_view("17-die-letzte-flut",Vector3(6.67,1.77,1.83),Vector3(19.9,2.24,-2.44),75,true)
	late.task=4
	late.build(3)
	await later_view("18-resonanzkammer",Vector3(-1.85,1.70,6.26),Vector3(.25,2.27,-2.15),75)
	for ending in ["last","rising","first"]:
		late.epilogue(ending)
		late.update_ending(3.8)
		await shot("19-ending-"+ending)
		late.dismiss()
	game.queue_free()
	await process_frame
	quit()
