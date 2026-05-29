import pytest

from debate.debate.agreement_detector import AgreementDetector


@pytest.fixture
def detector():
    return AgreementDetector()


def test_detects_explicit_agreement(detector):
    pro = "Statistics show renewable energy is cheaper."
    con = "I agree with your assessment. Renewable energy is indeed cheaper."
    assert detector.is_agreeing(pro, con) is True


def test_genuine_counter_argument_not_flagged(detector):
    pro = "Statistics show renewable energy is cheaper."
    con = (
        "While the upfront cost may appear lower, the total lifecycle cost "
        "including grid-storage infrastructure makes renewables far more "
        "expensive per reliable kilowatt-hour."
    )
    assert detector.is_agreeing(pro, con) is False


def test_partial_concession_not_flagged(detector):
    """A sentence like 'You make a good point, however ...' is a rhetorical
    device, not capitulation."""
    pro = "Electric cars reduce urban pollution significantly."
    con = (
        "You make a good point, however the pollution is merely shifted to "
        "the lithium mining regions and coal-burning power plants."
    )
    assert detector.is_agreeing(pro, con) is False


def test_detects_youre_right(detector):
    pro = "AI will replace most manual jobs."
    con = "You're right, AI will indeed replace manual jobs."
    assert detector.is_agreeing(pro, con) is True


def test_concession_with_but_not_flagged(detector):
    pro = "Social media connects people globally."
    con = (
        "I must admit social media has global reach, but it simultaneously "
        "fragments communities into echo chambers."
    )
    assert detector.is_agreeing(pro, con) is False
