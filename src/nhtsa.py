import requests

_BASE = "https://api.nhtsa.gov"

_LEAN_KEYWORDS = ["p0171", "p0174", "lean", "fuel trim", "vacuum", "maf", "mass air"]
_RICH_KEYWORDS = ["p0172", "p0175", "rich", "fuel trim", "injector", "over-fueling"]


def _fetch(url: str) -> dict:
    resp = requests.get(url, timeout=8)
    resp.raise_for_status()
    return resp.json()


def get_recalls(make: str, model: str, year: int) -> list[dict]:
    """Return list of active recalls for the given vehicle. Empty list on any error."""
    try:
        data = _fetch(
            f"{_BASE}/recalls/recallsByVehicle"
            f"?make={make}&model={model}&modelYear={year}"
        )
        return data.get("results", [])
    except Exception:
        return []


def get_complaints(make: str, model: str, year: int) -> list[dict]:
    """Return list of NHTSA complaints for the given vehicle. Empty list on any error."""
    try:
        data = _fetch(
            f"{_BASE}/complaints/complaintsByVehicle"
            f"?make={make}&model={model}&modelYear={year}"
        )
        return data.get("results", [])
    except Exception:
        return []


def get_fault_context(
    make: str, model: str, year: int, direction: str
) -> dict:
    """
    Combine recalls and complaints, filtering complaints relevant to the
    detected fault direction ('lean', 'rich', or 'nominal').
    Returns a dict safe to render even when the API is unavailable.
    """
    recalls = get_recalls(make, model, year)
    complaints = get_complaints(make, model, year)

    keywords = _LEAN_KEYWORDS if direction == "lean" else (
        _RICH_KEYWORDS if direction == "rich" else []
    )

    relevant = []
    for c in complaints:
        text = (c.get("summary", "") + " " + c.get("components", "")).lower()
        if any(kw in text for kw in keywords):
            relevant.append(c)

    dtc_codes = (
        ["P0171", "P0174"] if direction == "lean"
        else ["P0172", "P0175"] if direction == "rich"
        else []
    )

    nhtsa_url = (
        f"https://www.nhtsa.gov/vehicle/{make}/{model}/{year}/0"
        .replace(" ", "%20")
    )

    return {
        "recall_count": len(recalls),
        "recalls": recalls[:3],
        "total_complaints": len(complaints),
        "relevant_complaints": len(relevant),
        "dtc_codes": dtc_codes,
        "nhtsa_url": nhtsa_url,
        "api_available": len(recalls) > 0 or len(complaints) > 0 or (
            get_recalls(make, model, year) == [] and
            get_complaints(make, model, year) == []
        ),
    }