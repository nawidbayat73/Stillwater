extends SceneTree
## Capture the shipped waterfront with Godot's normal renderer.

var game: Node
var level: Node
var output: String

func _initialize() -> void:
	call_deferred("run")

func capture(name: String, eye: Vector3, toward: Vector3, fov := 72.0) -> void:
	level.body.position = eye-Vector3.UP*1.57
	level.camera.look_at(level.to_global(toward),Vector3.UP)
	level.camera.fov=fov
	for i in 4:
		await RenderingServer.frame_post_draw
	var result:=root.get_texture().get_image().save_jpg(output.path_join(name+".jpg"),.93)
	print(name,": ",error_string(result))

func run() -> void:
	var args:=OS.get_cmdline_user_args()
	if args.size()!=1:
		quit(1)
		return
	output=args[0]
	DirAccess.make_dir_recursive_absolute(output)
	game=load("res://main.tscn").instantiate()
	root.add_child(game)
	game.open_late()
	level=game.current
	level.task=0
	level.build(2)
	level.layer.hide()
	level.set_physics_process(false)
	level.torch.hide()
	root.size=Vector2i(1440,900)
	await RenderingServer.frame_post_draw
	await capture("01-uferstrasse",Vector3(-30.62,2.12,2.51),Vector3(4,2.55,-5.9))
	await capture("02-haus-ward",Vector3(7.01,1.57,-7.50),Vector3(4.57,1.10,-10.55),78)
	await capture("03-haus-miller",Vector3(-9.69,1.72,-7.46),Vector3(-6.40,1.1,-10.07),74)
	await capture("04-cafe",Vector3(-9.39,1.66,7.88),Vector3(-8.75,1.37,13.20),80)
	await capture("05-netzmacherei",Vector3(-24.26,1.56,-7.66),Vector3(-27.35,1.21,-10.35),74)
	await capture("06-kai",Vector3(-15.71,2.03,-19.4),Vector3(-21.7,1.23,-29.0),75)
	await capture("07-marktseite",Vector3(1.27,2.46,-1.76),Vector3(-12,2.11,7.0),78)
	level.task=3
	level.build(3)
	level.torch.hide()
	await capture("08-letzte-flut",Vector3(6.67,1.77,1.83),Vector3(19.9,2.24,-2.44),73)
	level.returned.emit()
	await process_frame
	quit()
