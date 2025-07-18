# This file will contain structured prompts for LLM interactions.
# Examples of prompts for fact extraction, summarization, etc. will go here.

# Example: Prompt for extracting user facts
EXTRACT_USER_FACTS_PROMPT = """
You are an expert assistant designed to extract specific facts about users from chat messages.
Your goal is to identify and categorize information that describes a user's profile.
Focus on factual information that can be used to build a user profile.

Here is the chat message context:
---
{context}
---

Here are the existing facts known about the user (if any), to avoid duplication:
---
{existing_facts}
---

Extract the following types of facts about the user who sent the message:
- **real_name**: The user's full real name.
- **city**: The city where the user lives or is from.
- **country**: The country where the user lives or is from.
- **occupation**: The user's profession or job.
- **interests**: Hobbies, passions, or topics the user is interested in.
- **contact_info**: Any phone numbers, emails, or social media handles.
- **skills**: Specific abilities or expertise the user possesses.
- **preferences**: User preferences (e.g., favorite food, music, movies).
- **opinions**: Strong opinions or stances on topics.
- **relationships**: Mentions of family members, friends, or professional connections.
- **goals**: Stated personal or professional goals.
- **travel_history**: Places the user has visited or plans to visit.
- **education**: Educational background or institutions attended.
- **pets**: Information about pets.
- **other**: Any other significant factual information that doesn't fit the above categories.

For each fact, provide the exact text from the message that supports it.
If a fact type is not present, omit it.
If multiple values for a fact type are found, list them all.
Do not make up facts. Only extract what is explicitly stated or strongly implied.

Output the facts as a JSON object, where keys are the fact types and values are lists of strings.
Example JSON output:
```json
{{
  "real_name": ["John Doe"],
  "city": ["New York"],
  "interests": ["photography", "hiking"],
  "other": ["loves coffee"]
}}
```
"""

# Example: Schema for extracting user facts
EXTRACT_USER_FACTS_SCHEMA = {
    "type": "object",
    "properties": {
        "real_name": {"type": "array", "items": {"type": "string"}},
        "city": {"type": "array", "items": {"type": "string"}},
        "country": {"type": "array", "items": {"type": "string"}},
        "occupation": {"type": "array", "items": {"type": "string"}},
        "interests": {"type": "array", "items": {"type": "string"}},
        "contact_info": {"type": "array", "items": {"type": "string"}},
        "skills": {"type": "array", "items": {"type": "string"}},
        "preferences": {"type": "array", "items": {"type": "string"}},
        "opinions": {"type": "array", "items": {"type": "string"}},
        "relationships": {"type": "array", "items": {"type": "string"}},
        "goals": {"type": "array", "items": {"type": "string"}},
        "travel_history": {"type": "array", "items": {"type": "string"}},
        "education": {"type": "array", "items": {"type": "string"}},
        "pets": {"type": "array", "items": {"type": "string"}},
        "other": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
}
