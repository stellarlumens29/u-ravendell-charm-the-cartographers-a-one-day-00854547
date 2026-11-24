# Charm the Cartographers: A One Day Treasure Map Sprint

make.fun bounty — prize $15, deadline 01:25 WIB, 25 Nov 2026.
Bounty page: https://make.fun/bounty/u-ravendell-charm-the-cartographers-a-one-day-00854547

NOTE: this bounty carries a $0.50 entry fee (`entryFeeUsd: 0.50` in the live
brief) — see FREE-ONLY note below.

## The entry

One picture: a treasure map of a fictional island, the Isle of Giggles,
drawn entirely from code. Seven labelled places, all legible:

- WHISPERING COVE (north coast inlet)
- PIRATES PERCH (north-west cliff)
- MOUNT GIGGLE (snow-capped peak, centre)
- PARROT TAVERN (east coast)
- MERMAID LAGOON (west lagoon)
- DEAD MAN'S DUNES (south-east dunes)
- THE GIGGLING CHEST (the big red X, end of the dashed route)

Plus a compass rose, a sea serpent ("HERE BE GIGGLES"), birds, waves,
palm trees and a "ONE LEAGUE" scale bar, on aged parchment with a double
border.

Gate: `/output/entry.png`, whole PNG, 1024x1024, 33,141 bytes (limit
1,048,576) — passes.

## Brief (live, read 24 Nov 2026 ~08:20 WIB)

Judging: house judge, pairwise on the image — charm first, then legible
labels, then cartographic sense, then craft; Swiss rounds vs other entries
and fixed house images, then a playoff. 0 submissions at read time — the
field is empty, so a charming, legible, coherent map is the whole game.

Top-entry pattern: none yet (0 subs). The brief's own order is the guide:
charm first — so the map leans into jokes in the place names (every name
is a giggle) and a hand-drawn storybook feel rather than realism.

## Run

```sh
python3 main.py
```

Writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` when set, otherwise to
`/output/entry.png`. Python standard library only — no network, no
randomness beyond a fixed seed, no timestamps — so running it twice
produces byte-identical output (verified, sha256 in VERIFY.txt).

## Determinism

See `VERIFY.txt` for the two-run sha256 comparison and the visual check.

## FREE-ONLY note

The live brief lists `entryFeeUsd: 0.50`. No payment was made and no
submit was attempted for this bounty on the free-only rule; the build +
push are free, the submit step is SKIPPED pending the user's call on the
$0.50 entry fee.
