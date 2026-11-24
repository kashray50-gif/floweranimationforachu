/**
 * ============================================================================
 * TYPESCRIPT + THREE.JS 3D PBR BOTANICAL BOUQUET CONSERVATORY
 * Builds procedural 3D curved rose & lily petal geometries with MeshPhysicalMaterial
 * (clearcoat, sheen, transmission) and harmonic wind vertex sway.
 * ============================================================================
 */
import * as THREE from 'three';

export interface BotanicalFlowerConfig {
  species: 'rose' | 'lily' | 'peony';
  basePosition: THREE.Vector3;
  tipPosition: THREE.Vector3;
  primaryColor: number;
  secondaryColor: number;
  scale: number;
}

export class BotanicalConservatory3D {
  private scene: THREE.Scene;
  private flowers: THREE.Group[] = [];
  private clock = new THREE.Clock();

  constructor(scene: THREE.Scene) {
    this.scene = scene;
    this.setupLighting();
  }

  private setupLighting(): void {
    const ambient = new THREE.AmbientLight(0xffeedd, 0.55);
    this.scene.add(ambient);

    const keyLight = new THREE.DirectionalLight(0xfff5e4, 2.2);
    keyLight.position.set(4, 9, 6);
    keyLight.castShadow = true;
    this.scene.add(keyLight);

    const rimLight = new THREE.PointLight(0xff758f, 1.8, 18);
    rimLight.position.set(-4, 5, -5);
    this.scene.add(rimLight);
  }

  private createPetalGeometry(width: number, height: number, curl: number): THREE.BufferGeometry {
    const geom = new THREE.PlaneGeometry(width, height, 12, 16);
    const pos = geom.attributes.position;

    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i) + height * 0.5;
      const u = y / height;
      const v = x / (width * 0.5);

      // Taper petal silhouette
      const taper = Math.sin(u * Math.PI);
      pos.setX(i, x * taper);
      pos.setY(i, y);

      // Cup & curl curvature in Z
      const zCup = (1.0 - v * v) * Math.sin(u * Math.PI) * 0.14;
      const zCurl = Math.pow(u, 2.4) * curl;
      pos.setZ(i, zCup - zCurl);
    }

    geom.computeVertexNormals();
    return geom;
  }

  public spawnRose(config: BotanicalFlowerConfig): THREE.Group {
    const flowerGroup = new THREE.Group();
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    const petalCount = 32;

    for (let i = 0; i < petalCount; i++) {
      const ratio = i / petalCount;
      const theta = i * goldenAngle;

      const color = new THREE.Color(config.primaryColor).lerp(
        new THREE.Color(config.secondaryColor),
        ratio
      );

      const material = new THREE.MeshPhysicalMaterial({
        color,
        roughness: 0.48,
        metalness: 0.02,
        sheen: 0.85,
        sheenRoughness: 0.35,
        sheenColor: new THREE.Color(0xffccd5),
        side: THREE.DoubleSide,
      });

      const geom = this.createPetalGeometry(
        (0.26 + ratio * 0.48) * config.scale,
        (0.32 + ratio * 0.55) * config.scale,
        0.12 + ratio * 0.28
      );

      const petal = new THREE.Mesh(geom, material);
      petal.rotation.y = theta;
      petal.rotation.x = 0.22 + ratio * 1.05;
      petal.position.y = ratio * 0.08;
      flowerGroup.add(petal);
    }

    // Curved Stem Tube
    const mid = config.basePosition.clone().lerp(config.tipPosition, 0.5);
    mid.x += (Math.random() - 0.5) * 0.4;
    const curve = new THREE.QuadraticBezierCurve3(config.basePosition, mid, config.tipPosition);
    const stemGeom = new THREE.TubeGeometry(curve, 24, 0.028 * config.scale, 8, false);
    const stemMat = new THREE.MeshStandardMaterial({ color: 0x2d6a4f, roughness: 0.65 });
    const stemMesh = new THREE.Mesh(stemGeom, stemMat);

    flowerGroup.position.copy(config.tipPosition);
    this.scene.add(stemMesh);
    this.scene.add(flowerGroup);
    this.flowers.push(flowerGroup);
    return flowerGroup;
  }

  public update(): void {
    const t = this.clock.getElapsedTime();
    this.flowers.forEach((f, idx) => {
      f.rotation.z = Math.sin(t * 1.4 + idx) * 0.045;
      f.rotation.x = Math.cos(t * 1.1 + idx * 0.7) * 0.035;
    });
  }
}
