"""Official /v2/ first-segment classification for Kunde route dumps."""

from __future__ import annotations

import re
from typing import Final, Literal
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_kunde_trace import request_path_class

TimingBucket = Literal["0_49", "50_99", "100_249", "250_499", "500_plus"]
RoutePhase = Literal["at_rest", "after_click", "after_type"]

OFFICIAL_V2_RESOURCES: Final[frozenset[str]] = frozenset(
    {
        "accountGroups",
        "accountNatures",
        "accounts",
        "attachments",
        "balanceModifiers",
        "bankLineMatches",
        "bankLineSubjectAssociations",
        "bankLines",
        "bankPayments",
        "billLines",
        "bills",
        "cities",
        "contactBalancePayments",
        "contactBalancePostings",
        "contactPersons",
        "contacts",
        "countries",
        "countryGroups",
        "currencies",
        "daybookBalanceAccounts",
        "daybookTransactionLines",
        "daybookTransactions",
        "daybooks",
        "documents",
        "files",
        "invoiceDeliveries",
        "invoiceLateFees",
        "invoiceLines",
        "invoiceLogs",
        "invoiceReminderAssociations",
        "invoiceReminders",
        "invoices",
        "locales",
        "organizations",
        "postings",
        "productPrices",
        "products",
        "salesTaxAccounts",
        "salesTaxMetaFields",
        "salesTaxPayments",
        "salesTaxReturns",
        "salesTaxRules",
        "salesTaxRulesets",
        "states",
        "taxRateDeductionComponents",
        "taxRates",
        "transactions",
        "user",
        "users",
        "zipcodes",
    }
)
CONTACT_ADJACENT_CLASSES: Final[frozenset[str]] = frozenset(
    {
        "contactPersons",
        "contactBalancePayments",
        "contactBalancePostings",
    }
)
COARSE_ROUTE_CLASSES: Final[frozenset[str]] = frozenset(
    {"contacts", "invoices", "other_v2", "other_same_origin", "denied"}
)
ROUTE_PHASES: Final[frozenset[str]] = frozenset({"at_rest", "after_click", "after_type"})
TIMING_BUCKETS: Final[frozenset[str]] = frozenset(
    {"0_49", "50_99", "100_249", "250_499", "500_plus"}
)
_UUID_RE: Final = re.compile(
    r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)
_LONG_HEX_RE: Final = re.compile(r"^[0-9A-Fa-f]{16,}$")
_DIGITS_RE: Final = re.compile(r"^\d+$")
_OPAQUE_ID_RE: Final = re.compile(r"^[A-Za-z0-9_-]{12,}$")
_ORG_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        "bootstrap",
        "campaign",
        "couponOffer",
        "subscription",
        "settings",
        "billy",
        "details",
    }
)


def _sanitize_segment(part: str, *, after_organizations: bool) -> str:
    if _UUID_RE.fullmatch(part):
        return ":uuid"
    if _LONG_HEX_RE.fullmatch(part):
        return ":id"
    if _DIGITS_RE.fullmatch(part):
        return ":n"
    if after_organizations and part not in _ORG_SUFFIXES:
        return ":id"
    if "-" in part:
        return ":id"
    if _OPAQUE_ID_RE.fullmatch(part) and part not in OFFICIAL_V2_RESOURCES:
        has_upper = any(char.isupper() for char in part)
        has_lower = any(char.islower() for char in part)
        if has_upper and has_lower:
            return ":id"
    return part


def sanitize_v2_route_template(path: str) -> str:
    """Strip query and replace UUID, ids, digits, slugs, and org values."""

    cleaned = path.split("?", 1)[0]
    parts = [part for part in cleaned.split("/") if part != ""]
    safe: list[str] = []
    after_organizations = False
    for part in parts:
        safe.append(_sanitize_segment(part, after_organizations=after_organizations))
        if part == "organizations":
            after_organizations = True
    return "/" + "/".join(safe) if safe else "/"


def route_class_for(path: str) -> str:
    """Map the first /v2/ segment to an official token, else other_v2."""

    coarse = request_path_class(path)
    if coarse in {"contacts", "invoices", "other_same_origin", "denied"}:
        return coarse
    cleaned = path.split("?", 1)[0]
    parts = [part for part in cleaned.split("/") if part != ""]
    if len(parts) >= 2 and parts[0] == "v2" and parts[1] in OFFICIAL_V2_RESOURCES:
        return parts[1]
    return "other_v2"


def route_class_for_url(url: str) -> str:
    """Classify a full URL without storing it."""

    parsed = urlsplit(url)
    host = parsed.netloc.split("@")[-1].split(":", 1)[0].casefold()
    if host not in {"mit.billy.dk", "api.billysbilling.com", "download.billy.dk"}:
        return "denied"
    return route_class_for(parsed.path)


def timing_bucket_for(timing_ms: int) -> TimingBucket:
    """Map elapsed ms to an allowlisted bucket."""

    if timing_ms < 50:
        return "0_49"
    if timing_ms < 100:
        return "50_99"
    if timing_ms < 250:
        return "100_249"
    if timing_ms < 500:
        return "250_499"
    return "500_plus"


def is_contact_adjacent_class(route_class: str) -> bool:
    """True when the class is a contact dataset that is not /v2/contacts."""

    if route_class in CONTACT_ADJACENT_CLASSES:
        return True
    return route_class.startswith("contact") and route_class != "contacts"


def owner_template_from_url(url: str) -> str:
    """Sanitized template only. Never include query or ids."""

    return sanitize_v2_route_template(urlsplit(url).path)
