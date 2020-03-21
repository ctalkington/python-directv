"""Tests for DirecTV Models."""
import directv.models as models


def test_program() -> None:
    """Test the Program model."""
    program = models.Program.from_dict({})

    assert program
