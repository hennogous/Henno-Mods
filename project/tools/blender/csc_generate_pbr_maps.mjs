#!/usr/bin/env node
/**
 * Generate aligned Civ VI-style companion PBR maps from a base color atlas.
 *
 * Intended CSC workflow:
 *   1. Create or generate the artistic *_B.png atlas.
 *   2. Run this script to derive *_N.png, *_G.png, *_M.png.
 *   3. Reload the maps in Blender/Asset Editor.
 *
 * This intentionally does not use Blender for pixel writing. Blender is better
 * used for material wiring, UV inspection, and render validation.
 *
 * Does NOT generate an AO map. AO must be baked from geometry in Blender (Cycles,
 * via UV2) rather than derived from the base color -- see
 * project/docs/shared-atlas-ao.md for why and how. UV2 for baking must be a fresh
 * non-overlapping unwrap/pack, not a copy of UV1.
 */

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

let sharp;

const HELP = `
Usage:
  node csc_generate_pbr_maps.mjs --base <Asset_B.png> [options]

Options:
  --asset-name <name>       Asset prefix for output files. Default: basename with _B removed.
  --out-dir <dir>           Output directory. Default: same folder as --base.
  --size <px>               Square output size. Default: source _B dimensions.
  --preset <name>           Region rules: auto, csc-textile-prop. Default: auto.
  --normal-strength <num>   Multiplier for normal map relief. Default: 2.25.
  --height <file.png>       Aligned grayscale height; replaces brightness-derived relief.
  --regions <file.json>     Explicit rectangular material regions (see textures-and-uvs.md).
  --reference-size <px>     Scale derivatives relative to this resolution. Default: no scaling.
  --normal-y <convention>   directx (legacy default) or opengl (Blender).
  --gloss-bias <num>        Additive gloss adjustment in -1..1. Default: 0.
  --copy-base               Also write a resized <Asset>_B.png beside derived maps.
  --overwrite               Replace existing output files.
  --backup                  Before overwriting, copy existing files to *.pre-pbrgen.png.
  --dry-run                 Print planned outputs without writing files.
  -h, --help                Show this help.

Examples:
  node project/tools/blender/csc_generate_pbr_maps.mjs \\
    --base "Spinning Wheel/CSC_TAILORS_SpinningWheel_B.png" \\
    --preset csc-textile-prop --overwrite --backup

Notes:
  Civ VI uses _G as gloss: white is shinier, black is duller.
  _M is black by default because most CSC wood/wool/stone props are non-metal.
  No _AO is generated here -- bake it from geometry in Blender instead.
`;

function parseArgs(argv) {
  const args = {
    preset: "auto",
    normalStrength: 2.25,
    normalY: "directx",
    glossBias: 0,
    copyBase: false,
    overwrite: false,
    backup: false,
    dryRun: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const readValue = () => {
      if (i + 1 >= argv.length) throw new Error(`Missing value for ${arg}`);
      i += 1;
      return argv[i];
    };

    switch (arg) {
      case "--base":
        args.base = readValue();
        break;
      case "--asset-name":
        args.assetName = readValue();
        break;
      case "--out-dir":
        args.outDir = readValue();
        break;
      case "--size":
        args.size = Number(readValue());
        break;
      case "--preset":
        args.preset = readValue();
        break;
      case "--normal-strength":
        args.normalStrength = Number(readValue());
        break;
      case "--height":
        args.height = readValue();
        break;
      case "--regions":
        args.regions = readValue();
        break;
      case "--reference-size":
        args.referenceSize = Number(readValue());
        break;
      case "--normal-y":
        args.normalY = readValue();
        break;
      case "--ao":
      case "--ao-strength":
        throw new Error("AO must be baked from geometry through UV2 in Blender; --ao and --ao-strength are unsupported.");
      case "--gloss-bias":
        args.glossBias = Number(readValue());
        break;
      case "--copy-base":
        args.copyBase = true;
        break;
      case "--overwrite":
        args.overwrite = true;
        break;
      case "--backup":
        args.backup = true;
        break;
      case "--dry-run":
        args.dryRun = true;
        break;
      case "-h":
      case "--help":
        args.help = true;
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (args.help) return args;
  if (!args.base) throw new Error("Missing required --base <Asset_B.png>");
  if (args.size !== undefined && (!Number.isInteger(args.size) || args.size < 16)) {
    throw new Error("--size must be an integer >= 16");
  }
  if (!["auto", "csc-textile-prop"].includes(args.preset)) {
    throw new Error("--preset must be one of: auto, csc-textile-prop");
  }
  for (const key of ["normalStrength", "glossBias"]) {
    if (!Number.isFinite(args[key])) throw new Error(`Invalid numeric value for ${key}`);
  }
  if (args.normalStrength < 0) throw new Error("--normal-strength must be nonnegative");
  if (args.referenceSize !== undefined && (!Number.isFinite(args.referenceSize) || args.referenceSize <= 0)) {
    throw new Error("--reference-size must be positive");
  }
  if (!["directx", "opengl"].includes(args.normalY)) throw new Error("--normal-y must be directx or opengl");
  return args;
}

function stripBaseSuffix(filePath) {
  const parsed = path.parse(filePath);
  return parsed.name.replace(/_B$/i, "");
}

function clampByte(value) {
  return Math.max(0, Math.min(255, Math.round(value)));
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function rgbToHsv(r, g, b) {
  const rn = r / 255;
  const gn = g / 255;
  const bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const delta = max - min;
  let h = 0;
  if (delta !== 0) {
    if (max === rn) h = ((gn - bn) / delta) % 6;
    else if (max === gn) h = (bn - rn) / delta + 2;
    else h = (rn - gn) / delta + 4;
    h *= 60;
    if (h < 0) h += 360;
  }
  const s = max === 0 ? 0 : delta / max;
  return { h, s, v: max };
}

function luminance(r, g, b) {
  return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
}

function makeRegionClassifier(preset, width, height, data) {
  if (preset === "csc-textile-prop") {
    return (x, y) => {
      if (x < Math.round(width * 0.555)) return "wood";
      if (y < Math.round(height * 0.492)) return "wool";
      if (y < Math.round(height * 0.688)) return "thread";
      if (y < Math.round(height * 0.844)) return "neutral";
      return "endgrain";
    };
  }

  return (x, y) => {
    const i = (y * width + x) * 4;
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const { h, s, v } = rgbToHsv(r, g, b);
    if (v > 0.66 && s < 0.22) return "wool";
    if (s > 0.32 && h >= 15 && h <= 55) return "wood";
    if (s > 0.35) return "thread";
    if (v < 0.22) return "dark";
    return "neutral";
  };
}

function materialSettings(region) {
  switch (region) {
    case "wood":
      return { normal: 1.05, aoFloor: 0.60, aoCeil: 0.96, gloss: 0.24 };
    case "wool":
      return { normal: 1.30, aoFloor: 0.74, aoCeil: 0.99, gloss: 0.08 };
    case "thread":
      return { normal: 1.15, aoFloor: 0.66, aoCeil: 0.96, gloss: 0.13 };
    case "endgrain":
      return { normal: 1.00, aoFloor: 0.60, aoCeil: 0.94, gloss: 0.20 };
    case "dark":
      return { normal: 0.70, aoFloor: 0.50, aoCeil: 0.90, gloss: 0.15 };
    case "neutral":
    default:
      return { normal: 0.85, aoFloor: 0.62, aoCeil: 0.95, gloss: 0.18 };
  }
}

// Bounds are normalized, top-left image coordinates, with exclusive upper edges.
// Explicit regions deliberately replace HSV guesses: painted highlights must not
// change a wood pixel into a different material or introduce a height discontinuity.
async function loadRegions(file, width, height) {
  if (!file) return null;
  const regions = JSON.parse(await fs.readFile(file, "utf8"));
  if (!Array.isArray(regions) || !regions.length) throw new Error("--regions must contain a nonempty JSON array");
  const ids = new Int32Array(width * height).fill(-1);
  const settings = regions.map((region, id) => {
    const { bounds } = region;
    if (!Array.isArray(bounds) || bounds.length !== 4 ||
        bounds.some(v => !Number.isFinite(v) || v < 0 || v > 1) ||
        bounds[0] >= bounds[2] || bounds[1] >= bounds[3]) {
      throw new Error(`Invalid bounds for region ${id}`);
    }
    const result = { normal: 1, gloss: 0.18, metalness: 0, ...region,
      pixels: bounds.map((v, i) => Math.round(v * (i % 2 === 0 ? width : height))) };
    for (const key of ["normal", "gloss", "metalness"]) {
      if (!Number.isFinite(result[key]) || result[key] < 0 || (key !== "normal" && result[key] > 1)) {
        throw new Error(`Invalid ${key} for region ${id}`);
      }
    }
    const [x0, y0, x1, y1] = result.pixels;
    if (x0 >= x1 || y0 >= y1) throw new Error(`Region ${id} is smaller than one output pixel`);
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
      const i = y * width + x;
      if (ids[i] !== -1) throw new Error(`Overlapping regions at ${x},${y}`);
      ids[i] = id;
    }
    return result;
  });
  if (ids.includes(-1)) throw new Error("Regions must cover the entire output atlas");
  return { ids, settings };
}

function pixelStats(buffer) {
  let min = 255;
  let max = 0;
  let sum = 0;
  let alphaMin = 255;
  let alphaMax = 0;
  const count = buffer.length / 4;
  for (let i = 0; i < buffer.length; i += 4) {
    min = Math.min(min, buffer[i]);
    max = Math.max(max, buffer[i]);
    sum += buffer[i];
    alphaMin = Math.min(alphaMin, buffer[i + 3]);
    alphaMax = Math.max(alphaMax, buffer[i + 3]);
  }
  return {
    min,
    max,
    avg: Number((sum / count).toFixed(2)),
    alpha: [alphaMin, alphaMax],
  };
}

async function pathExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function prepareOutput(filePath, { overwrite, backup, dryRun }) {
  if (!(await pathExists(filePath))) return;
  if (!overwrite) {
    throw new Error(`Refusing to overwrite existing file without --overwrite: ${filePath}`);
  }
  if (backup && !dryRun) {
    const backupPath = filePath.replace(/\.(png|webp|jpg|jpeg)$/i, ".pre-pbrgen.$1");
    if (!(await pathExists(backupPath))) {
      await fs.copyFile(filePath, backupPath);
    }
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(HELP.trim());
    return;
  }

  try {
    sharp = (await import("sharp")).default;
  } catch (error) {
    console.error("Missing dependency: sharp");
    console.error("");
    console.error("Install it from the tool folder, then rerun:");
    console.error("  cd project/tools/blender");
    console.error("  npm install");
    console.error("");
    console.error(`Original error: ${error.code || error.message}`);
    process.exit(1);
  }

  const basePath = path.resolve(args.base);
  const outDir = path.resolve(args.outDir || path.dirname(basePath));
  const assetName = args.assetName || stripBaseSuffix(basePath);
  const outputs = {
    B: path.join(outDir, `${assetName}_B.png`),
    N: path.join(outDir, `${assetName}_N.png`),
    G: path.join(outDir, `${assetName}_G.png`),
    M: path.join(outDir, `${assetName}_M.png`),
  };

  let baseImage = sharp(basePath);
  if (args.size !== undefined) {
    baseImage = baseImage.resize(args.size, args.size, { fit: "fill" });
  }
  const { data, info } = await baseImage.ensureAlpha().raw().toBuffer({ resolveWithObject: true });

  const width = info.width;
  const height = info.height;
  const regions = await loadRegions(args.regions, width, height);
  let explicitHeight;
  if (args.height) {
    const [baseMeta, heightMeta] = await Promise.all([sharp(basePath).metadata(), sharp(args.height).metadata()]);
    if (baseMeta.width !== heightMeta.width || baseMeta.height !== heightMeta.height) {
      throw new Error("Height map dimensions must match the source base atlas before resizing");
    }
    // Height is scalar data: use the stored red channel without an sRGB transform.
    explicitHeight = await sharp(args.height).resize(width, height, { fit: "fill" })
      .removeAlpha().extractChannel(0).raw().toBuffer();
  }
  const pixelIndex = (x, y) => (y * width + x) * 4;
  const getLum = (x, y) => {
    const cx = Math.max(0, Math.min(width - 1, x));
    const cy = Math.max(0, Math.min(height - 1, y));
    const i = pixelIndex(cx, cy);
    return luminance(data[i], data[i + 1], data[i + 2]);
  };
  const classifyRegion = makeRegionClassifier(args.preset, width, height, data);
  const settingsAt = (x, y) => regions
    ? regions.settings[regions.ids[y * width + x]]
    : materialSettings(classifyRegion(x, y));

  const base = Buffer.from(data);
  const normal = Buffer.alloc(width * height * 4);
  const gloss = Buffer.alloc(width * height * 4);
  const metal = Buffer.alloc(width * height * 4);
  const heights = new Float32Array(width * height);

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = pixelIndex(x, y);
      const lum = luminance(data[i], data[i + 1], data[i + 2]);
      heights[y * width + x] = explicitHeight ? explicitHeight[y * width + x] / 255 : lum;
    }
  }

  const heightAt = (x, y, bounds) => {
    const [x0, y0, x1, y1] = bounds;
    const cx = Math.max(x0, Math.min(x1 - 1, x));
    const cy = Math.max(y0, Math.min(y1 - 1, y));
    return heights[cy * width + cx];
  };
  const heightGradient = (x, y, bounds) => {
    const at = (sx, sy) => heightAt(sx, sy, bounds);
    const dx =
      (at(x + 1, y - 1) + 2 * at(x + 1, y) + at(x + 1, y + 1) -
        (at(x - 1, y - 1) + 2 * at(x - 1, y) + at(x - 1, y + 1))) *
      0.25;
    const dy =
      (at(x - 1, y + 1) + 2 * at(x, y + 1) + at(x + 1, y + 1) -
        (at(x - 1, y - 1) + 2 * at(x, y - 1) + at(x + 1, y - 1))) *
      0.25;
    return { dx, dy };
  };

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = pixelIndex(x, y);
      const settings = settingsAt(x, y);
      const lum = getLum(x, y);

      const { dx: rawDx, dy: rawDy } = heightGradient(x, y, settings.pixels || [0, 0, width, height]);
      // Apply material amplitude AFTER differentiation to avoid artificial steps.
      const dx = rawDx * args.normalStrength * settings.normal * (args.referenceSize ? width / args.referenceSize : 1);
      const dy = rawDy * args.normalStrength * settings.normal * (args.referenceSize ? height / args.referenceSize : 1);
      let nx = -dx;
      // Image Y points down; Blender's tangent V points up.
      let ny = args.normalY === "opengl" ? dy : -dy;
      let nz = 1;
      const length = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
      nx /= length;
      ny /= length;
      nz /= length;
      normal[i] = clampByte((nx * 0.5 + 0.5) * 255);
      normal[i + 1] = clampByte((ny * 0.5 + 0.5) * 255);
      normal[i + 2] = clampByte((nz * 0.5 + 0.5) * 255);
      normal[i + 3] = 255;

      const glossValue = clamp01(settings.gloss + (regions ? 0 : (lum - 0.5) * 0.035) + args.glossBias);
      const glossByte = clampByte(glossValue * 255);
      gloss[i] = glossByte;
      gloss[i + 1] = glossByte;
      gloss[i + 2] = glossByte;
      gloss[i + 3] = 255;

      metal[i] = metal[i + 1] = metal[i + 2] = clampByte((settings.metalness || 0) * 255);
      metal[i + 3] = 255;
    }
  }

  const writes = [
    ...(args.copyBase ? [["B", base]] : []),
    ["N", normal],
    ["G", gloss],
    ["M", metal],
  ];

  for (const [suffix] of writes) {
    await prepareOutput(outputs[suffix], args);
  }

  const report = {};
  if (!args.dryRun) await fs.mkdir(outDir, { recursive: true });
  for (const [suffix, buffer] of writes) {
    report[suffix] = {
      path: outputs[suffix],
      ...pixelStats(buffer),
    };
    if (!args.dryRun) {
      await sharp(buffer, { raw: { width, height, channels: 4 } }).png().toFile(outputs[suffix]);
    }
  }

  console.log(
    JSON.stringify(
      {
        base: basePath,
        assetName,
        size: [width, height],
        preset: args.preset,
        heightSource: args.height ? path.resolve(args.height) : "base luminance (approximation)",
        regions: args.regions ? path.resolve(args.regions) : null,
        normalY: args.normalY,
        normalStrength: args.normalStrength,
        referenceSize: args.referenceSize || null,
        wrote: report,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
