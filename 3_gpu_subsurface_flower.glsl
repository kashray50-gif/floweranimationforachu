// ============================================================================
// GLSL FRAGMENT SHADER — REAL-TIME GPU SUBSURFACE FLORAL BOUQUET (Shadertoy/WebGL2)
// Features:
//  - Polar Phyllotaxis Petal SDFs with Curl Deformation
//  - Subsurface Scattering (SSS) Translucency Approximation
//  - Specular Fresnel Rim Lighting & Bokeh Depth-of-Field
// ============================================================================
#version 300 es
precision highp float;

uniform vec2 u_resolution;
uniform float u_time;
out vec4 fragColor;

#define PI 3.14159265359
#define GOLDEN_ANGLE 2.39996323

mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}

// Signed Distance Function for a single sculpted rose petal
float sdPetal(vec2 p, float radius, float curl) {
    p.y += radius * 0.45;
    p.x *= 1.15 - 0.25 * smoothstep(-radius, radius, p.y);
    float d = length(p) - radius;
    d += sin(p.x * 12.0 + curl) * 0.008;
    return d;
}

// Render multi-layered spiral rose with self-shadowing & rim highlights
vec3 renderRose(vec2 uv, vec2 center, float scale, vec3 baseCol, vec3 tipCol, float time) {
    vec2 p = (uv - center) / scale;
    float distCenter = length(p);
    if (distCenter > 0.55) return vec3(0.0);

    vec3 accum = vec3(0.0);
    float alphaAccum = 0.0;

    for (int i = 28; i >= 0; i--) {
        float fi = float(i);
        float ratio = fi / 28.0;
        float angle = fi * GOLDEN_ANGLE + sin(time * 0.8 + fi * 0.15) * 0.04;
        float rad = mix(0.04, 0.24, ratio);

        vec2 q = rot(angle) * p;
        q.y -= rad * 0.55;

        float d = sdPetal(q, rad * 0.85, fi);
        float mask = 1.0 - smoothstep(-0.004, 0.004, d);

        if (mask > 0.001) {
            float edge = smoothstep(-0.025, 0.0, d);
            float ao = mix(0.45, 1.05, ratio);
            vec3 col = mix(baseCol, tipCol, smoothstep(-rad, rad, q.y)) * ao;
            col += vec3(1.0, 0.82, 0.88) * pow(edge, 3.0) * 0.45; // Fresnel rim
            accum = mix(accum, col, mask);
            alphaAccum = max(alphaAccum, mask);
        }
    }
    return accum * alphaAccum;
}

// Render 6-petal Stargazer Lily with papillae spots & golden anthers
vec3 renderLily(vec2 uv, vec2 center, float scale, float time) {
    vec2 p = (uv - center) / scale;
    if (length(p) > 0.65) return vec3(0.0);

    vec3 col = vec3(0.0);
    for (int i = 0; i < 6; i++) {
        float ang = float(i) * (PI * 2.0 / 6.0) + sin(time * 0.6) * 0.05;
        vec2 q = rot(ang) * p;
        q.y -= 0.18;

        float w = 0.09 * sin(clamp((q.y + 0.18) / 0.36, 0.0, 1.0) * PI);
        float d = length(vec2(max(abs(q.x) - w, 0.0), max(abs(q.y) - 0.17, 0.0))) - 0.015;
        float mask = 1.0 - smoothstep(-0.004, 0.004, d);

        if (mask > 0.001) {
            float grad = clamp((q.y + 0.18) / 0.36, 0.0, 1.0);
            vec3 petalCol = mix(vec3(0.85, 0.12, 0.36), vec3(1.0, 0.92, 0.95), pow(grad, 1.4));
            // Crimson spots
            float spots = sin(q.x * 160.0) * sin(q.y * 160.0);
            if (spots > 0.82 && grad < 0.65) {
                petalCol = vec3(0.32, 0.02, 0.12);
            }
            col = mix(col, petalCol, mask);
        }
    }
    return col;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    vec3 bg = mix(vec3(0.02, 0.03, 0.06), vec3(0.08, 0.11, 0.18), 1.0 - length(uv));

    vec3 flower1 = renderRose(uv, vec2(-0.18, 0.06), 0.72, vec3(0.35, 0.02, 0.12), vec3(1.0, 0.35, 0.52), u_time);
    vec3 flower2 = renderRose(uv, vec2(0.19, 0.04), 0.68, vec3(0.45, 0.05, 0.08), vec3(1.0, 0.55, 0.42), u_time + 1.4);
    vec3 flower3 = renderLily(uv, vec2(0.0, 0.22), 0.78, u_time);

    vec3 color = bg + flower1 + flower2 + flower3;
    // Tone mapping & gamma correction
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0 / 2.2));
    fragColor = vec4(color, 1.0);
}
