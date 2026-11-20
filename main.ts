// Entry point for the news-image-20261120 competition (Node 22,
// standard library only). The finished poster lives in this repository
// as entry.png (drawn by render_poster.py). This program only copies it
// to the output location the grader reads: /output/entry.png, or
// $MAKEFUN_OUTPUT_DIR/entry.png for a local run. No network, fully
// deterministic: the same bytes are written on every run.
//
// Local check:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import {
  copyFileSync,
  mkdirSync,
  openSync,
  readSync,
  closeSync,
  statSync,
} from "node:fs";
import { join } from "node:path";

const PNG_SIGNATURE = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);

const source = new URL("./entry.png", import.meta.url);

// Read only the 8-byte header: a truncated or misnamed image fails
// loudly here instead of silently failing the gate downstream.
const fd = openSync(source, "r");
const header = Buffer.alloc(PNG_SIGNATURE.length);
readSync(fd, header, 0, header.length, 0);
closeSync(fd);
if (!header.equals(PNG_SIGNATURE)) {
  throw new Error("poster image is not a PNG file: " + source.pathname);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(source, target);

if (statSync(target).size !== statSync(source).size) {
  throw new Error("copied image size does not match the source");
}
