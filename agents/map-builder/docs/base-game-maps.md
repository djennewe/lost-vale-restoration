# Base Game Map Catalog

Analysis of all 42 non-empty maps in FIXED.DAT from the GOG Ultima 8 Gold Edition.
See `map-format.md` for the format specification.

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total maps allocated | 256 |
| Non-empty maps | 42 |
| Total items across all maps | 86,610 |
| Available slots for Lost Vale | 214 |
| Map 10 (LV overworld target) | **Empty — available** |

## Map Connectivity Graph

Traced from teleport egg pairs (TRIGGER frame=1 → DEST frame=0):

```
                                    ┌─── Map 63
                                    │
              Map 3 ← Map 40 ─── Map 7 ─── Map 8 (Plateau / LV entry)
                        │  │
                  Map 39 │  Map 41
                    │    │    │
                  Map 4  │  Map 5 ─── Map 6 ─── Map 50
                         │                        │  │  │
                         │                   Map 51  │  Map 54
                         │                     │     │
                         │                   Map 57  Map 62
                         │                     │
                         └─── Map 21 ──────────┘
                               │
                             Map 31
                               │
                             Map 49 ─── Map 37

    Dungeons/Interiors: Maps 12─14─15, 16─26─28, 43─44─45─46─47
    Minimal/Test: Maps 20, 29, 33, 56, 159, 200, 222, 223, 243, 255
```

Maps 43–47 form a hub-and-spoke pattern (Map 43 has destinations to 44, 45, 46,
47 — likely the Sorcerers' Enclave / Catacombs).

## Individual Map Profiles

### Map 3
- **Items:** 1,835 (875 globs, 960 placed)
- **Unique shapes:** 82
- **Span:** ~44 x 26 chunks
- **Bounding box:** X=[1215, 23839] Y=[287, 13887] Z=[-128, 120]
- **Teleports:** 3 (connects to Map 40)
- **Monster eggs:** 13

### Map 4
- **Items:** 4,377 (1,543 globs, 2,834 placed)
- **Unique shapes:** 168
- **Span:** ~42 x 61 chunks
- **Bounding box:** X=[1535, 23167] Y=[639, 32031] Z=[-128, 112]
- **Teleports:** 10 (connects to Maps 39)
- **Containers:** 3
- **Monster eggs:** 27

### Map 5
- **Items:** 2,691 (772 globs, 1,919 placed)
- **Unique shapes:** 44
- **Span:** ~24 x 42 chunks
- **Bounding box:** X=[2623, 15359] Y=[10943, 32767] Z=[-128, 88]
- **Teleports:** 6 (connects to Maps 6, 41)
- **Monster eggs:** 35

### Map 6
- **Items:** 2,908 (863 globs, 2,045 placed)
- **Unique shapes:** 128
- **Span:** ~39 x 24 chunks
- **Bounding box:** X=[479, 20639] Y=[18815, 31551] Z=[-120, 120]
- **Teleports:** 4 (connects to Maps 5, 50)
- **Containers:** 3
- **Monster eggs:** 9

### Map 7
- **Items:** 2,230 (1,079 globs, 1,151 placed)
- **Unique shapes:** 67
- **Span:** ~41 x 53 chunks
- **Bounding box:** X=[1279, 22399] Y=[4735, 32127] Z=[-128, 120]
- **Teleports:** 6 (connects to Maps 8, 40, 63)
- **Containers:** 1
- **Monster eggs:** 30

### Map 8 — Plateau (Lost Vale Entry Point)
- **Items:** 4,306 (1,414 globs, 2,892 placed)
- **Unique shapes:** 152
- **Span:** ~61 x 60 chunks (nearly full-size map)
- **Bounding box:** X=[1023, 32735] Y=[1055, 31775] Z=[-128, 120]
- **Teleports:** 15 (connects to Maps 7, 8-internal)
- **Containers:** 3
- **Monster eggs:** 19

**Detailed teleport analysis (LV-relevant):**

| Role | Position | Quality | NPC | Target Map | Notes |
|------|----------|---------|-----|------------|-------|
| TRIGGER | (31583,19135,0) | 0 | — | — | Near east edge → Map 7 |
| DEST | (31871,19167,0) | 257 | 84 | 7 | From Map 7 arrival |
| TRIGGER | (29375,30015,0) | 2 | — | — | South-east corner → internal |
| DEST | (29407,30335,0) | 257 | 69 | 8 | Internal transition |

The double doors for LV access are in Bonecrusher's Cave area. A new teleport
egg pair would need to be added:
- TRIGGER on Map 8 at the double door location
- DEST on the new Beyond Double Doors map (e.g., Map 11)

**Top shapes in Map 8:**

| Shape | Count | Type | Description |
|-------|-------|------|-------------|
| 2 | 1,414 | GLOBEGG | Terrain globs |
| 794 | 274 | GENERIC | Terrain feature |
| 26 | 174 | GENERIC | Wall/cliff (solid, drawable) |
| 32 | 153 | GENERIC | Wall/cliff (solid, drawable) |
| 466 | 136 | GENERIC | Terrain (solid) |
| 301 | 120 | GENERIC | Wall (solid, drawable) |
| 347 | 116 | GENERIC | Water/terrain (solid) |
| 65 | 96 | GENERIC | Rock/terrain (solid) |
| 3 | 92 | GENERIC | Ground (solid) |
| 125 | 90 | GENERIC | Cliff face (solid, drawable) |

### Map 12
- **Items:** 2,410 (1,085 globs, 1,325 placed)
- **Unique shapes:** 78
- **Span:** ~35 x 19 chunks
- **Teleports:** 9 (connects to Map 14, internal)
- **Containers:** 5

### Map 14
- **Items:** 2,956 (1,217 globs, 1,739 placed)
- **Unique shapes:** 66
- **Span:** ~49 x 46 chunks
- **Teleports:** 2 (connects to Map 12)
- **Monster eggs:** 28

### Map 15
- **Items:** 2,400 (526 globs, 1,874 placed)
- **Unique shapes:** 82
- **Span:** ~26 x 26 chunks
- **Teleports:** 2 (connects to Map 5)
- **Containers:** 2
- **Monster eggs:** 19

### Map 16
- **Items:** 1,052 (664 globs, 388 placed)
- **Unique shapes:** 34
- **Span:** ~33 x 41 chunks
- **Teleports:** 5 (connects to Maps 28, 49)

### Map 20
- **Items:** 596 (567 globs, 29 placed)
- **Unique shapes:** 9
- **Span:** ~27 x 59 chunks
- **Notes:** Mostly terrain — sparse map

### Map 21
- **Items:** 2,665 (458 globs, 2,207 placed)
- **Unique shapes:** 53
- **Span:** ~20 x 31 chunks
- **Teleports:** 6 (connects to Maps 31, 49, 57)
- **Monster eggs:** 7
- **Notes:** Hub connecting three major areas

### Map 24
- **Items:** 558 (344 globs, 214 placed)
- **Unique shapes:** 19
- **Span:** ~23 x 30 chunks

### Map 25
- **Items:** 1,044 (489 globs, 555 placed)
- **Unique shapes:** 29
- **Span:** ~25 x 30 chunks

### Map 26
- **Items:** 1,355 (661 globs, 694 placed)
- **Unique shapes:** 37
- **Span:** ~26 x 33 chunks
- **Teleports:** 5 (connects to Maps 28, 49)
- **Monster eggs:** 16

### Map 28
- **Items:** 1,369 (725 globs, 644 placed)
- **Unique shapes:** 54
- **Span:** ~31 x 23 chunks
- **Teleports:** 10 (connects to Map 16, internal)
- **Monster eggs:** 7

### Map 29
- **Items:** 150 (130 globs, 20 placed)
- **Unique shapes:** 9
- **Span:** ~16 x 6 chunks — small area

### Map 31
- **Items:** 3,663 (1,395 globs, 2,268 placed)
- **Unique shapes:** 87
- **Span:** ~60 x 57 chunks (large)
- **Teleports:** 7 (connects to Map 21)
- **Monster eggs:** 12

### Map 33
- **Items:** 131 (0 globs, 131 placed)
- **Unique shapes:** 11
- **Span:** ~8 x 11 chunks — small interior, no globs
- **Notes:** Only map with zero glob eggs — all items placed individually

### Map 37
- **Items:** 5,054 (1,576 globs, 3,478 placed)
- **Unique shapes:** 165
- **Span:** ~58 x 52 chunks (large outdoor)
- **Teleports:** 7 (connects to Map 49)
- **Containers:** 6
- **Monster eggs:** 24

### Map 39
- **Items:** 4,624 (973 globs, 3,651 placed)
- **Unique shapes:** 181 (most diverse)
- **Span:** ~22 x 41 chunks
- **Teleports:** 6 (connects to Maps 4, 40)
- **Containers:** 17
- **Monster eggs:** 3
- **Notes:** High container count suggests a city/town map (likely Tenebrae)

### Map 40
- **Items:** 1,963 (638 globs, 1,325 placed)
- **Unique shapes:** 120
- **Span:** ~29 x 32 chunks
- **Teleports:** 17 (highest count — major hub)
- **Containers:** 9
- **Monster eggs:** 4
- **Notes:** Central hub connecting Maps 3, 7, 39, 41

### Map 41
- **Items:** 3,859 (941 globs, 2,918 placed)
- **Unique shapes:** 188 (second most diverse)
- **Span:** ~40 x 43 chunks
- **Teleports:** 6 (connects to Maps 5, 40)
- **Containers:** 21 (highest count)
- **Monster eggs:** 12

### Map 43 — Dungeon Hub
- **Items:** 784 (260 globs, 524 placed)
- **Unique shapes:** 23
- **Span:** ~14 x 14 chunks
- **Teleports:** 4 (DEST only — leads to Maps 44, 45, 46, 47)
- **Monster eggs:** 3
- **Notes:** Hub with four exits — likely Sorcerers' Enclave entrance

### Map 44
- **Items:** 2,523 (864 globs, 1,659 placed)
- **Unique shapes:** 96
- **Span:** ~33 x 40 chunks
- **Teleports:** 1 (connects back)
- **Containers:** 1
- **Monster eggs:** 27

### Map 45
- **Items:** 1,276 (739 globs, 537 placed)
- **Unique shapes:** 28
- **Span:** ~45 x 41 chunks
- **Teleports:** 1

### Map 46
- **Items:** 385 (240 globs, 145 placed)
- **Unique shapes:** 14
- **Span:** ~5 x 10 chunks (narrow)
- **Teleports:** 1

### Map 47
- **Items:** 2,442 (1,246 globs, 1,196 placed)
- **Unique shapes:** 52
- **Span:** ~46 x 28 chunks
- **Teleports:** 1
- **Monster eggs:** 24

### Map 49
- **Items:** 4,447 (947 globs, 3,500 placed)
- **Unique shapes:** 121
- **Span:** ~44 x 49 chunks
- **Teleports:** 7 (connects to Maps 21, 37, 50)
- **Monster eggs:** 16

### Map 50
- **Items:** 4,555 (1,114 globs, 3,441 placed)
- **Unique shapes:** 167
- **Span:** ~58 x 62 chunks (nearly full-size)
- **Teleports:** 14 (connects to Maps 49, 51, 54, 62)
- **Monster eggs:** 15
- **Notes:** Large hub area, connects to many maps

### Map 51
- **Items:** 2,507 (864 globs, 1,643 placed)
- **Unique shapes:** 83
- **Span:** ~53 x 36 chunks
- **Teleports:** 8 (connects to Maps 50, 57)
- **Monster eggs:** 4

### Map 54
- **Items:** 1,729 (617 globs, 1,112 placed)
- **Unique shapes:** 84
- **Span:** ~20 x 31 chunks
- **Teleports:** 2 (connects to Map 50)

### Map 56
- **Items:** 182 (130 globs, 52 placed)
- **Unique shapes:** 10
- **Span:** ~7 x 3 chunks — tiny area

### Map 57
- **Items:** 4,257 (1,229 globs, 3,028 placed)
- **Unique shapes:** 117
- **Span:** ~45 x 43 chunks
- **Teleports:** 12 (connects to Maps 21, 51)
- **Monster eggs:** 28

### Map 62
- **Items:** 5,715 (2,076 globs, 3,639 placed)
- **Unique shapes:** 114
- **Span:** ~60 x 59 chunks (largest map by item count)
- **Teleports:** 7 (connects to Map 50)
- **Monster eggs:** 25

### Map 63
- **Items:** 752 (206 globs, 546 placed)
- **Unique shapes:** 57
- **Span:** ~8 x 22 chunks (narrow)
- **Teleports:** 2 (connects to Map 7)
- **Containers:** 1
- **Monster eggs:** 4

### Map 159
- **Items:** 3 (2 globs, 1 placed)
- **Span:** ~0 x 0 chunks — test/debug map

### Map 200
- **Items:** 36 (36 globs, 0 placed) — glob-only test

### Map 222
- **Items:** 87 (74 globs, 13 placed)
- **Span:** ~52 x 46 chunks — sparse overlay

### Map 223
- **Items:** 1,233 (1,188 globs, 45 placed)
- **Span:** ~37 x 56 chunks — mostly terrain

### Map 243
- **Items:** 14 (3 globs, 11 placed)
- **Span:** ~1 x 1 chunks — tiny test area

### Map 255
- **Items:** 480 (480 globs, 0 placed) — glob-only

## Map Size Reference for Lost Vale Design

Typical map sizes from base game:

| Category | Examples | Chunk Span | Item Count |
|----------|----------|------------|------------|
| Small interior | Maps 29, 33, 56, 243 | 1-16 chunks | 14-182 |
| Medium interior | Maps 46, 63 | 5-22 chunks | 385-752 |
| Medium area | Maps 24, 25, 28, 43, 54 | 14-31 chunks | 558-1,729 |
| Large area | Maps 3, 5, 6, 7, 12, 15, 41, 49, 57 | 26-60 chunks | 1,835-4,447 |
| Full-size exterior | Maps 8, 31, 37, 50, 62 | 52-62 chunks | 3,663-5,715 |

**Recommendations for Lost Vale maps:**

| LV Map | Suggested Size | Reference |
|--------|---------------|-----------|
| Map 10: LV overworld | Full-size (~60x60 chunks) | Like Map 8 or 50 |
| Galjeron's Chamber | Small interior (~8x8 chunks) | Like Map 63 |
| Elemental Dungeon | Large area (~40x40 chunks) | Like Map 49 |
| Cloud Cliffs | Medium area (~20x30 chunks) | Like Map 54 |
| Cloud City | Medium-large (~30x30 chunks) | Like Map 28 |
| Ancient Temple | Medium interior (~15x15 chunks) | Like Map 43 |

## Available Map Slots

The following map indices are empty and available for new content:

**Low range (0-63):** 0, 1, 2, 9, 10, 11, 13, 17, 18, 19, 22, 23, 27, 30, 32,
34, 35, 36, 38, 42, 48, 52, 53, 55, 58, 59, 60, 61

**Mid range (64-158):** All 95 slots empty

**High range (160-254):** 161-199 (39 slots), 201-221 (21 slots), 224-242 (19 slots), 244-254 (11 slots)

**Confirmed allocation:** Map 10 = Lost Vale overworld (from usecode `MapLostVale`)
