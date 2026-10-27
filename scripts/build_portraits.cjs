#!/usr/bin/env node
/*
 * Rebuild the homepage's responsive 4:5 WebP portraits from the editable SVG.
 * Requires sharp: npm install --no-save sharp (or set NODE_PATH to its location).
 * Run from any directory: node scripts/build_portraits.cjs
 *
 * The original square artwork is centered in the site's 4:5 object-fit:cover
 * frame. Encode that same visible crop so visitors do not download pixels that
 * the frame always hides. This does not alter the photograph or cobalt mug.
 */
"use strict";
const fs = require("node:fs/promises");
const path = require("node:path");
const sharp = require("sharp");

const assets = path.resolve(__dirname, "../docs/assets");
const widths = [400, 640, 800, 1000];

async function main() {
  let source = await fs.readFile(path.join(assets, "mark-deniel-office-cobalt-mug.svg"), "utf8");
  // librsvg's embedded raster support varies by build. PNG is universally
  // supported; this lossless conversion preserves the original decoded pixels.
  for (const match of source.matchAll(/data:image\/webp;base64,([^"]+)/g)) {
    const png = await sharp(Buffer.from(match[1], "base64")).png().toBuffer();
    source = source.replace(match[0], `data:image/png;base64,${png.toString("base64")}`);
  }
  // Original 1254-square source: a 1003.2-wide crop starts 125.4px from the left.
  // Fractional coordinates retain the exact centered CSS crop at every size.
  const cropped = source.replace(/<svg\b[^>]*>/, '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1250" viewBox="125.4 0 1003.2 1254">');
  for (const width of widths) {
    const height = width * 5 / 4;
    const filename = `mark-deniel-portrait-${width}.webp`;
    const output = path.join(assets, filename);
    await sharp(Buffer.from(cropped)).resize(width, height).webp({ quality: 82, effort: 6 }).toFile(output);
    const stat = await fs.stat(output);
    console.log(`${filename}: ${width} × ${height}, ${stat.size} bytes`);
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
