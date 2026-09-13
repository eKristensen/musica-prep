# Working on `lsdp-static`

## Bump the version when you change behaviour

`Cargo.toml`'s `version` is the only place the version is written —
`const VERSION` reads it through `env!("CARGO_PKG_VERSION")`, so the two
cannot drift. What is still manual is remembering to raise it.

**It has already been forgotten once.** `--broadcast` was renamed `--to` and
released as `1.0`, so every run saved by that build claims a version whose
published behaviour it does not have. A saved run under `test-runs/` is only
reproducible if the version in its `REPORT.md` identifies the code that
produced it, which is the whole reason the field is there.

So: if a change alters what the program does — a flag, an output format, the
wire codec, a default — raise `version` in `Cargo.toml` in the same commit.
Patch for a fix, minor for a new or renamed flag. Refactors and comment
changes need nothing.

Check with `cargo build --release && ./target/release/lsdp-static version`
before committing, and run `selftest` — it has 38 assertions and needs no
network or hardware.
