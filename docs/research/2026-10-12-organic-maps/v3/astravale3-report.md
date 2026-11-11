# Vale round 3 research

Research-only; all outputs here, repository and shared/build read-only.

## Iteration log
| Iteration | Raw items | Dressing | Hoskuld/Gunnar dirt | Pins | Reach |
|---|---:|---:|---|---|---|
| 1 | 24,447 | 1,170 | 90.4% / 68.5% | 65/65 | not run |
| 2 | 23,274 | 2,447 (8.51/100 tiles) | 76.5% / 68.5% | 65/65 | **13/13**, offline 16-unit exact flood |

## Changes vs round 2
Winding silhouette, T1 arms, T2 horseshoe/back wall, z64 south shelf and 8-unit ramp, NW 48-step backdrop to 288; three-lobe lake; grey highlands and broad earth sheets; grouped mushroom beds, ruins and temple gargoyle stair. Kept existing red keep (replacement remains a user decision). All 68 pin records retained exactly, including 65 positioned records. Water ground stays inside original lake rectangle; pier foot y=20480.

Critical new finding: v2 selected cliff frames generically. Contact sheet `iter01_cliff_frames.png` shows 27/28/30/31 frames 2/3 are BLACK, 5/6 invalid for several shapes; 29 frame6 is black. Iter2 uses textured 0/1/4 for short faces and excludes 29:6. Campfire corrected from misidentified 399 to catalogued 267.

## Visual evidence
`iter02_whole_map.png`; `iter02_pair_screen{19,20,21,22,18,17,02}.png`, plus circle/shelf/NW. Iter01 equivalents retained. Every comparison: RefArtCatalog/x3 + round2 same camera + v3 native 320×186 ×3 nearest. Scale faithful; no engine paint-order claim.

## Reachability
`reach.json`: seed (12800,2560,0), body 64×64×40, grid16, lava margin128; Sacred Circle, Ezrekal wall/NPC, cloud207, temple211, Pagan213, dungeon204, Hoskuld, Gunnar well, Hrodny chest, lake causeway, Passage plant and Ragnar cache all reached. 4.66s. Offline geometry only; not swept-segment, NPC/door, paint sorting or fall safety certification.

## Remaining iteration work
Still above 22k budget; Hoskuld slightly above 75%. Reintroduce back faces reviewer correctly flagged as visible on ridge corners, optimize actual redundant lips/short splits instead. Camera20 now shows cliff arm but needs a coherent dirt camp composition. Temple's inherited pale paving and fragment walls obscure new stair; remove unpinned obsolete masonry in mock. No claim of finished visual match yet.
