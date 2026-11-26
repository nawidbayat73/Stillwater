shader_type spatial;
render_mode cull_disabled;
uniform float movement = 0.7;
varying vec2 world;
void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
	VERTEX.y += 0.09 * movement * sin(world.x * 1.7 + world.y - TIME * 2.0);
}
void fragment() {
	float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 2.5);
	float ripples = sin(world.x * 2.1 + world.y * 1.4 + movement * TIME * 2.5);
	ALBEDO = mix(vec3(.025,.10,.12), vec3(.40,.55,.56), .47*fresnel + .035*ripples);
	ROUGHNESS = .20 + .10 * ripples * movement;
	METALLIC = .19;
	EMISSION = vec3(.017,.043,.05) * (1.0 + fresnel);
}
