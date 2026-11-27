shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled;

uniform vec3 ember : source_color=vec3(.95,.36,.25);
uniform float power=.22;

void fragment(){
	float spread=pow(max(0.0,1.0-abs(UV.x*2.0-1.0)),2.4);
	float end_fade=smoothstep(0.0,.20,UV.y)*pow(1.0-smoothstep(.32,1.0,UV.y),1.8);
	ALBEDO=ember;
	ALPHA=spread*end_fade*power;
}
