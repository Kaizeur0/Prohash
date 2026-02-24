import pytest
from core.detector import HashDetector

def test_detector_initialization():
    """Un test de vérification du système simple."""
    detector = HashDetector()
    assert detector is not None
