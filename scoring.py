from typing import Any


def calculate_trust_score(fields: dict[str, Any]) -> int:
    """
    Returns a trust score between 0 and 100.

    Scoring logic:
      +15  SOC 2 certified
      +15  GDPR compliant
      +10  HIPAA compliant
      +10  ISO 27001 certified
      +10  Does NOT train on user inputs
      -20  Breach incidents mentioned
    """
    score = 50

    if fields.get("soc2_certified") is True:
        score += 15
    if fields.get("gdpr_compliant") is True:
        score += 15
    if fields.get("hipaa_compliant") is True:
        score += 10
    if fields.get("iso_27001") is True:
        score += 10
    if fields.get("trains_on_input") is False:
        score += 10
    if fields.get("breach_mentions") is True:
        score -= 20

    return max(0, min(100, score))