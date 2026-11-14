# Claim audit (M3 acceptance: at least 90% of 30 random verified claims judged correct)

0 claims drawn with a seeded random sample (seed 20261019) from the claims with status `verified_auto`. For each row read the span in the source (PDF page number is the PDF page index) and answer in `correct?`: **yes** if the statement is supported by the span and its conditions (gravity class, material, numbers) are right, **no** if not, with a short note. Fill in `reviewer` too. Statistics are computed by `python -m ledger report` from the filled rows.

| # | claim_id | document | page | gravity | statement | span | correct? | reviewer | note |
|---|---|---|---|---|---|---|---|---|---|
