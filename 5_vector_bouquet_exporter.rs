//! ============================================================================
//! RUST PROCEDURAL BOTANICAL SVG ENGINE (Zero External Dependencies)
//! Generates a crisp, infinite-resolution vector bouquet with multi-stop radial
//! gradients, Fibonacci roses, lilies, and sunflowers saved to `bouquet.svg`.
//! Run: rustc botanical_bouquet.rs && ./botanical_bouquet
//! ============================================================================

use std::f64::consts::PI;
use std::fs::File;
use std::io::{BufWriter, Write};

const GOLDEN_ANGLE: f64 = 2.399963229728653;

struct Rng(u64);
impl Rng {
    fn next_f64(&mut self) -> f64 {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1);
        ((self.0 >> 11) as f64) / ((1u64 << 53) as f64)
    }
    fn range(&mut self, min: f64, max: f64) -> f64 {
        min + (max - min) * self.next_f64()
    }
}

fn write_rose<W: Write>(w: &mut W, cx: f64, cy: f64, scale: f64, grad_id: &str) -> std::io::Result<()> {
    writeln!(w, r#"<g transform="translate({cx:.2},{cy:.2}) scale({scale:.3})">"#)?;
    for i in (0..30).rev() {
        let ratio = (i as f64) / 30.0;
        let deg = (i as f64) * GOLDEN_ANGLE * (180.0 / PI);
        let r = 8.0 + ratio * 38.0;
        let pw = 14.0 + ratio * 26.0;
        let ph = 16.0 + ratio * 30.0;
        writeln!(
            w,
            r#"  <g transform="rotate({deg:.2}) translate(0,{:.2})">
    <path d="M 0,4 C -{pw:.2},-{:.2} -{:.2},-{:.2} 0,-{ph:.2} C {:.2},-{:.2} {pw:.2},-{:.2} 0,4 Z"
          fill="url(#{grad_id})" stroke="rgba(255,220,230,0.45)" stroke-width="0.7"/>
  </g>"#,
            -r * 0.36,
            ph * 0.25,
            pw * 0.85,
            ph * 1.15,
            pw * 0.85,
            ph * 1.15,
            ph * 0.25
        )?;
    }
    writeln!(w, "</g>")
}

fn write_lily<W: Write>(w: &mut W, cx: f64, cy: f64, scale: f64) -> std::io::Result<()> {
    writeln!(w, r#"<g transform="translate({cx:.2},{cy:.2}) scale({scale:.3})">"#)?;
    for p in 0..6 {
        let deg = (p as f64) * 60.0;
        let len = if p % 2 == 0 { 64.0 } else { 58.0 };
        let wid = if p % 2 == 0 { 20.0 } else { 16.0 };
        writeln!(
            w,
            r#"  <g transform="rotate({deg:.1})">
    <path d="M 0,0 C -{wid:.1},-{:.1} -{:.1},-{:.1} 0,-{len:.1} C {:.1},-{:.1} {wid:.1},-{:.1} 0,0 Z"
          fill="url(#lilyGrad)" stroke="rgba(255,255,255,0.65)" stroke-width="0.8"/>
    <line x1="0" y1="-4" x2="0" y2="-{:.1}" stroke="rgba(255,255,255,0.6)" stroke-width="1.2"/>
  </g>"#,
            len * 0.3,
            wid * 0.7,
            len * 0.82,
            wid * 0.7,
            len * 0.82,
            len * 0.3,
            len * 0.85
        )?;
    }
    writeln!(w, "</g>")
}

fn main() -> std::io::Result<()> {
    let file = File::create("botanical_bouquet.svg")?;
    let mut w = BufWriter::new(file);
    let mut rng = Rng(20261124);

    writeln!(
        w,
        r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900">
  <defs>
    <radialGradient id="bgGrad" cx="50%" cy="42%" r="70%">
      <stop offset="0%" stop-color="#141e30"/>
      <stop offset="100%" stop-color="#05080f"/>
    </radialGradient>
    <radialGradient id="roseCrimson" cx="50%" cy="75%" r="80%">
      <stop offset="0%" stop-color="#590d22"/>
      <stop offset="55%" stop-color="#c9184a"/>
      <stop offset="100%" stop-color="#ff8fa3"/>
    </radialGradient>
    <radialGradient id="roseGold" cx="50%" cy="75%" r="80%">
      <stop offset="0%" stop-color="#9a3412"/>
      <stop offset="55%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#fef08a"/>
    </radialGradient>
    <linearGradient id="lilyGrad" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#c8e6c9"/>
      <stop offset="25%" stop-color="#ff4d79"/>
      <stop offset="80%" stop-color="#ff8fa3"/>
      <stop offset="100%" stop-color="#fff0f3"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="900" fill="url(#bgGrad)"/>"##
    )?;

    let cx = 600.0;
    let base_y = 840.0;

    for i in 0..22 {
        let norm = (i as f64) / 21.0 - 0.5;
        let tip_x = cx + norm * 480.0 + rng.range(-25.0, 25.0);
        let tip_y = base_y - rng.range(320.0, 620.0);
        let ctrl_x = cx + norm * 160.0;
        let ctrl_y = base_y - 260.0;
        writeln!(
            w,
            r##"  <path d="M {:.2},{base_y:.2} Q {ctrl_x:.2},{ctrl_y:.2} {tip_x:.2},{tip_y:.2}"
        fill="none" stroke="#2d6a4f" stroke-width="4.2" stroke-linecap="round"/>"##,
            cx + norm * 24.0
        )?;

        let scale = rng.range(0.85, 1.25);
        if i % 3 == 0 {
            write_lily(&mut w, tip_x, tip_y, scale)?;
        } else if i % 2 == 0 {
            write_rose(&mut w, tip_x, tip_y, scale, "roseCrimson")?;
        } else {
            write_rose(&mut w, tip_x, tip_y, scale, "roseGold")?;
        }
    }

    writeln!(w, "</svg>")?;
    w.flush()?;
    println!("Generated high-resolution botanical_bouquet.svg");
    Ok(())
}
