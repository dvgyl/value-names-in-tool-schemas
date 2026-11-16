# Operator coding of the Track P sample (addendum to registration A)

Registration A: https://osf.io/bv8q9. This addendum is filed with registration B, before the operator freezes the first codes.

- The operator codes the 144 sample dialogues blind, in the registered order, with the codebook that registration A, section 7a, registered for the annotator models: `annot/codebook.md`, SHA-256 `bff44f7a881d84e3327f76021eb6b21f834935d584f4a62cd04a4ce837613154`. The SI-10 codebook of PLAN revision 11 was not written; this text takes its place. Coder id `operator`.
- Coding tool `main/trackp_coding/` (SHA-256: `serve.py` f94e7162d2f5be64b7df72544a2837dbf4eb6cb8553a08b5382a8f147c68eeb0, `index.html` 3fb5e00d71e574ebf316f594a749f6b9dae75c35bd2f6252e7844d97b2785fb0, `build_export.py` 4c3f172a6857ec0ef4a8f0143488d973fe2b125791de6c039f9fb6253a1e947c; blind export `export.json` e8a102837ce40640cd1a709c7f2c898bb902e0484447a0df4b94b13ba0ddd927).
- Test-retest (PLAN SI-10): when the first codes are frozen, the tool draws ceil(0.2 x 144) = 29 dialogues. Seed = the first 16 hex digits of SHA-256("Semantic Integrity revision 12, Track P test-retest, 2026-11-13" + newline + the SHA-256 of the frozen code file), as an integer; `random.Random(seed).sample(sorted(sample), 29)`. The operator re-codes them blind (coder id `O2`) 14 or more calendar days (India time) after the day of the freeze. The re-code never shows a first code.
- The first codes, the annotator codes, the corpus labels and every Track P result stay hidden until the re-code is frozen.
