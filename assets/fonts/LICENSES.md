# Vendored fonts — licenses & sources

All fonts are vendored into the repo at build time. **The deployed app makes no
runtime font requests to any CDN** (Off-the-Grid hygiene).

| File | Family | License | Source |
|---|---|---|---|
| AtkinsonHyperlegible-{Regular,Bold}.woff2 | Atkinson Hyperlegible (latin subset) | [SIL OFL 1.1](https://openfontlicense.org) | Braille Institute, via the @fontsource/atkinson-hyperlegible npm package |
| NotoSansDevanagari-{Regular,Bold}.woff2 | Noto Sans Devanagari (devanagari subset) | [SIL OFL 1.1](https://openfontlicense.org) | Google Noto, via the @fontsource/noto-sans-devanagari npm package |

Atkinson Hyperlegible was designed by the Braille Institute specifically to
maximize legibility for low-vision readers — a deliberate fit for an app built
for an elder.

Japanese text intentionally uses the OS-native stack ("Hiragino Sans",
"Yu Gothic UI", "Meiryo") instead of a vendored font: CJK WOFF2 subsets run to
megabytes, and every target platform ships an excellent native Japanese font.
