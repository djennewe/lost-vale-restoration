# Cloud City and mountain summit — round 3

Research-only; repository and shipped artifacts untouched. Everything here builds on copied round-2 code/art.

## Iteration 1 — rendered and reviewed
Native 320×186 crops and ×3 nearest-neighbour catalog pairs: `iter01_m17_pair_screen11.png`, `...screen12.png`, `...screen13.png`, `iter01_m13_pair_screen01.png`, `...screen16.png`; whole map `iter01_m17_whole.png`.

Counts: Map17 5,772 items; Map13 8,230. Pin accounting: Map17 11 placed pins exact + 2 deliberately absent/deferred unchanged; Map13 11/11 exact. Full pin tuples and exports in `iter01_pins.json` and `iter01_map{13,17}_items.json`. No engine or reachability run.

Changes: 862's actual three-colour palette, four fills; desaturated gold; every macro rim/contact sampled at 64 units with 880/881 round lobes; connected processional cloud sea; raised Y walkway/terraces, 192-unit colonnades, radius420 gem ring, 3×3 + 2×2 drums, furnishings; summit sheet, gold corner, full 26–32 family. Family sizes are NOT interchangeable: 26/32 faces are partitioned into matching 27/28/29 or 31/30/29 runs preserving the original box.

Visual review finds needed iteration: cloud texture too striped; gold forum wrongly dominates screen11 (needs cloud directly under ring, gold south of it); court furniture not clustered tightly enough; old summit columns obscure the requested cloud; climb retains large black facade patches and is not close to screen16. Native crop background-colour counts are not a measure of those opaque black patches. Initial uncached palette generation timed out before rendering; memoizing exact palette matches reduced the successful render pass to 9.25s.

`art_contracts.json` contains proposed 874–881 donor/footpad/frame/flag contracts, not installed art. Ground-first compositing is an offline design view, not ScummVM sort evidence. Further iteration follows.
