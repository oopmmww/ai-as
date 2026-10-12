---
name: opencv-offline-validation
description: Validate general OpenCV image-processing code on local sample images or synthetic fixtures. Use for HSV/color conversion correctness, masks, contours, image input validation, reproducibility, or performance profiling of offline CV pipelines.
---
# OpenCV Offline Validation

## Scope
Use recorded sample images or synthetic test fixtures. Keep this skill focused on generic image-processing correctness and performance diagnostics, not identifying or tracking players in competitive games or improving automated aiming.

## Workflow
1. Inspect the existing pipeline and document expected input type, shape, channel order, dtype, and output contract.
2. Add fixtures covering valid images, empty/None inputs, unexpected channel counts, wrong dtype, low/high intensity, and edge/boundary values.
3. Check BGR/RGB assumptions; OpenCV's common 8-bit HSV representation uses H=0..179 and S/V=0..255. Verify the code's actual conversion and bounds before changing them.
4. Assert output dimensions/dtypes and mask semantics. Check lower/upper bounds, empty masks, and contour-free images.
5. Measure stages independently using a monotonic high-resolution timer such as `time.perf_counter()`. Warm up if relevant and run repeated trials; report median and spread rather than one timing.
6. Compare results against a fixed baseline fixture set. Separate accuracy changes from speed changes.
7. Avoid optimizing based on intuition; retain a change only when correctness stays intact and the measurement supports it.

## Output
Summarize test fixtures, edge cases, measured timings, regression risks, and tests run. Do not tune parameters for game-player targeting or automated game input.
