You classify how a microgravity flammability test ended, using only the observation text of one test (NASA BASS-II, solid-fuel flame spread in a spacecraft experiment). You work alone and see no other rating.

Choose exactly one class:
- no_ignition: the text says the sample did not ignite, or no flame could be sustained and no flame is described.
- self_extinguished: a flame existed and went out while the flow was still on, including blowoff, quench limits found by stepping the flow down (flow not zero), and brief flames that died. Extinction at a non-zero reduced flow counts as a measured limit.
- burned_to_completion: the text says the sample burned entirely or completely.
- externally_terminated: the operator ended the burn while the flame was still burning or by switching the flow off or to zero (also running out of camera card, loss of signal). This is censored: it is not an extinction.
- other: a procedure or equipment issue makes none of the above clear.
- unknown: the text has no outcome (appearance, instrument or oxygen notes only, no end state, or no text).

Confidence: high = the text states the end state plainly; medium = the end state is stated but needs an interpretation (for example extinction while the flow was being reduced); low = the text is ambiguous.
Do not use outside knowledge and do not guess an end state that the text does not give.

Return one JSON object and nothing else:
{"class": "<one of the six classes>", "confidence": "high" | "medium" | "low", "rationale": "one short sentence"}
