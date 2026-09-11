# Musica — protocol notes

What the code depends on, and nothing else.

## How this file is written

Add to it when an endpoint is implemented, not before. For each one, record the
request, the response shape the parser actually reads, and the traps the code
guards against. Cite the section of the reference it corresponds to, so the two
stay tied.

Write it as observed device behaviour: *the device returns X when sent Y*. Never
how any of it was found. No client class or method names, no source clients
named, no confidence markers, no provenance.

The reference (`docs/bluos-http-api.md`, not committed) is the source of truth.
This file is a subset of it, narrowed to what is built. It is expected to be
permanently incomplete. See D16.

If the device disagrees with the reference, or does something the reference does
not cover, do not write it here and do not work around it in code. Report it, so
it can go back into the reference at its own source.

---

## Endpoints

*(Nothing implemented yet.)*
