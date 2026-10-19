# Preserved v35 preparation failure

The first `build_pages_v35.py --prepare --preflight` invocation stopped before
writing the final closure/preparation/preflight files.  The current exporter
loader was called with the complete frozen map route set as `frozen_routes`,
so it correctly rejected the first closure entry as if it were a new route:

`wow_recovery_v35_exporter.PagesExportError: entity-source-map.json[0] would override an existing route: /visa/reward/images/border-bot.gif`

The generated primary, supplement, and native-input bytes are retained here
for audit.  The retry changes only the preflight call: it loads the frozen
closure with an empty collision baseline, then loads the new v35 maps against
the frozen route/static baseline.  No export or network request occurred.
