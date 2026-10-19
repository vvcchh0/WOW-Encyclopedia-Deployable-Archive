# v34 input proposal

v34 is a preparation-only rebuild of the accepted v33 closure. It adds no
image source rows and does not inspect pending network folders. The closure
remains 459 primary overlays, 100 supplement overlays, 559 total overlays,
39 guide images, and 22 guide previews.

The only planned derived difference is the accepted exact-route contest
navigation fallback in `tools/export_github_pages.py`, bound to the root
contest-tool receipt. The source15 site and both manifests remain the frozen
inputs; v33 output is not used as the new source tree.

The future output is `.scratch/pages-resources-20261019-v34`. It must not
exist before the explicit root v34 input gate and `--go --root-export-go`.
Expected counts are 9017 declared files and 9018 actual files, subject to
root post-export acceptance.
