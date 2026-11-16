---
layout: page
title: Claudoperation
description: Session records that show what each human contributed when AI writes most of the output.
img: assets/img/projects/problem-after.svg
importance: 1
category: claude
github: https://github.com/kakwok/claudoperation
---

When AI writes most of the output, teammates can no longer see what each human actually
contributed. **Claudoperation** fixes that with a *session record*: a short Markdown file, drafted
by Claude and approved by you, that says what you decided, corrected and originated in a session
with Claude, and which AI decisions nobody has reviewed. Teammates read it before the AI output.

<img src="{{ '/assets/img/projects/problem-before.svg' | relative_url }}" alt="Before: three people each work with a private AI chat. The shared product is large and mostly unreviewed AI output, with a few buried human lines." style="max-width:100%">

Each session becomes a short record the author approves. Teammates, and their AIs, read the
records before the product.

<img src="{{ '/assets/img/projects/problem-after.svg' | relative_url }}" alt="After: the capture skill drafts a record from each chat, the author approves it, the synthesize skill merges the records into a net story, and the product's text is tagged to its human author or marked as unreviewed AI." style="max-width:100%">

### What you approve

`/clop:approve` opens the record in a pane. You tick the claims that are accurate, fix labels, add
evidence where a label needs it, and endorse the AI decisions you checked.

<img src="{{ '/assets/img/projects/approve-pane.svg' | relative_url }}" alt="The /clop:approve pane showing an example record with approve checkboxes, label dropdowns, an evidence prompt, endorse checkboxes for AI decisions, and Save, Approve all and Cancel buttons." style="max-width:100%">

### Try it

```bash
claude plugin marketplace add kakwok/claudoperation
claude plugin install claudoperation@claudoperation
```

Then work with Claude as usual, run `/claudoperation:capture`, and `/clop:approve` to sign off.
The records from the conversation that designed Claudoperation are in the repository as worked examples.

[Source on GitHub](https://github.com/kakwok/claudoperation)
