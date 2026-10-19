# Formal application versus frozen candidates

The Visa structure follows the frozen `integration/visa-exhibit/visa-exhibit.patch`:
the same canonical route, two aliases, six accepted image routes, P0 dispatch,
local archive/rewards links, and removal of source business controls. The formal
production copy changes only the product-facing prose from the candidate:

- the notice is the concise historical description requested for the product;
- the candidate's repeated paragraph about recovered bytes and unavailable
  interaction is omitted;
- each image receives a short specific caption (`upper frame`, `lower frame`,
  `historical offer panel`, or `title heading`) instead of a repeated disclaimer.

The formal historical test extends the candidate checks with alias equivalence,
reward-route isolation, ordinary-route isolation, and a direct idempotence
assertion. The existing reward P0 tests and the source-structure P1 regression
remain in place.

The workspace-budget candidate directory was not present in this checkout. The
approved production change is the two-line conditional around the existing
before/after `workspace_size()` calls; its formal regression covers uncapped
skip behavior, finite before/after rejection, and both pre/post disk-floor
checks.
