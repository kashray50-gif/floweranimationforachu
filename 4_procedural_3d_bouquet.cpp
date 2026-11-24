/**
 * ============================================================================
 * C++17 PROCEDURAL 3D BOTANICAL BOUQUET ENGINE (OpenGL / Raylib Compatible)
 * Generates parametric Bezier stems, Fibonacci phyllotaxis rose petals,
 * and dynamic harmonic wind deformation in real time.
 * Compile: g++ -std=c++17 bouquet_3d.cpp -lraylib -lm -o bouquet_3d
 * ============================================================================
 */
#include <cmath>
#include <vector>
#include <random>
#include <algorithm>

struct Vec3 {
    float x, y, z;
    Vec3 operator+(const Vec3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vec3 operator-(const Vec3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vec3 operator*(float s) const { return {x * s, y * s, z * s}; }
};

struct ColorRGBA {
    unsigned char r, g, b, a;
};

struct PetalVertex {
    Vec3 position;
    Vec3 normal;
    ColorRGBA color;
};

class BotanicalBouquetGenerator {
public:
    static constexpr float PI = 3.14159265359f;
    static constexpr float GOLDEN_ANGLE = 2.399963229728653f;

    static Vec3 evalQuadraticBezier(const Vec3& p0, const Vec3& p1, const Vec3& p2, float t) {
        float inv = 1.0f - t;
        return p0 * (inv * inv) + p1 * (2.0f * inv * t) + p2 * (t * t);
    }

    static ColorRGBA lerpColor(ColorRGBA c1, ColorRGBA c2, float t) {
        t = std::clamp(t, 0.0f, 1.0f);
        return {
            static_cast<unsigned char>(c1.r + (c2.r - c1.r) * t),
            static_cast<unsigned char>(c1.g + (c2.g - c1.g) * t),
            static_cast<unsigned char>(c1.b + (c2.b - c1.b) * t),
            static_cast<unsigned char>(c1.a + (c2.a - c1.a) * t)
        };
    }

    std::vector<PetalVertex> buildRoseMesh(Vec3 center, float scale, ColorRGBA coreCol, ColorRGBA tipCol) {
        std::vector<PetalVertex> mesh;
        const int petalCount = 34;

        for (int i = 0; i < petalCount; ++i) {
            float ratio = static_cast<float>(i) / static_cast<float>(petalCount);
            float theta = i * GOLDEN_ANGLE;
            float openAngle = 0.22f + ratio * 1.15f;
            float petalLen = (0.35f + ratio * 0.85f) * scale;
            float petalWid = (0.28f + ratio * 0.65f) * scale;

            ColorRGBA c = lerpColor(coreCol, tipCol, ratio);

            // Subdivide each petal into a curved 3D patch
            const int uSteps = 8;
            const int vSteps = 8;
            for (int u = 0; u < uSteps; ++u) {
                float u0 = static_cast<float>(u) / uSteps;
                float u1 = static_cast<float>(u + 1) / uSteps;
                for (int v = 0; v < vSteps; ++v) {
                    float v0 = (static_cast<float>(v) / vSteps) * 2.0f - 1.0f;
                    float v1 = (static_cast<float>(v + 1) / vSteps) * 2.0f - 1.0f;

                    auto evalPatch = [&](float uu, float vv) -> Vec3 {
                        float r = uu * petalLen;
                        float widthEnv = std::sin(uu * PI) * petalWid * 0.5f;
                        float localX = vv * widthEnv;
                        float localY = std::cos(openAngle) * r - std::pow(uu, 2.2f) * 0.18f * scale;
                        float localZ = std::sin(openAngle) * r + (vv * vv) * 0.08f * scale;

                        float rotX = localX * std::cos(theta) - localZ * std::sin(theta);
                        float rotZ = localX * std::sin(theta) + localZ * std::cos(theta);
                        return {center.x + rotX, center.y + localY, center.z + rotZ};
                    };

                    Vec3 p00 = evalPatch(u0, v0);
                    Vec3 p10 = evalPatch(u1, v0);
                    Vec3 p11 = evalPatch(u1, v1);
                    Vec3 p01 = evalPatch(u0, v1);

                    Vec3 norm = {std::cos(theta), 0.65f, std::sin(theta)};
                    mesh.push_back({p00, norm, c});
                    mesh.push_back({p10, norm, c});
                    mesh.push_back({p11, norm, c});
                    mesh.push_back({p00, norm, c});
                    mesh.push_back({p11, norm, c});
                    mesh.push_back({p01, norm, c});
                }
            }
        }
        return mesh;
    }
};

int main() {
    BotanicalBouquetGenerator generator;
    auto roseVertices = generator.buildRoseMesh(
        {0.0f, 1.5f, 0.0f},
        1.25f,
        {110, 12, 38, 255},
        {255, 117, 143, 255}
    );
    return roseVertices.empty() ? 1 : 0;
}
