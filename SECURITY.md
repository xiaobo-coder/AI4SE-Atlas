# Security policy

AI4SE Atlas is a static website with no backend, accounts or user data. Security issues are still possible, for example a script injection through a data record, a malicious link, or a compromised build dependency.

**To report a vulnerability,** use GitHub's private vulnerability reporting (*Security → Report a vulnerability*) rather than a public issue. Please include the affected page or file and steps to reproduce. You can expect an acknowledgment within about a week.

**Data safety.** All records are rendered as escaped text (including JSON-LD and the search index), text fields may not contain `<` or `>`, links must be `http(s)://`, and the validator rejects records that do not match the JSON Schemas.
