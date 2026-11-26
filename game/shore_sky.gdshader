shader_type sky;

uniform bool storm = false;

float hash21(vec2 p) {
	return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);
}
float noise(vec2 uv) {
	vec2 i=floor(uv);
	vec2 u=fract(uv);
	u=u*u*(3.0-2.0*u);
	return mix(mix(hash21(i),hash21(i+vec2(1,0)),u.x),
		mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),u.x),u.y);
}
float fBm(vec2 p) {
	return .49*noise(p)+.27*noise(p*2.07+17.3)+.137*noise(p*4.09-3.5)
		+.065*noise(p*8.07+15.4)+.038*noise(p*16.3-19.2);
}
void sky() {
	vec3 ray=normalize(EYEDIR);
	float altitude=max(0.0,ray.y);
	vec3 sun=normalize(vec3(-.65,.26,.46));
	float near_sun=pow(max(dot(ray,sun),0.0),11.0);
	vec3 horizon=storm ? vec3(.22,.32,.35) : vec3(.69,.73,.68);
	vec3 zenith=storm ? vec3(.061,.116,.165) : vec3(.27,.47,.61);
	vec3 colour=mix(horizon,zenith,pow(altitude,.48));
	vec2 uv=ray.xz/(.17+altitude)*vec2(2.4,3.6);
	float soft=fBm(uv*1.2+vec2(3.9,-5.7));
	float cloud=smoothstep(storm ? .37 : .47,storm ? .63 : .68,soft);
	float shore_fade=smoothstep(-.018,.17,altitude);
	vec3 water_heavy=vec3(.135,.208,.267);
	vec3 warm=vec3(.88,.83,.70)+vec3(.17,.088,.015)*near_sun;
	colour=mix(colour,storm? water_heavy : warm,cloud*shore_fade*(storm ? .94 : .76));
	colour+=vec3(.26,.16,.068)*near_sun*(storm ? .19 : .68);
	colour+=vec3(.50,.30,.142)*pow(max(dot(ray,sun),0.0),650.0)*(storm ? .03 : .50);
	COLOR=colour;
}
