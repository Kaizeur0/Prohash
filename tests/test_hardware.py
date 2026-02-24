import pytest
from core.hardware_checker import HardwareChecker

def test_hardware_initialization():
    """Un test de vérification pour HardwareChecker."""
    checker = HardwareChecker()
    assert checker is not None
