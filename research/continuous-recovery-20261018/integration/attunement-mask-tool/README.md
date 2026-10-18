# Attunement map mask tool evidence

The accepted popup-tool baseline was `b353b0f88da385321a70b35e2bb7f9bccc7cbb371f69c7d36c3cd8d2c3af543c`. The narrow repair is
`rewrite_attunement_mask_pixel`: it runs only for `/bcattunement/index.html`,
uses `_MarkupTokenParser` source positions, and replaces exactly three visible
references whose requested original is
`https://www.worldofwarcraft.com/bcattunement/images/pixel.gif`:
`img#mapPixel`, `.coverDivStyle1` `background`, and `.coverDivStyle2`
`background`. The legacy `_background` declaration and unrelated pixel URLs
are intentionally unchanged. The replacement is the existing 43-byte
transparent `/shared/wow-com/includes/images/pixel.gif`, prefixed for Pages;
it is a compatibility mask, not recovered attunement image content.

Focused command:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -m unittest -v tests.test_attunement_mask_pixel tests.test_popup_image_viewer
```

The JSON receipt records exact hashes and the read-only frozen v30 page check.
No export, network request, old-output mutation, commit, or publication was
performed.
