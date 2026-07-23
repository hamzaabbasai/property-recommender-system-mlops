from app.evaluation.ranking_metrics import ndcg_at_k, precision_at_k


def test_precision_at_k() -> None:
    assert precision_at_k(["a", "b", "c"], {"a", "c"}, 3) == 2 / 3


def test_ndcg_rewards_correct_order() -> None:
    good = ndcg_at_k(["a", "x"], {"a"}, 2)
    late = ndcg_at_k(["x", "a"], {"a"}, 2)
    assert good > late
