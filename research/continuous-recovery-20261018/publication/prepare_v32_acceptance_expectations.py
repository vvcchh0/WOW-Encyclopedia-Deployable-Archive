"""Add the reviewed runtime and three compatibility-mask changes to the image forecast."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base_path = PUB/'v32-export-expectations.json'
dest = PUB/'v32-acceptance-expectations.json'
assert not dest.exists()
base = json.loads(base_path.read_bytes())
assert base['accepted'] and base['removed_static_occurrences'] == base['removed_static_unique_addresses'] == 103
assert not base['assets_without_current_static_marker']
mask_path = PUB/'root-attunement-mask-tool-acceptance.json'
assert sha(mask_path) == '8c295a243993353de30ea8173ef5e8530656c65acdbbf0785855eadb14eefa24'
mask = json.loads(mask_path.read_bytes())
assert mask['accepted'] and mask['compatibility_references_replaced'] == 3
impact_path = PUB/'root-v31-runtime-impact.json'
assert sha(impact_path) == '6b11f2b3b3c5b9d00aec1ad2433b047da30f7582877defedc20f73d4830a9401'
impact = json.loads(impact_path.read_bytes())
assert impact['accepted'] and len(impact['affected_pages']) == 5
base['source_bindings'].extend({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in [base_path, mask_path, impact_path])
base['allowed_changed_output_paths'] = sorted(set(base['allowed_changed_output_paths']) |
    {p['output_path'] for p in impact['affected_pages']} | {'new-hp/js/enhancedtip.js'})
base['expected_static_counts']['missing_occurrences'] -= 3
assert base['expected_static_counts'] == {'static_text_files': 1104, 'unique_missing_images': 930,
    'missing_occurrences': 1573, 'news_unique_missing_images': 387, 'news_missing_occurrences': 387}
base['derived_compatibility_change'] = {'route': '/bcattunement/index.html', 'missing_occurrences_removed': 3,
    'unique_addresses_removed': 0, 'remaining_legacy_pixel_references': 2, 'new_original_images': 0}
base['scope'] += ' Add the separately accepted retired-tooltip and real-body banner fixes, plus three transparent compatibility mask references; the two legacy pixel markers remain.'
dest.write_text(json.dumps(base, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'sha256': sha(dest), 'expected_static_counts': base['expected_static_counts']}))
