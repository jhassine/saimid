"""Prompt templates."""

from saimid.api.admin import Prompt
from saimid.api.models import PromptLabelChoices

REDACTION_SUMMARY = "# REDACTION SUMMARY"

NO_ID_DATA = "No identifiable data detected."

REDACTION_SUMMARY_INSTRUCTIONS = f"""
{REDACTION_SUMMARY}

| Token                                  | Value          |
|----------------------------------------|----------------|
| REDACTED PERSON [id] [data type]       | real data here |
| REDACTED ORGANIZATION [id] [data type] | real data here |

---

If there was no content to de-identify, return "{NO_ID_DATA}" instead of the table.

"""

DEID_HEADER = "# DE-IDENTIFIED CONTENT"

QUOTE = "> "

DEID_INSTRUCTIONS = f"""Your are a de-identifier.

Your task is to return the user provided text as de-identified and replace
the identifiers with tokens.

The de-identification shall include the following data categories:

- Names
- Ages
- Dates of birth
- Email addresses
- Addresses
- Zip codes
- Phone numbers
- Social security numbers
- National identification numbers
- Credit card numbers
- Bank account numbers
- Driver's license numbers
- Passport numbers
- URLs
- IP addresses
- Organization names

Replace these types of data with appropriate tokens in this format:
***<REDACTED PERSON [ID] [DATA CATEGORY]>***
***<REDACTED ORGANIZATION [ID] [DATA CATEGORY]>***

, where the `[ID]` is a unique identifier (number) of the entity owning it
and the `[DATA CATEGORY]` indicates the category of information being redacted.

If the content does not have any content to be de-identified, return the text as it is without any alterations.
But provide the answer always in this markdown format:

{DEID_HEADER}

{QUOTE}de-identified content (or original content, if nothing to be de-identified) here

{REDACTION_SUMMARY_INSTRUCTIONS}
"""


def reid_instructions(tokens: str) -> str:
    """Return re-id prompt."""
    return (
        "Your task is to re-identify the content based on the provided tokens.\n"
        "If you see in the user provided text a token used, replace it with the value according to the TOKEN MAPPING.\n"
        "If the text is already in identified form, do not replace.\n"
        "\n"
        f"If the TOKEN MAPPING has '{NO_ID_DATA}', return the content as it is without any alterations.\n"
        "\n"
        "TOKEN MAPPING:\n"
        f"{tokens}"
    )


USER_RESPONSE_PROMPT = """
Your task is to respond to the user question in the same language user asked.
If you encounter a redacted word, and refer to it in your answer, provide a response using the same redacted word.
"""


def get_deid_prompt() -> str:
    """Get de-identification prompt."""
    return (
        Prompt.objects.get(purpose=PromptLabelChoices.DEID).prompt or DEID_INSTRUCTIONS
    )


def get_reid_prompt(tokens: str) -> str:
    """Get re-identification prompt."""
    if prompt := Prompt.objects.get(purpose=PromptLabelChoices.REID).prompt:
        return f"{prompt}\n{tokens}"
    return reid_instructions(tokens)


def get_user_response_system_prompt() -> str:
    return (
        Prompt.objects.get(purpose=PromptLabelChoices.RESPONSE).prompt
        or USER_RESPONSE_PROMPT
    )
