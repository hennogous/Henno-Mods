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
  --ao                      Also write an ambient occlusion map.
  --ao-strength <num>       Multiplier for AO seam/recess contrast. Default: 1.
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
    writeAo: false,
    aoStrength: 1,
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
      case "--ao":
        args.writeAo = true;
        break;
      case "--ao-strength":
        args.aoStrength = Number(readValue());
        break;
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

  await fs.mkdir(outDir, { recursive: true });

  let baseImage = sharp(basePath);
  if (args.size !== undefined) {
    baseImage = baseImage.resize(args.size, args.size, { fit: "fill" });
  }
  const { data, info } = await baseImage.ensureAlpha().raw().toBuffer({ resolveWithObject: true });

  const width = info.width;
  const height = info.height;
  const pixelIndex = (x, y) => (y * width + x) * 4;
  const getLum = (x, y) => {
    const cx = Math.max(0, Math.min(width - 1, x));
    const cy = Math.max(0, Math.min(height - 1, y));
    const i = pixelIndex(cx, cy);
    return luminance(data[i], data[i + 1], data[i + 2]);
  };
  const classifyRegion = makeRegionClassifier(args.preset, width, height, data);

  const base = Buffer.from(data);
  const normal = Buffer.alloc(width * height * 4);
  const gloss = Buffer.alloc(width * height * 4);
  const metal = Buffer.alloc(width * height * 4);
  const heights = new Float32Array(width * height);

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = pixelIndex(x, y);
      const region = classifyRegion(x, y);
      const settings = materialSettings(region);
      const lum = luminance(data[i], data[i + 1], data[i + 2]);
      heights[y * width + x] = lum * settings.normal;
    }
  }

  const heightAt = (x, y) => {
    const cx = Math.max(0, Math.min(width - 1, x));
    const cy = Math.max(0, Math.min(height - 1, y));
    return heights[cy * width + cx];
  };
  const heightGradient = (x, y) => {
    const dx =
      (heightAt(x + 1, y - 1) + 2 * heightAt(x + 1, y) + heightAt(x + 1, y + 1) -
        (heightAt(x - 1, y - 1) + 2 * heightAt(x - 1, y) + heightAt(x - 1, y + 1))) *
      0.25;
    const dy =
      (heightAt(x - 1, y + 1) + 2 * heightAt(x, y + 1) + heightAt(x + 1, y + 1) -
        (heightAt(x - 1, y - 1) + 2 * heightAt(x, y - 1) + heightAt(x + 1, y - 1))) *
      0.25;
    return { dx, dy };
  };

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = pixelIndex(x, y);
      const region = classifyRegion(x, y);
      const settings = materialSettings(region);
      const lum = getLum(x, y);

      const { dx: rawDx, dy: rawDy } = heightGradient(x, y);
      const dx = rawDx * args.normalStrength;
      const dy = rawDy * args.normalStrength;
      let nx = -dx;
      let ny = -dy;
      let nz = 1;
      const length = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
      nx /= length;
      ny /= length;
      nz /= length;
      normal[i] = clampByte((nx * 0.5 + 0.5) * 255);
      normal[i + 1] = clampByte((ny * 0.5 + 0.5) * 255);
      normal[i + 2] = clampByte((nz * 0.5 + 0.5) * 255);
      normal[i + 3] = 255;

      const glossValue = clamp01(settings.gloss + (lum - 0.5) * 0.035 + args.glossBias);
      const glossByte = clampByte(glossValue * 255);
      gloss[i] = glossByte;
      gloss[i + 1] = glossByte;
      gloss[i + 2] = glossByte;
      gloss[i + 3] = 255;

      metal[i] = 0;
      metal[i + 1] = 0;
      metal[i + 2] = 0;
      metal[i + 3] = 255;
    }
  }

  const writes = [
    ...(args.copyBase ? [["B", base]] : []),
    ...(args.writeAo ? [["AO", ao]] : []),
    ["N", normal],
    ["G", gloss],
    ["M", metal],
  ];

  for (const [suffix] of writes) {
    await prepareOutput(outputs[suffix], args);
  }

  const report = {};
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
