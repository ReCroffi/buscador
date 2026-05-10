import re
import unicodedata
from dataclasses import dataclass

STOPWORDS = {
    "de",
    "da",
    "do",
    "das",
    "dos",
    "com",
    "para",
    "novo",
    "original",
    "lacrado",
    "unidade",
}

CAPACITY_RE = re.compile(r"\b(\d+(?:tb|gb|g|t|ml|l|kg|w|hz))\b", re.I)
MODEL_RE = re.compile(r"\b([a-z]{1,8}[- ]?\d{2,6}[a-z0-9-]*|\d{2,5}[a-z]{1,5})\b", re.I)
VERSION_RE = re.compile(r"\b(pro max|pro|plus|slim|digital|ti|super|ultra|tuf|oc|frost free)\b", re.I)


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_text(value: str) -> str:
    value = strip_accents(value.lower())
    value = re.sub(r"([0-9]+)\s+(gb|tb|g|t|ml|l|kg|w|hz)\b", r"\1\2", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    tokens = [token for token in value.split() if token not in STOPWORDS]
    return " ".join(tokens)


@dataclass(frozen=True)
class ProductSignature:
    normalized: str
    tokens: frozenset[str]
    capacities: frozenset[str]
    models: frozenset[str]
    versions: frozenset[str]


def build_signature(value: str) -> ProductSignature:
    normalized = normalize_text(value)
    return ProductSignature(
        normalized=normalized,
        tokens=frozenset(normalized.split()),
        capacities=frozenset(match.lower().replace(" ", "") for match in CAPACITY_RE.findall(normalized)),
        models=frozenset(match.lower().replace(" ", "") for match in MODEL_RE.findall(normalized)),
        versions=frozenset(match.lower() for match in VERSION_RE.findall(normalized)),
    )

