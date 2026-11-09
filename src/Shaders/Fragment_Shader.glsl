#version 460 core
out vec4 FragColor;

in vec3 Color;
in vec2 Coord_Tex;
in float Id_Texture;


uniform sampler2D uTexture0;
uniform sampler2D uTexture1;
uniform sampler2D uTexture2;




void main() {
    FragColor = vec4(Color, 1.0);
}