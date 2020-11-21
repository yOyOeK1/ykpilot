header = '''
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

uniform mat4 frag_modelview_mat;
'''

shader_monochrome = header + '''
void main() {
    /*
    vec4 rgb = texture2D(texture0, tex_coord0);
    float c = (rgb.x + rgb.y + rgb.z) * 0.3333;
    gl_FragColor = vec4(c, c, c, rgb[3]);
    */
    gl_FragColor = frag_color * texture2D(texture0, tex_coord0);
}
'''

shader_day = header + '''
void main() {
    /*
    vec4 rgb = texture2D(texture0, tex_coord0);
    float c = (rgb.x + rgb.y + rgb.z) * 0.3333;
    gl_FragColor = vec4(c, c, c, rgb[3]);
    */
    gl_FragColor = frag_color * texture2D(texture0, tex_coord0);
}
'''


shader_red = header + '''
void main() {
	vec4 rgb = texture2D(texture0, tex_coord0);
	float c = rgb[0];
	//(rgb.x + (rgb[1]/4.0) + rgb[2]/4.0);
	if( c < 0.01 ){
	    c = (rgb[1]+rgb[2])*0.5*rgb[3];
	}
	    
	gl_FragColor = frag_color*vec4(c, rgb[1]*0.1, rgb[2]*0.1, rgb[3]);//vec4(rgb[0], rgb[1]*0.1, rgb[2]*0.1, rgb[3]); 
	
}
'''
shaders_list = [shader_monochrome, shader_red]
