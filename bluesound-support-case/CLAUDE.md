# CLAUDE.md — bluesound-support-case

## Do not wrap lines in this folder

The `.txt` files here are the emails as they are sent and received. A draft is
copied straight into the support portal, so hard-wrapped prose has to be
un-wrapped by hand before it can go out.

**Keep each paragraph, section or list item on one line, however long.** No
fills, no reflowing, no 80-column wrapping. This applies to every file in this
folder and to nothing outside it.

## Conventions

Every message gets its own number, in the order the exchange happened —
theirs and mine alike, never a shared number for a response and its reply —
with `-sent-` or `-support-response-` and the date. A draft is `NN-reply-draft.txt` and carries a
`Status: DRAFT — not sent` line under the subject; on sending it is renamed to
`NN-reply-sent-<date>.txt` and that line becomes `Sent: <date>`.

## What may be used as evidence in these emails

**Only measurements taken here, and the vendor's own material.** Nothing from
third-party open-source BluOS projects: unofficial work carries no weight with
the company, and citing it invites an argument about the source instead of the
finding. Nothing read out of a shipping app either — that is against its EULA,
and they are better placed to find it themselves.

**A measurement supports claims about what was measured, and nothing past it.**
Timings taken on the wire say what the players did. They say nothing about what
the controller app does with an answer once it arrives — how long it listens,
what it waits for, when it subscribes. State the observation and stop; the
reader can draw the inference.
