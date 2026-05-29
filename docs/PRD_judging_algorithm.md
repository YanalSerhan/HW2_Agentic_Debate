# Judging Algorithm (PRD_judging_algorithm)

### Input
- Full transcript of all debate rounds (all matched `ARGUMENT` and `COUNTER_ARGUMENT` pairs).

### Scoring Dimensions
1. **Rhetorical Strength**: The assertiveness, clarity, and persuasiveness of the arguments.
2. **Evidence Quality**: The utilization and integration of mandatory web search results.
3. **Logical Coherence**: Structural soundness of the points made.
4. **Counter-Argument Effectiveness**: The ability to identify weak points in the opponent's case and successfully rebut them.

### Output Format
The algorithm generates a `Verdict` object containing:
- `pro_score` (0-100)
- `con_score` (0-100)
- `winner` (PRO or CON)
- `reasoning` (a paragraph-length justification of the decision)
- `key_winning_arguments` (list of the top 3 arguments that swayed the judge)
- Metadata (round count, token usage, cost)

### Edge Case: Tie-Breaking Procedure
- Ties are strictly forbidden.
- If the initial evaluation yields a tied score, the judging algorithm must execute a tie-breaker.
- The tie-breaker assigns +1 point to the agent that successfully cited more diverse/authoritative external evidence via web search, or the agent who addressed more counter-arguments directly.

### Constraints
- The Judge evaluates based exclusively on **persuasion power**, not factual truth or absolute correctness.
- The Father agent must never reveal internal state or preliminary scores to children during the debate.
