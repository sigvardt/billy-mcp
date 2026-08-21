"""Company-phone preview tokens. Empty is a deliberate clear."""

from __future__ import annotations

from typing import Final, Literal

PhoneAction = Literal["clear", "set"]

PHONE_INPUT_NAME: Final = "phone"
SAVE_LABEL: Final = "Gem ændringer"


def phone_action_from(phone: str) -> PhoneAction:
    """Return clear for exact empty phone, set for a non-empty value."""

    if phone == "":
        return "clear"
    if phone.strip() != phone:
        raise ValueError("phone must be exact empty or already trimmed")
    return "set"


def preview_summary_for(action: PhoneAction) -> str:
    """Plain-language preview summary. Distinguishes clear from set."""

    match action:
        case "clear":
            return (
                "Clear the company phone on Billy Indstillinger. "
                "Does not touch users, access tokens, or subscription."
            )
        case "set":
            return (
                "Set the company phone on Billy Indstillinger. "
                "Does not touch users, access tokens, or subscription."
            )


def named_input_matches(expected: str, actual: str) -> bool:
    """True when the phone input value equals the bound request exactly."""

    return expected == actual
