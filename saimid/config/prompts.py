"""Prompt templates."""

REDACTION_SUMMARY = "# REDACTION SUMMARY"

REDACTION_SUMMARY_INSTRUCTIONS = f"""
{REDACTION_SUMMARY}

| Key | Id |
|-----|----|
| REDACTED PERSON 1 NAME | real person 1 name |
| REDACTED PERSON 1 EMAIL | real person 1 email |
| REDACTED ORGANIZATION 1 NAME | real organization 1 name |

---
"""

DEID_INSTRUCTIONS = f"""
Your task is to return the user provided content as de-identied/pseudonymized.

The de-identification shall include, but not limited to, the following data types:
- Names
- Email addresses
- Addresses
- Date of birth
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

Replace these types of content with appropriate placeholders in this way:
***<REDACTED PERSON 1 NAME>***
***<REDACTED PERSON 1 EMAIL>***
***<REDACTED ORGANIZATION 1 NAME>***


Provide the answer in this markdown format:

# DE-IDENTIFIED CONTENT

> de-identified content here

{REDACTION_SUMMARY_INSTRUCTIONS}

---

"""


REID_INSTRUCTIONS = """Your task is to return the user provided content as re-identified by using the following (if any):
"""

GUARDRAIL_CHECK = """

Your task is to evaluate the provided content and check if it contains any of the following data types.

# DATA TYPE SUMMARY

| Data Type | Contains (✓/✗) |
|-----|----|
| Personal data | ✓/✗ |
| Data concerning health | ✓/✗ |
| Business sensitive data | ✓/✗ |
| Data concerning national security | ✓/✗ |
| Data concerning financial information | ✓/✗ |
| Data concerning sensitive data | ✓/✗ |
| Data concerning children | ✓/✗ |
| Data concerning sexual orientation | ✓/✗ |
| Data concerning political opinions | ✓/✗ |
| Data concerning religious beliefs | ✓/✗ |
| Data concerning biometric data | ✓/✗ |
| Data concerning genetic data | ✓/✗ |
| Data concerning sexual life | ✓/✗ |
| Data concerning location data | ✓/✗ |

"""
