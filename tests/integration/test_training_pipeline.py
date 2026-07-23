from pathlib import Path

from app.pipelines.train_ranker import build_training_data

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_training_data_has_groups_and_labels() -> None:
    frame, labels, groups = build_training_data(
        properties_path=FIXTURES / "properties.csv",
        interactions_path=FIXTURES / "interactions.csv",
        max_users=10,
        candidate_count=3,
    )
    assert len(frame) == len(labels)
    assert sum(groups) == len(frame)
