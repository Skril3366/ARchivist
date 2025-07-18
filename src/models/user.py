from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UserFact(BaseModel):
    """Represents a single extracted fact about a user."""

    fact_type: str = Field(..., description="The category of the fact (e.g., 'location', 'interest', 'occupation')")
    value: str = Field(..., description="The extracted value of the fact")
    source_message_id: Optional[int] = Field(
        None, description="The ID of the message from which the fact was extracted"
    )
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score of the extraction (0.0 to 1.0)")
    # Add timestamp of extraction, LLM model used, etc. for provenance


class UserProfile(BaseModel):
    """Represents a comprehensive profile of a user, accumulating various facts."""

    telegram_id: str = Field(..., description="The unique Telegram ID of the user (e.g., 'user12345678')")
    display_name: Optional[str] = Field(None, description="The user's display name in the chat")
    # Core facts
    real_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    occupation: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    # Dynamic facts: for any other facts not explicitly modeled
    dynamic_facts: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="A dictionary of dynamically discovered facts, e.g., {'favorite_food': ['pizza', 'sushi']}",
    )
    # List of all extracted facts, including those that populate core fields
    all_facts: List[UserFact] = Field(default_factory=list)

    def add_fact(self, fact: UserFact):
        """Add a fact to the user profile, updating core fields if applicable."""
        # Avoid adding duplicate facts based on type and value
        if any(f.fact_type == fact.fact_type and f.value == fact.value for f in self.all_facts):
            return

        self.all_facts.append(fact)

        # Update core fields if the fact type matches
        if fact.fact_type == "real_name" and not self.real_name:
            self.real_name = fact.value
        elif fact.fact_type == "city" and not self.city:
            self.city = fact.value
        elif fact.fact_type == "country" and not self.country:
            self.country = fact.value
        elif fact.fact_type == "occupation" and not self.occupation:
            self.occupation = fact.value
        elif fact.fact_type == "interest":
            if fact.value not in self.interests:
                self.interests.append(fact.value)
        else:
            # Add to dynamic facts
            if fact.fact_type not in self.dynamic_facts:
                self.dynamic_facts[fact.fact_type] = []
            if fact.value not in self.dynamic_facts[fact.fact_type]:
                self.dynamic_facts[fact.fact_type].append(fact.value)

    def get_facts_by_type(self, fact_type: str) -> List[str]:
        """Return a list of values for a given fact type."""
        if fact_type == "real_name" and self.real_name:
            return [self.real_name]
        elif fact_type == "city" and self.city:
            return [self.city]
        elif fact_type == "country" and self.country:
            return [self.country]
        elif fact_type == "occupation" and self.occupation:
            return [self.occupation]
        elif fact_type == "interest":
            return self.interests
        elif fact_type in self.dynamic_facts:
            return self.dynamic_facts[fact_type]
        return []
