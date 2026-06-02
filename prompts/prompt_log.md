# Prompt Engineering Log

This log documents the iterative process of designing, testing, and refining the core prompts that power the multi-agent debate system. The system relies heavily on carefully constructed persona prompts (Hitchens and Chomsky) and a rigid evaluation rubric (Justice Ginsburg).

## 1. Persona Engineering: Christopher Hitchens (Pro)

**Goal:** Create a highly aggressive, witty, and evidence-demanding persona that argues for the affirmative.
**Early Attempt:** 
> "You are Christopher Hitchens. Argue the pro side of the topic using your typical style. Be aggressive and use web search."
**Feedback/Issue:** The model adopted a generic "angry" tone rather than Hitchens' specific intellectual aggression. It lacked his trademark historical references and rhetorical traps.
**Refinement:** 
We broke down Hitchens' style into 5 distinct "Rhetorical Patterns" (The Hitchens Razor, Moral Inversion, Historical Parallel, Escalating Concession, Direct Challenge). We added explicit instructions to attack root assumptions rather than just rebutting points.
**Final Prompt Structure:** (See `src/debate/skills/pro_skill.skill.md`)
Includes specific examples of his rhetorical techniques and strict directives to cite empirical evidence from web searches.

## 2. Persona Engineering: Noam Chomsky (Con)

**Goal:** Create a calm, systematic, and institutional-critique persona that argues for the negative.
**Early Attempt:** 
> "You are Noam Chomsky. Argue the con side. Focus on linguistics and politics."
**Feedback/Issue:** The model wandered into abstract linguistic theory instead of debating the actual topic. It also occasionally sounded too emotional when debating.
**Refinement:** 
Refocused the prompt entirely on "Institutional Analysis" and "The Documentary Record". Explicitly banned emotional appeals ("Never emotional. Deconstruct power structures."). We instructed the model to always identify which corporations or power structures benefit from the opponent's position.
**Final Prompt Structure:** (See `src/debate/skills/con_skill.skill.md`)
Forces the agent to systematically dismantle the opponent's premises using declassified documents and historical precedent.

## 3. The Master Agent: Justice Ruth Bader Ginsburg (Judge)

**Goal:** Create an impartial, rigorous judge that scores the debate on specific metrics and never allows a tie.
**Early Attempt:** 
> "You are the judge. Who won the debate and why? Give a score out of 100."
**Feedback/Issue:** The LLM frequently declared ties (e.g., 50-50) or scored based on "truth" rather than persuasion. The output format was unpredictable, breaking the JSON parser.
**Refinement:** 
1. **JSON Constraint:** Forced the output to be a strict JSON object with specific keys.
2. **Four-Dimensional Rubric:** Created a 4-point rubric (Rhetorical Strength, Evidence Quality, Logical Coherence, Counter-Argument Effectiveness) capped at 25 points each.
3. **No-Tie Policy:** Explicitly banned ties in the system prompt ("Ties are mathematically and philosophically forbidden").
4. **Persuasion over Truth:** Added a directive to judge based *only* on the arguments presented, not the LLM's internal knowledge base.

## 4. Web Search Tool Integration

**Goal:** Ensure agents use the `web_search_20250305` tool correctly and format citations.
**Challenge:** Early on, agents would say "Let me search the web for this..." in their final text output, which ruined the immersion of the debate.
**Solution:** Implemented regex cleanup in `api_mixin.py` to strip out "search announcements" (e.g., "I need to search..."). The prompt was also updated to instruct agents: "Do not narrate your search process. Just deliver the argument."

## 5. Agreement Detection

**Goal:** Prevent agents from capitulating prematurely.
**Challenge:** The Con agent would sometimes concede points rhetorically ("You make a good point, but..."), which a naive keyword matcher caught as full capitulation.
**Solution:** Developed the `AgreementDetector` using qualifier-aware heuristic NLP. If a concession phrase ("i agree") is followed closely by a qualifier ("however", "nonetheless"), it is correctly identified as a rhetorical pivot rather than a surrender.
