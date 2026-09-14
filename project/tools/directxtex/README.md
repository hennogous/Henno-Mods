# DirectXTex texture converter

The asset exporter uses a local `texconv.exe` here when `--texconv` is omitted,
falling back to PATH. The binary is ignored by Git. No system installation is needed.

Verified on Shadow, 14 September 2026: Microsoft's `may2026` release,
`texconv version 2026.5.8.1`.

- Release: https://github.com/microsoft/DirectXTex/releases/tag/may2026
- Binary: https://github.com/microsoft/DirectXTex/releases/download/may2026/texconv.exe
- Published SHA256: `dcfdec10244e02cf5037fba089c55fb7e1326b1c8181742d77d15fa5cb5eef06`
- License: https://github.com/microsoft/DirectXTex/blob/may2026/LICENSE

Download the binary here and verify the SHA256 before running it. The older copy
inside Shadow's CivNexus6 installation fails to start with status `0xC0000135`;
it is not the converter used by the current exporter recipe.
