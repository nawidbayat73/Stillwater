extends Node

const LATE = preload("res://after_rigel.gd")
var original
var current
var menu_stamp: String
var offer: Button
var last_overlay: Control

func _ready() -> void:
	original = $Original

func _process(_delta: float) -> void:
	if is_instance_valid(current):
		return
	var ui = original.interface
	if not is_instance_valid(ui.overlay):
		return
	if last_overlay == ui.overlay and menu_stamp == original.game_mode and is_instance_valid(offer):
		return
	last_overlay = ui.overlay
	menu_stamp = original.game_mode
	for item in ui.overlay.find_children("*","Label",true,false):
		if "Sounddesign" in item.text:
			item.text = item.text.replace("Codex","ECHØ CEO Nawid")
	if menu_stamp == "menu" or (menu_stamp == "finish" and original.current_chapter()==3):
		offer = Button.new()
		offer.text = "Kapitel IV–VII · Nach der RIGEL" if menu_stamp == "menu" else "Kapitel IV beginnen"
		offer.theme = ui.root.theme
		ui.overlay.add_child(offer)
		offer.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
		offer.offset_left = -345
		offer.offset_right = -36
		offer.offset_top = -112
		offer.offset_bottom = -69
		offer.pressed.connect(open_late)

func open_late() -> void:
	current = LATE.new()
	current.base = original
	current.position.x = 420.0
	original.process_mode = Node.PROCESS_MODE_DISABLED
	original.world.hide()
	original.interface.hide()
	if original.audio.dialogue:
		original.audio.dialogue.stop()
	add_child(current)
	current.returned.connect(close_late)

func close_late() -> void:
	current.queue_free()
	current = null
	original.world.show()
	original.interface.show()
	original.process_mode = Node.PROCESS_MODE_INHERIT
	original.show_menu()
