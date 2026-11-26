shader_type spatial;
render_mode cull_disabled;

uniform float wind=0.24;
uniform bool street=false;
varying vec3 world;

float ripple(vec2 p, float time) {
	return sin(p.x*.67+p.y*.71+time)*.066
		+sin(p.x*.88-p.y*1.29-time*1.49)*.048
		+sin(-p.x*2.2+p.y*2.23+time*1.81)*.018;
}

void vertex() {
	vec3 p=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
	float amp=street ? .42 : .98;
	VERTEX.y+=ripple(p.xz,TIME*1.2)*wind*amp;
	world=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
}

void fragment() {
	vec2 p=world.xz;
	float tx=TIME*1.2;
	float e=.085;
	float h0=ripple(p,tx);
	float amp=wind*(street ? .42 : .98);
	float spectral=sin(p.y*19.0+p.x*8.0+sin(p.x*3.1)+TIME*4.9);
	vec2 small=vec2(spectral*.064,sin(p.y*24.0-p.x*5.7+TIME*4.3)*.071);
	vec3 n=normalize(vec3(amp*(h0-ripple(p+vec2(e,0),tx))/e+small.x*wind,1.0,
		amp*(h0-ripple(p+vec2(0,e),tx))/e+small.y*wind));
	NORMAL=normalize((VIEW_MATRIX*vec4(n,0.0)).xyz);
	float sheen=pow(1.0-max(dot(NORMAL,VIEW),0.0),3.0);
	vec3 deep=street ? vec3(.073,.116,.129) : vec3(.068,.195,.225);
	vec3 light=street ? vec3(.22,.282,.30) : vec3(.38,.48,.49);
	float crest=smoothstep(.083,.131,h0)*wind;
	float foam=street ? 0.0 : crest*exp(-abs(world.z+27.0)*.27)*.67;
	ALBEDO=mix(deep,light,sheen*.86)+vec3(.29,.32,.30)*foam;
	EMISSION=ALBEDO*(.08+.04*sheen);
	ROUGHNESS=.26+spectral*.074;
	METALLIC=.21;
}
