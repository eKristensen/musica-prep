# CLAUDE.md

Top-level guidance for working in this repo with Claude Code. `musica/`
has its own `CLAUDE.md` with project-specific rules once code work starts
there — this file is about how sessions in this repo should behave, not
about BluOS or Musica itself.

## The one thing this file is for

The owner of this repo uses AI tools well enough to keep finding more to
fix, which means work in an area rarely gets marked done. That is the
failure mode to actively guard against here, more than any specific
mistake.

**When asked to review, refine, or polish something that is already in
reasonable shape: say so, plainly, before offering more.** "This is good
enough to move on from" is a valid and often correct answer. Don't let a
review turn into an open-ended search for something to flag.

Concretely:

- If you're asked to find problems and the material is solid, lead with
  that assessment. Report only what's actually worth fixing — not every
  wording tweak or stylistic preference you can think of.
- Distinguish real problems (factual errors, contradictions, missing
  information someone will actually need) from taste (you'd have phrased
  it differently). Only the first kind is worth raising unprompted.
- If you notice the same document being revised for the third or fourth
  time with no substantive issue behind the latest round, say that
  directly: this looks done, further changes are diminishing returns.
- Never manufacture a finding to have something to report. "No changes
  needed" is a complete answer.
- If scope is ambiguous, ask what "done" means for the current task rather
  than defaulting to maximum thoroughness.

## Write the conclusion, not the journey to it

The second failure mode here, and it recurs constantly: when something
that was open gets settled, the writing keeps the fact that it *used* to
be open. "This closes the question X left open." "No longer an open
item." "An earlier guess was Y." "What is left: nothing."

**A settled question is just a fact. Write the fact.** The reader did not
watch the work happen and does not need the before-and-after; they need
what is true now. A document that narrates its own history makes the
reader reconstruct a timeline to extract one sentence of content — and
that narration is the part most likely to go stale, because nobody
rereads a note about something already decided.

Concretely:

- State the finding. Don't frame it as a resolution of a prior state:
  "a query has to arrive by broadcast to be acted on", not "this closes
  the question of whether unicast works".
- Delete status sections once their answer is "nothing" or "all done".
  A heading whose content is "no open items" is worse than no heading.
- Don't leave pointers to things that no longer exist — a corrected
  hypothesis, a deleted section, a renamed flag. When the thing is gone,
  the pointer is a dead end that reads like content.
- If a section only exists to say work happened, delete it. The work is
  visible in the result, and the commit history holds the rest.

**The exception is a wrong turn that could be taken again.** If knowing
why an approach failed stops someone repeating it — a control that cannot
distinguish two hypotheses, a measurement invalidated by something left
running, a conclusion that looked obvious and was wrong — keep it, and
say what it costs to get it wrong. That is not history, it is a finding.
Everything else about how the work unfolded belongs in the commit
message, not the document.

## Keep the pull request description current

A branch's PR description is created from the first commit message and
does not update itself. By the third commit it describes a fraction of
the branch, and it is what a reviewer reads first.

**After pushing, bring the description up to date with the whole branch.**
Not a commit-by-commit log — the same thing the branch's final state would
be described as if it had been written in one go, plus anything a reviewer
needs in order to decide: what was deliberately left out, and what is
someone else's call. If a later commit corrects something an earlier one
claimed, the description carries the correction, not both versions.

## Otherwise

Standard judgment applies: be accurate, flag real errors, ask when
genuinely unsure. This file overrides the instinct to keep digging once
the digging has stopped finding anything that matters — it is not a
license to skip real problems.
