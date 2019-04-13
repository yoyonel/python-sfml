/**
https://github.com/vinibiavatti1/mode7
http://glslsandbox.com/e#26532.3
https://github.com/OneLoneCoder/videos/blob/master/OneLoneCoder_Pseudo3DPlanesMode7.cpp
/**/
uniform sampler2D texture;
uniform sampler2D sat;

uniform float time;

uniform float fFarX1;
uniform float fFarY1;

uniform float fNearX1;
uniform float fNearY1;

uniform float fFarX2;
uniform float fFarY2;

uniform float fNearX2;
uniform float fNearY2;

uniform float tex_width;

uniform vec4 pixel_average;


vec4 mode7_0()
{
    vec2 pos = gl_TexCoord[0].xy;

    float horizon = 0.0;
    float fov = 0.5;
    float scaling = 0.1;

    vec3 p = vec3(pos.x, fov, pos.y - horizon);
    vec2 s = vec2(p.x/p.z, p.y/p.z) * scaling;

    //fading
    float fading = min(p.z*p.z*10.0, 1.0);

    vec3 color_tex = texture2D(texture, s).rgb;

    return vec4(fading * color_tex, 1.0);
}

// https://github.com/hughsk/glsl-fog
// https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glFog.xml
float fogFactorExp2(const float dist, const float density)
{
    const float LOG2 = -1.442695;
    float d = density * dist;
    return 1.0 - clamp(exp2(d * d * LOG2), 0.0, 1.0);
}

vec4 sample_sat(sampler2D t, vec2 UL, float size_filter)
{
    vec2 UR = UL + vec2(size_filter, 0.0) / tex_width;
    vec2 LR = UL + vec2(size_filter, size_filter) / tex_width;
    vec2 LL = UL + vec2(0.0, size_filter) / tex_width;

    vec3 avg = (
        (texture2D(t, UL).rgb + texture2D(t, LR).rgb) -
        (texture2D(t, UR).rgb + texture2D(t, LL).rgb)
    ) / (size_filter*size_filter) + pixel_average.rgb;

    return vec4(avg, 1.0);
}

vec4 mode7_1()
{
    vec2 pos = gl_TexCoord[0].xy;

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
    fSampleX = mod(fSampleX, 1.0);
    fSampleY = mod(fSampleY, 1.0);

    // texture sampling
//    vec4 tex_sampling = texture2D(texture, vec2(fSampleX, fSampleY));

    // SAT
    float size_filter = 1.5;
    vec4 tex_sampling = sample_sat(sat, vec2(fSampleX, fSampleY), size_filter);

    vec4 result = tex_sampling;

    //fading
//    float fogAmount = fogFactorExp2(1.0 - fSampleDepth, 0.82);
//    const vec4 fogColor = vec4(1.0);
//    result = mix(result, fogColor, fogAmount);

    return result;
}

void main()
{
    //	gl_FragColor = mode7_0();
    gl_FragColor = mode7_1();
}


