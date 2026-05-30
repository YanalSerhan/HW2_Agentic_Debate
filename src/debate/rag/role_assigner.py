class RoleAssigner:
    """Assigns debate roles dynamically based on topic."""

    def __init__(self):
        # Known topics that each persona would naturally support (PRO) or oppose (CON)
        self.hitchens_pro = ["free speech", "secularism", "atheism", "intervention", "liberalism", "war on terror"]
        self.hitchens_con = ["religion", "authoritarianism", "nationalism", "censorship"]

        self.chomsky_pro = ["anti-capitalism", "media criticism", "anti-imperialism", "workers rights", "palestine"]
        self.chomsky_con = ["us foreign policy", "corporate power", "mainstream media", "military intervention"]

    def assign_roles(self, topic: str) -> dict:
        """
        Returns a dict indicating which persona takes which side, e.g.
        {"pro": "hitchens", "con": "chomsky"}
        """
        topic_lower = topic.lower()

        hitchens_score = 0
        chomsky_score = 0

        # Calculate affinity for PRO
        for term in self.hitchens_pro:
            if term in topic_lower:
                hitchens_score += 1

        for term in self.chomsky_pro:
            if term in topic_lower:
                chomsky_score += 1

        # Calculate affinity for CON (which implies negative affinity for PRO)
        for term in self.hitchens_con:
            if term in topic_lower:
                hitchens_score -= 1

        for term in self.chomsky_con:
            if term in topic_lower:
                chomsky_score -= 1

        # If Chomsky has a stronger affinity for PRO than Hitchens (or Hitchens has a strong affinity for CON),
        # we flip the default so Chomsky is PRO and Hitchens is CON.
        if chomsky_score > hitchens_score:
            return {"pro": "chomsky", "con": "hitchens"}

        # Default fallback
        return {"pro": "hitchens", "con": "chomsky"}
