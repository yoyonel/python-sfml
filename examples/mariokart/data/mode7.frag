/**
https://github.com/vinibiavatti1/mode7
http://glslsandbox.com/e#26532.3
https://github.com/OneLoneCoder/videos/blob/master/OneLoneCoder_Pseudo3DPlanesMode7.cpp
/**/
uniform sampler2D texture;

uniform float time;

uniform float fFarX1;
uniform float fFarY1;

uniform float fNearX1;
uniform float fNearY1;

uniform float fFarX2;
uniform float fFarY2;

uniform float fNearX2;
uniform float fNearY2;

// https://github.com/hughsk/glsl-fog
// https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glFog.xml
float fogFactorExp2(const float dist, const float density)
{
    const float LOG2 = -1.442695;
    float d = density * dist;
    return 1.0 - clamp(exp2(d * d * LOG2), 0.0, 1.0);
}

vec2 project_sample_mode7(vec2 pos)
{
    float fSampleDepth = pos.y;

    // Use sample point in non-linear (1/x) way to enable perspective
    // and grab start and end points for lines across the screen
    float fStartX = (fFarX1 - fNearX1) / (fSampleDepth) + fNearX1;
    float fStartY = (fFarY1 - fNearY1) / (fSampleDepth) + fNearY1;
    float fEndX = (fFarX2 - fNearX2) / (fSampleDepth) + fNearX2;
    float fEndY = (fFarY2 - fNearY2) / (fSampleDepth) + fNearY2;

    float fSampleWidth = pos.x;
    float fSampleX = (fEndX - fStartX) * fSampleWidth + fStartX;
    float fSampleY = (fEndY - fStartY) * fSampleWidth + fStartY;

    // Wrap sample coordinates to give "infinite" periodicity on maps
//    fSampleX = mod(fSampleX, 1.0);
//    fSampleY = mod(fSampleY, 1.0);

    return vec2(fSampleX, fSampleY);
}

vec4 mode7_nearest_sampling()
{
    vec2 pos = gl_TexCoord[0].xy;

    vec2 proj_pos = project_sample_mode7(pos);

    // texture sampling
    vec4 tex_sampling = texture2D(texture, proj_pos);

    return tex_sampling;
}

void main()
{
    vec4 color = mode7_nearest_sampling();

    //fading
//    float depth = 1.0 - pos.y;
//    float fogAmount = fogFactorExp2(depth, 0.82);
//    const vec4 fogColor = vec4(1.0);
//    color = mix(color, fogColor, fogAmount);

    gl_FragColor = color;
}


