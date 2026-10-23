# Animation parameters

## Water (V8 refined candidate)

`create_v8_refined.py` keeps the edit inside a conservative polygon mask with an inward min-filter and soft edge. Reflection brightness field has three sinusoidal spatial terms and amplitude 1.6% (`factor = 1 + 0.016 * field * alpha`). It does not displace the shoreline. If the source V7 differs in crop or alignment, recheck the mask before use; the polygon is specific to the known 1280×720 composition.

## Meteors (V9/V10)

Edit the `events` records in `create_v9.py`: `start`, `duration`, `tail`, `decay`, and four Bézier control points. The render function places the tail opposite the travel tangent. V10's `events` in `create_v10.py` use x decreasing and y increasing for both tracks. Keep `old_events` aligned with old tracks only when cleaning a known V9 input.

## Point star (V11)

In `create_v11.py`, adjust `P0`, `P1`, `START`, `END`, fade times, `COLOR`, and core/halo strengths. Current path moves from (730,35) to (700,65) over the clip, with entry/exit fades. `tests/test_v11_star.py` verifies down-left monotonic travel, loop-seam absence, and a compact local overlay.

Cat-tail and lantern motion cannot be independently tuned from the available source files: those pixels are already combined in the source MP4.
