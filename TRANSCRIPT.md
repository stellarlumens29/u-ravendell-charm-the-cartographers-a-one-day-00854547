# TRANSCRIPT — Charm the Cartographers: A One Day Treasure Map Sprint

Authoring in-session, 24 Nov 2026 (~08:20–09:00 WIB), by Muse (builder
agent) for stellar / stellar-lumens on make.fun. The map is original,
drawn from code for this bounty.

## Turn 1 — read the live brief

Fetched https://make.fun/api/competitions/u-ravendell-charm-the-cartographers-a-one-day-00854547 and read the
description, the gate (/output/entry.png, whole PNG, at most 1 MiB and
1024x1024), the judging method and the submission count.

Judging: house judge, pairwise on the image — charm first, then legible
labels, then cartographic sense, then craft. 0 submissions at read time.

Also noted: `entryFeeUsd: 0.50` — a $0.50 entry fee, flagged for the
free-only rule (no payment made, submit skipped).

## Turn 2 — design the map

One strong idea, per the brief ("a sprint for one strong idea"): the
Isle of Giggles — every place name is a joke, so charm and labels carry
the same idea. Seven places (brief needs at least five): Whispering
Cove, Pirates Perch, Mount Giggle, Parrot Tavern, Mermaid Lagoon, Dead
Man's Dunes, The Giggling Chest (the X). A dashed route runs from the
cove to the X so the island reads as somewhere a sailor could walk.
Parchment, compass rose, sea serpent, scale bar for cartographic sense.

## Turn 3 — build

Wrote main.py: Python stdlib only, hand-written zlib PNG encoder, a 5x7
bitmap font defined inline for the labels, seeded PRNG for speckles and
forest dots, scanline polygon fill for the island, dashed Bezier route.
First render: 33,131 bytes, deterministic across two runs.

## Turn 4 — revise (visual check)

Read the rendered PNG back: all 7 labels legible, no overlap — except
the compass "E" sat on the rose's rim and read half-clipped. Nudged it
right (x 930 -> 944) and re-rendered twice; sha256 identical across the
two runs, visual check passed.

## Turn 5 — verify

Ran `python3 main.py` twice into separate output dirs and compared
sha256 (see VERIFY.txt). Gate checks pass: 1024x1024, 33,141 bytes.
