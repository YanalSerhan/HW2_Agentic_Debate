# Skill System (PRD_skill_system)

### Skill Discovery Mechanism
- Skills are discovered via a description-based routing mechanism.
- The `RouterSkill` acts as the initial entry point, analyzing the initial configuration/topic and selecting the appropriate specialized skills for context.

### ProSkill Behavior
- **Focus**: Offensive argumentation and evidence-first approach.
- **Strategy**: Proactively finds and leads with the strongest statistical evidence available via web search. Asserts points factually and aggressively.

### ConSkill Behavior
- **Focus**: Socratic questioning and rebuttal focus.
- **Strategy**: Identifies the weakest link in the opponent's evidence chain and attacks it. Must never automatically agree with the Pro agent.
- **Differentiation**: Must differ significantly from ProSkill both in system prompt and underlying implementation.

### RouterSkill
- Loads the system prompt once.
- Reads the opening statement and debate topic.
- Selects relevant skills (Pro or Con depending on assignment) and loads only those into context, optimizing token usage.

### Skill File Format
- Specialized logic is split into a markdown prompt (`.skill.md`) and a companion Python implementation (`.py`).
- Examples: `pro_skill.skill.md` + `pro_skill.py`.
