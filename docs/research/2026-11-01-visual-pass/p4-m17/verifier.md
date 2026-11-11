# Map 17 second-run verification

The final build has zero strict dressing failures, zero city target failures, and zero strict visual failures. The estate passes 57 of 58 files; its sole failure is the permitted shared-install mismatch in `test_integration_state`.

`canonical-main-script.txt` restores main’s Map 17 into the final archive. The resulting SHA-256 matches main’s recorded `e7ae4760fd273a34afa06e284d905bb1a41f45d947b135057dd28406eb1b51f2`. Comparing that reference with the final archive changes Map 17 alone. The before-capture Map 17 records match main exactly.

`geometry.json` records zero changed pixels in both protected windows, all 1,731 barrier records unchanged, all pin rows unchanged, and the first 3,875 glob payloads preserved. `contracts.log.gz` verifies the explicit scene records against expanded FIXED and their provenance.

`movables.log.gz` checks the 26 requested movable reservations and the retained side chair. No movable intersects a new solid, and no introduced dressing enters their clear boxes or reach reservations.

All 80 captures have exact readback coordinates and native 640×400 surfaces. Every after-tour and set-piece image has an inspection entry tied to its SHA-256. The highest engine object counter is 10,106 of 32,511 slots.

`review-final.log.gz` contains the completed Codex review with no actionable defects. The default sandbox attempt could not create a network namespace; its startup failure is preserved separately.
