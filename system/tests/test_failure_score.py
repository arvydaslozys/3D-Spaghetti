import pytest

import utils.tools as tools


@pytest.mark.parametrize("det1,det2,score,expected",    [
    (0, 100, 0, 90),
    (10, 10, 50, 70),
    (100, 0, 100, 190),
    (None, None, 100, 100),
    (10, 10, 0, 20),
    (None, None, 3, 3),
    (0, 0, 5, 0)
])
def test_calculate_score_updates_running_score_from_model_counts(det1,det2,score,expected):
    assert tools.calculate_score(score,det1,det2) == expected
