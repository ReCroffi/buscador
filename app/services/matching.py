from dataclasses import dataclass

from rapidfuzz import fuzz

from app.core.config import settings
from app.services.normalization import ProductSignature, build_signature


@dataclass(frozen=True)
class MatchResult:
    accepted: bool
    score: int
    reason: str


def _missing(required: frozenset[str], candidate: frozenset[str]) -> set[str]:
    return set(required - candidate)


class ExactProductMatcher:
    def __init__(self, threshold: int | None = None) -> None:
        self.threshold = threshold or settings.exact_match_threshold

    def match(self, query: str, candidate: str, sku: str | None = None, candidate_sku: str | None = None) -> MatchResult:
        query_sig = build_signature(query)
        candidate_sig = build_signature(candidate)

        if sku and candidate_sku and sku.lower() == candidate_sku.lower():
            return MatchResult(True, 100, "sku")

        hard_reject = self._hard_reject(query_sig, candidate_sig)
        if hard_reject:
            return MatchResult(False, 0, hard_reject)

        token_sort = fuzz.token_sort_ratio(query_sig.normalized, candidate_sig.normalized)
        token_set = fuzz.token_set_ratio(query_sig.normalized, candidate_sig.normalized)
        partial = fuzz.partial_ratio(query_sig.normalized, candidate_sig.normalized)
        coverage = 100 * len(query_sig.tokens & candidate_sig.tokens) / max(len(query_sig.tokens), 1)
        score = round((token_sort * 0.35) + (token_set * 0.25) + (partial * 0.15) + (coverage * 0.25))

        if score < self.threshold:
            return MatchResult(False, score, "score_below_threshold")
        return MatchResult(True, score, "exact_enough")

    @staticmethod
    def _hard_reject(query: ProductSignature, candidate: ProductSignature) -> str | None:
        if missing := _missing(query.capacities, candidate.capacities):
            return f"missing_capacity:{','.join(sorted(missing))}"
        if missing := _missing(query.models, candidate.models):
            return f"missing_model:{','.join(sorted(missing))}"
        if missing := _missing(query.versions, candidate.versions):
            return f"missing_version:{','.join(sorted(missing))}"
        numbers_query = {token for token in query.tokens if token.isdigit()}
        numbers_candidate = {token for token in candidate.tokens if token.isdigit()}
        if numbers_query and not numbers_query <= numbers_candidate:
            return "numeric_variant_mismatch"
        return None

