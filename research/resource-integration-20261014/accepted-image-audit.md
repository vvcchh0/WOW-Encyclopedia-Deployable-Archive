# Accepted image resource audit

This local audit covers the 19 accepted image entities from resource-resume rounds 002 and 003.
The source bodies, metadata, and frozen mirror were read without modification.

- Status: **accepted** (19/19 entities verified)
- Anchor: `20080512210044` (2008-05-12 21:00:44 UTC)
- Frozen mirror files: 8304; proposed supplement routes: 19
- Source mirror placeholder references: 67
- Latest local browser preview placeholder references: 67
- Route collisions: none; the 19 image paths are absent from the frozen file and origin indexes.

All 19 items passed raw SHA-256, base32 SHA-1/CDX digest, length, MIME/magic, Pillow verification, and temporal checks. The proposed map is supplement-only and points to the existing local raw bodies; it does not copy or rewrite the frozen site.

| Entity | Capture | Bytes | Image | Source placeholders | Preview placeholders | Use |
|---|---:|---:|---:|---:|---:|---|
| `border-bot.gif` | `20080402093136` | 1235 | GIF 124×17 | 3 | 3 | static_layout_image |
| `pixel.gif` | `20080402025616` | 43 | GIF 1×1 | 8 | 8 | static_layout_image |
| `frame-bot-bg.gif` | `20080402093145` | 4380 | GIF 121×79 | 6 | 6 | static_layout_image |
| `frame-bot-left.gif` | `20080402093154` | 4865 | GIF 139×78 | 3 | 3 | static_layout_image |
| `frame-bot-right.gif` | `20080402093138` | 4786 | GIF 139×78 | 3 | 3 | static_layout_image |
| `frame-left-bg.gif` | `20080402093136` | 6030 | GIF 78×167 | 3 | 3 | static_layout_image |
| `frame-left-bot.gif` | `20080402093145` | 3076 | GIF 78×78 | 3 | 3 | static_layout_image |
| `frame-left-top.gif` | `20080402093147` | 2998 | GIF 78×78 | 3 | 3 | static_layout_image |
| `frame-right-bg.gif` | `20080402093139` | 5478 | GIF 76×155 | 3 | 3 | static_layout_image |
| `frame-right-bot.gif` | `20080402093152` | 3013 | GIF 76×78 | 3 | 3 | static_layout_image |
| `frame-right-top.gif` | `20080402093142` | 3012 | GIF 76×78 | 3 | 3 | static_layout_image |
| `frame-top-bg.gif` | `20080402093139` | 7366 | GIF 204×71 | 3 | 3 | static_layout_image |
| `frame-top-left.gif` | `20080402093137` | 4361 | GIF 139×71 | 3 | 3 | static_layout_image |
| `frame-top-right.gif` | `20080402093135` | 4284 | GIF 139×71 | 3 | 3 | static_layout_image |
| `header-float.gif` | `20080402093134` | 8169 | GIF 261×93 | 3 | 3 | static_layout_image |
| `header.jpg` | `20080402093131` | 53689 | JPEG 602×179 | 3 | 3 | static_layout_image |
| `navbar-bot.gif` | `20080402093155` | 1250 | GIF 78×12 | 3 | 3 | static_layout_image |
| `pixel.gif` | `20080402093130` | 43 | GIF 1×1 | 6 | 6 | static_layout_image |
| `submit-button.jpg` | `20080402093130` | 6703 | JPEG 239×70 | 2 | 2 | historical_form_submit_control, presentation_only_form_image |

The `submit-button.jpg` entity is referenced by the historical form as an image submit control in the source mirror. In the latest browser preview its element is presentation-only after form staticization; restoring that image must not restore submission behavior.

The raw source paths and sanitized metadata paths are recorded in `entity-source-map.json`. HTTP headers, cookies, and transport traces are intentionally excluded from this integration record.
