# Demo video regeneration

The Build Week product branches remain independent. These shared scripts only
capture their public fixture pages and render the resulting images with each
product's own narration file.

## Web products

```sh
./scripts/regenerate_web_demo.sh \
  /absolute/path/to/product/site \
  4311 \
  /absolute/path/to/product/artifacts/demo/narration.txt \
  /absolute/path/to/product/artifacts/demo/product-demo.mp4
```

The command starts the product's local site, captures the overview, verified
fixture result, and method sections, synthesizes narration with the macOS
`Samantha` voice, and writes an H.264/AAC MP4.

The script resolves `node` from `PATH`. Set `CODEX_BUNDLED_NODE` only when a
specific Node executable is required. Playwright must be resolvable by that
Node process; when it lives outside normal module resolution, set
`CODEX_BUNDLED_NODE_MODULES` or `NODE_PATH` to its module directory.

## Image sequence

```sh
./scripts/render_demo_video.sh \
  output.mp4 narration.txt 1080x1920 \
  welcome.png results.png evidence.png report.png
```

This path is used for the iOS product's inspected screenshots. Inputs must be
trusted local images because the installed FFmpeg 8.0.1 is behind the current
8.0 maintenance release.
