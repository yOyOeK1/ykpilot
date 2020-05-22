header = '''
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

uniform vec2 resolution;
uniform float time;
'''

shader_monochrome = header + '''
void main() {
    vec4 rgb = texture2D(texture0, tex_coord0);
    float c = (rgb.x + rgb.y + rgb.z) * 0.3333;
    gl_FragColor = vec4(c, c, c, 1.0);
}
'''

shader_red = header + '''
void main() {
	vec4 rgb = texture2D(texture0, tex_coord0);
	float c = (rgb.x + rgb.y + rgb.z) * 0.3333;
	gl_FragColor = vec4(c, 0.0, 0.0, 1
	.0);
}
'''
shaders_list = [shader_monochrome, shader_red]
