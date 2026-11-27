shader_type spatial;
render_mode cull_disabled, diffuse_burley;

uniform vec3 deep : source_color = vec3(.112,.252,.294);
uniform vec3 horizon : source_color = vec3(.355,.463,.491);
uniform float tide = .2;
varying vec2 water_position;
varying vec3 wave_normal;

float hash21(vec2 v) {
	return fract(sin(dot(v,vec2(112.31,362.86)))*42663.9);
}

float noise2(vec2 v) {
	vec2 cell=floor(v), f=smoothstep(vec2(0.0),vec2(1.0),fract(v));
	return mix(mix(hash21(cell),hash21(cell+vec2(1,0)),f.x),
		mix(hash21(cell+vec2(0,1)),hash21(cell+vec2(1)),f.x),f.y);
}

float surface(vec2 p) {
	return sin(dot(p,vec2(1.07,.64))+TIME*1.27)*.065
		+sin(dot(p,vec2(.53,-1.45))-TIME*1.71)*.037
		+sin(dot(p,vec2(2.20,.31))+TIME*2.3)*.016;
}

void vertex() {
	water_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;
	float height=surface(water_position);
	VERTEX.y+=height;
	vec2 d=vec2(.05,0.0);
	wave_normal=normalize(vec3(height-surface(water_position+d),.05,height-surface(water_position+d.yx)));
}

void fragment() {
	vec2 q=water_position;
	// The bilge has a separate surface on the same tide cycle.
	if (q.x>68.0 && q.x<81.42 && q.y>-51.96 && q.y<-11.70) {
		discard;
	}
	float gust=noise2(q*vec2(2.33,5.37)+vec2(TIME*.60,-TIME*.48));
	float rib=sin(7.5*q.x+11.9*q.y+gust*3.1-TIME*6.1)*.016;
	vec3 n=normalize(wave_normal+vec3(rib,0.0,(gust-.52)*.11));
	NORMAL=normalize((VIEW_MATRIX*vec4(n,0.0)).xyz);
	float sheen=pow(1.0-max(dot(NORMAL,VIEW),0.0),3.0);
	float coast=19.25+sin(q.y*.16)*.39-max(0.0,-q.y-36.0)*.33;
	float cliff=abs(length((q-vec2(43.0,-54.08))/vec2(11.55,8.16))-1.0)*8.16;
	float shore=min(abs(q.x-coast),cliff);
	float surge=sin((q.x-coast)*3.8-TIME*2.2+noise2(q*.77)*2.21);
	float foam=smoothstep(.55,.92,surge+noise2(q*2.4)*.31);
	foam*=1.0-smoothstep(.03,1.80+clamp(tide,0.0,.4),shore);
	vec3 colour=mix(deep,horizon,sheen*.72);
	colour=mix(colour,vec3(.48,.55,.53),foam*(.22+noise2(q*15.0)*.32));
	ALBEDO=colour*(.90+gust*.18);
	EMISSION=colour*(.07+sheen*.15);
	METALLIC=.06;
	ROUGHNESS=.33+gust*.25;
	SPECULAR=.35;
}
