# Gallery coverage supplement r2

This is an offline supplement to coverage-ledger.json; the v1 files remain unchanged. The audit made zero external requests.

The local publication scan found only two accepted late-prefix source receipts. The first queried Karazhan (20090101000000..20101207235959), Zul'Aman (20080512210045..20101207235959), and Black Temple (20080512210045..20101207235959): Zul'Aman completed with 63 CDX rows and 29 nested image rows, while Karazhan and Black Temple produced no valid index. The retry-2 receipt queried only Karazhan and Black Temple and stopped on 503; both still had zero valid rows. No later successful receipt naming either window exists in the local publication/status set. Therefore the two windows remain transport_unknown, not payload 404.

The native Karazhan replay ledger is a different coverage layer: 114 archive replay 404, 12 observed redirect classifications, and zero transport unknown remain after NET35–38. It does not close the late prefix index gap. The two r2 plans therefore contain exactly the unresolved Karazhan and Black Temple prefix literals and exclude Zul'Aman.

The frozen dungeon pages give these exact source literals:

| gallery | page evidence | declared slots | exact native prefix |
| --- | --- | ---: | --- |
| Karazhan | karazhan-gallery.html:60 numShots = 63; and :126 addshots("/info/dungeons/images/karazhan/","ss",numShots); | 63 | http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ |
| Black Temple | black-temple-gallery.html:60 numShots = 48; and :112 addshots("/info/dungeons/images/blacktemple/","ss",numShots); | 48 | http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/ |
| Zul'Aman | zulaman-gallery.html:60 numShots = 60; and :123 addshots("/info/dungeons/images/zulaman/","ss",numShots); | 60 | http://www.worldofwarcraft.com/info/dungeons/images/zulaman/ |

guidegallery-screenie.js constructs the source family as sourceDirectory + filename + number + ".jpg" and derives the preview with .replace(".jpg","-thumb.jpg"). This explains the page behavior but is not a capture row. No individual full-size target is added from that rule alone.

An evidence-based mechanism hypothesis is that the player gallery resources were assembled dynamically, while guide previews were present as static page-linked routes. That difference is consistent with an archive discovery gap and explains why repeating the same failed prefix points is unlikely to add information. It remains an inference from the JS, saved preview map, and incomplete CDX results; it does not prove the historical crawler cause or turn an unknown prefix into 404.

The accepted Karazhan related map contains only these preview URLs: http://.../karazhan/thumbs/ss2-thumb.jpg, http://.../karazhan/thumbs/ss3-thumb.jpg, and https://.../karazhan/thumbs/ss1-thumb.jpg. Their saved 2008 captures are already covered; the HTTPS form remains a separate source variant. The accepted Zul'Aman guide map contains three .../zulaman/thumbs/ss[1-3]-thumb.jpg previews. The saved regional page inventory contains a wow-europe Screenshot of the Day page, not a dungeon-region source, and the next regional image map is empty. No saved regional page supplies an unqueried Karazhan/Black Temple full-size target.

The twelve late-2013 rows require narrower wording. The queue/CDX batches describe twelve literal thumbnail replay rows. Only ss1-thumb.jpg at 20130612155549 was actually replayed for a Location header, which pointed to the archived Battle.net guide and was not followed. The other eleven destinations are unobserved; they are not confirmed redirect targets.

The two JSON plan slices are review packets. They reuse the frozen retry-2 driver hash and 15/15 offline fixture result. That driver intentionally validates the exact pair {Karazhan, Black Temple}; a one-target packet must not be passed to its --execute entry point. A later root-approved paired plan can combine these two immutable slices. No network command was run here.
