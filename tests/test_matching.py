from app.services.matching import ExactProductMatcher


def test_accepts_exact_capacity_and_variant() -> None:
    matcher = ExactProductMatcher(threshold=85)
    result = matcher.match("iPhone 16 Pro Max 512GB", "Apple iPhone 16 Pro Max 512GB Titanio Natural")
    assert result.accepted
    assert result.score >= 85


def test_rejects_wrong_capacity() -> None:
    matcher = ExactProductMatcher(threshold=85)
    result = matcher.match("iPhone 16 Pro Max 512GB", "Apple iPhone 16 Pro Max 256GB")
    assert not result.accepted
    assert result.reason.startswith("missing_capacity")


def test_rejects_wrong_version() -> None:
    matcher = ExactProductMatcher(threshold=85)
    result = matcher.match("Playstation 5 Slim Digital", "Console Playstation 5 Slim com disco")
    assert not result.accepted

