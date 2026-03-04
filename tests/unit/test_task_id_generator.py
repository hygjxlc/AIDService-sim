"""Unit tests for TaskID generator"""
import pytest
from src.utils.task_id_generator import (
    is_valid_simulate_type,
    VALID_SIMULATE_TYPES
)


class TestSimulateTypeValidation:
    """Tests for simulate type validation"""
    
    def test_valid_simulate_types(self):
        """Test all valid simulate types"""
        for sim_type in VALID_SIMULATE_TYPES:
            assert is_valid_simulate_type(sim_type) is True
    
    def test_invalid_simulate_type(self):
        """Test invalid simulate type"""
        assert is_valid_simulate_type("InvalidType") is False
        assert is_valid_simulate_type("") is False
        assert is_valid_simulate_type("lawan") is False  # Case sensitive
    
    def test_valid_types_list(self):
        """Test that all expected types are in the list"""
        expected = ["LaWan", "CHOnYA", "ZhuZao", "ZhaZhi", "ZHEWan", "JIYA"]
        assert VALID_SIMULATE_TYPES == expected
