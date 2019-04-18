/**
https://github.com/vinibiavatti1/mode7
http://glslsandbox.com/e#26532.3
https://github.com/OneLoneCoder/videos/blob/master/OneLoneCoder_Pseudo3DPlanesMode7.cpp
/**/
uniform sampler2D tex_sat;

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

uniform float size_filter;

float invTextureSize = 1.0 / tex_width;

vec4 sample_sat(sampler2D t, vec2 UL, float size_filter)
{
    vec2 UR = UL + vec2(size_filter, 0.0) * invTextureSize;
    vec2 LR = UL + vec2(size_filter, size_filter) * invTextureSize;
    vec2 LL = UL + vec2(0.0, size_filter) * invTextureSize;

    vec3 avg = (
        (texture2D(t, UL).rgb + texture2D(t, LR).rgb) -
        (texture2D(t, UR).rgb + texture2D(t, LL).rgb)
    ) / (size_filter*size_filter);
    avg += pixel_average.rgb;

    return vec4(avg, 1.0);
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

// https://github.com/hughsk/glsl-fog
// https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glFog.xml
float fogFactorExp2(const float dist, const float density)
{
    const float LOG2 = -1.442695;
    float d = density * dist;
    return 1.0 - clamp(exp2(d * d * LOG2), 0.0, 1.0);
}

vec4 mode7_with_sat()
{
    vec2 pos = gl_TexCoord[0].xy - vec2(0.5, 0.5) * invTextureSize;

    vec2 proj_pos = project_sample_mode7(pos);

    // SAT
    //float size_filter = 4.0;
    vec4 tex_sampling = sample_sat(tex_sat, proj_pos, size_filter);

    vec4 result = tex_sampling;

    //fading
    float depth = 1.0 - pos.y;
    float fogAmount = fogFactorExp2(depth, 0.582);
    const vec4 fogColor = vec4(1.0);
    result = mix(result, fogColor, fogAmount);

    return result;
}

void main()
{
    gl_FragColor = mode7_with_sat();
}


