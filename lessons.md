# Lessons Learned

> Mistake → correction pairs. Read at session start to avoid repeating.
> Added to by the LLM after every correction from the user.
>
> Format:
> ```
> ## YYYY-MM-DD — {short title}
> **Mistake**: {what I did wrong}
> **Correction**: {what I should have done}
> **Rule**: {generalized guidance for future sessions}
> ```

<!--
  Starter lessons (delete/replace as you accumulate your own):
-->

## {{YYYY-MM-DD}} — {{example: fabricated a name that wasn't in the source}}
**Mistake**: I wrote `jane-smith` as an attendee when the transcript only listed initials `JS`.
**Correction**: When names are ambiguous, flag with `_(to confirm)_` and ask the user before creating a `people/` page.
**Rule**: Never cristallize a name from an ambiguous source. Flag inline with `_(to confirm)_` or use a `> [!gap]` callout.
