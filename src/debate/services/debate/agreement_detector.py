"""Detects when an agent agrees with its opponent instead of rebutting."""



# Phrases that signal capitulation rather than genuine rebuttal
_AGREEMENT_PHRASES = [
    "i agree",
    "you're right",
    "you are right",
    "you make a good point",
    "you make a great point",
    "you make an excellent point",
    "i concede",
    "i must admit",
    "i have to agree",
    "i cannot argue",
    "i can't argue",
    "that's a fair point",
    "that is a fair point",
]

# Phrases that look like agreement but are actually rhetorical concessions
# used as a lead-in to a counter-argument.  These should NOT trigger.
_CONCESSION_QUALIFIERS = [
    "however",
    "but",
    "nevertheless",
    "nonetheless",
    "on the other hand",
    "that said",
    "still",
    "yet",
    "despite",
    "although",
]


class AgreementDetector:
    """Detects whether a Con/Pro agent is capitulating instead of rebutting."""

    def __init__(self, extra_phrases: list[str] | None = None):
        """Auto-generated docstring."""
        self._phrases = list(_AGREEMENT_PHRASES)
        if extra_phrases:
            self._phrases.extend(p.lower() for p in extra_phrases)

    def is_agreeing(self, pro_message: str, con_message: str) -> bool:
        """Returns True if *con_message* capitulates to *pro_message*.

        A message is considered an agreement when it contains one of the
        known agreement phrases **without** a nearby qualifying conjunction
        that would turn it into a partial concession + counter-argument.
        """
        con_lower = con_message.lower()

        for phrase in self._phrases:
            if phrase not in con_lower:
                continue

            # Find the position of the agreement phrase
            idx = con_lower.index(phrase)
            # Look at the surrounding window (phrase + 120 chars after)
            window = con_lower[idx : idx + len(phrase) + 120]

            has_qualifier = any(q in window for q in _CONCESSION_QUALIFIERS)
            if not has_qualifier:
                return True

        return False
