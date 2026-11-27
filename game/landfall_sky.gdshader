shader_type sky;

float hash2(vec2 p) {
	vec3 q=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973));
	q+=dot(q,q.yzx+33.33);
	return fract((q.x+q.y)*q.z);
}
float cloud(vec2 q) {
	vec2 p=floor(q);
	vec2 u=fract(q);
	u=u*u*(3.0-2.0*u);
	return mix(mix(hash2(p),hash2(p+vec2(1.0,0.0)),u.x),
		mix(hash2(p+vec2(0.0,1.0)),hash2(p+vec2(1.0)),u.x),u.y);
}

void sky() {
	vec3 ray=normalize(EYEDIR);
	float h=max(ray.y,0.0);
	vec3 dawn=normalize(vec3(-.78,.09,.53));
	float wash=pow(max(dot(ray,dawn),0.0),5.0)*exp(-h*2.8);
	vec2 sheet=ray.xz/(.21+h)*vec2(2.66,5.65)+vec2(-8.17,-5.44);
	float banks=.59*cloud(sheet)+.24*cloud(sheet*2.06+11.5)+.11*cloud(sheet*4.33-7.3)+.055*cloud(sheet*8.58);
	float layer=smoothstep(.35,.72,banks);
	float edge_light=smoothstep(.13,.35,banks)-smoothstep(.39,.57,banks);

	vec3 horizon=vec3(.302,.371,.383)+vec3(.233,.105,.044)*wash;
	vec3 overhead=vec3(.054,.105,.145);
	vec3 open_sky=mix(horizon,overhead,pow(h,.47));
	vec3 cloud_body=mix(vec3(.184,.238,.266),vec3(.063,.098,.125),pow(h,.52));
	cloud_body+=vec3(.231,.131,.079)*edge_light*wash;
	float weight=smoothstep(-.03,.17,h)*layer;
	vec3 colour=mix(open_sky,cloud_body,weight*.93);
	colour+=vec3(.12,.061,.03)*pow(wash,5.0)*(.53+edge_light*.4);
	COLOR=colour;
}
