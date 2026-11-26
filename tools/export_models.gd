extends SceneTree

func _initialize() -> void:
	call_deferred("export_models")

func export_models() -> void:
	var output := OS.get_cmdline_user_args()
	if output.size()!=1:
		printerr("Pass the target directory after --")
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output[0])
	var game: Node=load("res://main.tscn").instantiate()
	root.add_child(game)
	game.open_late()
	var chapter: Node=game.current
	for entry in [["Gezeitenhoehlen",0,0],["Platform-6",1,0],["Other-Shore",2,0],["Letzte-Flut",3,0],["Resonanzkammer",3,4]]:
		chapter.task=entry[2]
		chapter.build(entry[1])
		var document:=GLTFDocument.new()
		var state:=GLTFState.new()
		var result:=document.append_from_scene(chapter.area,state)
		if result==OK:
			result=document.write_to_filesystem(state,output[0].path_join(entry[0]+".glb"))
		if result!=OK:
			printerr(entry[0]," failed: ",error_string(result))
			quit(1)
			return
		print("Exported ",entry[0])
	quit()
