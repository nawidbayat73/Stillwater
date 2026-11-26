extends SceneTree
var game: Node
var late: Node

func _initialize() -> void:
	call_deferred("run")

func assert_ok(ok: bool, details: String) -> void:
	if not ok:
		printerr("FAILED ",details)
		quit(1)
	assert(ok,details)
	print("PASS ",details)

func frames(n: int) -> void:
	for i in n:
		await physics_frame

func run() -> void:
	game=load("res://main.tscn").instantiate()
	root.add_child(game)
	await frames(8)
	assert_ok(is_instance_valid(game.offer),"entry button on original home screen")
	game.original.command("credits")
	await frames(3)
	var credit:=false
	for item in game.original.interface.overlay.find_children("*","Label",true,false):
		credit=credit or item.text.contains("ECHØ CEO Nawid")
	assert_ok(credit,"attribution in original credits")
	game.open_late()
	late=game.current
	await frames(8)
	assert_ok(late.chapter==0 and late.area.get_child_count()>150,"caves built")
	assert_ok(late.body.is_on_floor(),"player stands on cave floor")
	late.act("ebb")
	late.act("cave_spool")
	late.act("pump")
	assert_ok(late.task==1,"pump rejects wrong order")
	late.act("inlet")
	late.act("bypass")
	late.act("pump")
	late.act("receiver")
	await frames(195)
	assert_ok(late.task==3 and late.scene_data.shutter.position.y<1.4,"Drowned closes floodgate")
	late.act("cave_end")
	late.act("coupler")
	late.act("phase")
	assert_ok(late.chapter==1 and late.past and late.scene_data.rubble.position.y>4,"phase changes physical passage")
	late.act("server_spool")
	late.act("archive")
	await frames(545)
	assert_ok(late.task==2,"archived cutscene completes")
	late.act("station_end")
	assert_ok(late.chapter==1,"exit requires the current reality")
	late.act("phase")
	late.act("station_end")
	var town: Node = late.area.get_node("Uferstrasse")
	assert_ok(late.chapter==2 and town.find_child("Ward",true,false)!=null and town.find_child("Cafe",true,false)!=null,
		"new waterfront and its furnished buildings loaded")
	for id in ["log","photo","family","bell"]:
		late.act(id)
	for i in 6: late.act("mara")
	assert_ok(late.chapter==3 and late.task==0,"Mara concludes and opens final chapter")
	late.act("post")
	late.act("ward")
	late.act("clock")
	assert_ok(late.task==3 and late.scene_data.guard.visible,"flood and roadblock activate")
	late.body.position=Vector3(7,.10,-16)
	await frames(3)
	late.act("tower")
	assert_ok(late.task==4 and late.scene_data.has("outer_ring"),"reactor chamber")
	late.act("first")
	assert_ok(not is_instance_valid(late.panel),"null channel rejects wrong digits")
	for i in 3:
		for j in [3,1,6][i]: late.act("digit"+str(i))
	for id in ["first","last","rising"]:
		late.act(id)
		assert_ok(is_instance_valid(late.panel),"decision "+id)
		late.dismiss()
		late.epilogue(id)
		late.dismiss()
		assert_ok(late.finds.get("ending_"+id,false),"epilogue "+id)
	quit()
