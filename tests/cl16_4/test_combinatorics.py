"""
Tests for Cl(16,4) Combinatorics
==============================
"""

import unittest
from daxda_engine.cl16_4.combinatorics.cl_space import ClSpace, ClConfig
from daxda_engine.cl16_4.combinatorics.state_repr import ClState, STATE_TABLE
from daxda_engine.cl16_4.combinatorics.constraints import ConstraintSystem, DEFAULT_CONSTRAINTS


class TestClSpace(unittest.TestCase):
    """Test ClSpace functionality."""
    
    def setUp(self):
        self.space = ClSpace(n=16, k=4)
    
    def test_size(self):
        """Test that Cl(16,4) has correct size."""
        # C(16,4) = 16! / (4! * 12!) = 1820
        self.assertEqual(self.space.size, 1820)
    
    def test_get_config(self):
        """Test configuration retrieval."""
        config = self.space.get_config((0, 1, 2, 3))
        self.assertIsNotNone(config)
        self.assertEqual(config.indices, (0, 1, 2, 3))
    
    def test_invalid_config(self):
        """Test invalid configuration handling."""
        # Too many indices
        self.assertIsNone(self.space.get_config((0, 1, 2, 3, 4)))
        # Out of range
        self.assertIsNone(self.space.get_config((0, 1, 2, 16)))
    
    def test_mapping(self):
        """Test coordinate mapping to configuration."""
        # Create a vector that should map to (0, 1, 2, 3)
        vector = [0.0] * 16
        vector[0] = 1.0
        vector[1] = 0.9
        vector[2] = 0.8
        vector[3] = 0.7
        
        config = self.space.map_to_config(vector)
        self.assertIsNotNone(config)
        # The exact mapping depends on the implementation
        self.assertEqual(len(config.indices), 4)
    
    def test_neighbors(self):
        """Test neighbor finding."""
        config = self.space.get_config((0, 1, 2, 3))
        neighbors = self.space.get_neighbors(config, distance=1)
        
        # Should find configurations with Hamming distance 1
        self.assertGreater(len(neighbors), 0)
        for neighbor in neighbors:
            dist = self.space.hamming_distance(config, neighbor)
            self.assertLessEqual(dist, 1)
    
    def test_subspace(self):
        """Test subspace extraction."""
        subspace = self.space.get_subspace(n=8, k=2)
        self.assertEqual(subspace.n, 8)
        self.assertEqual(subspace.k, 2)
        # C(8,2) = 28
        self.assertEqual(subspace.size, 28)


class TestClState(unittest.TestCase):
    """Test ClState functionality."""
    
    def test_state_creation(self):
        """Test state creation."""
        state = ClState((0, 1, 2, 3))
        self.assertEqual(state.indices, (0, 1, 2, 3))
    
    def test_validation(self):
        """Test state validation."""
        # Valid state
        state = ClState((0, 1, 2, 3))
        self.assertEqual(state.indices, (0, 1, 2, 3))
        
        # Invalid - duplicate indices
        with self.assertRaises(ValueError):
            ClState((0, 1, 2, 2))
        
        # Invalid - out of range
        with self.assertRaises(ValueError):
            ClState((0, 1, 2, 16))
        
        # Invalid - wrong number of indices
        with self.assertRaises(ValueError):
            ClState((0, 1, 2))
    
    def test_int_conversion(self):
        """Test integer packing/unpacking."""
        state = ClState((0, 1, 2, 3))
        packed = state.to_int()
        unpacked = ClState.from_int(packed)
        self.assertEqual(state.indices, unpacked.indices)
    
    def test_bytes_conversion(self):
        """Test bytes packing/unpacking."""
        state = ClState((10, 11, 12, 13))
        packed = state.to_bytes()
        unpacked = ClState.from_bytes(packed)
        self.assertEqual(state.indices, unpacked.indices)


class TestConstraintSystem(unittest.TestCase):
    """Test constraint system functionality."""
    
    def setUp(self):
        self.space = ClSpace(n=16, k=4)
        self.constraints = ConstraintSystem(space=self.space)
    
    def test_default_constraints(self):
        """Test default constraints are registered."""
        self.assertGreater(len(self.constraints), 0)
    
    def test_check_valid_config(self):
        """Test checking a valid configuration."""
        config = self.space.get_config((0, 1, 2, 3))
        result = self.constraints.check_config(config)
        self.assertEqual(result.config, config)
        # Should pass hard constraints
        self.assertEqual(len(result.failed), 0)
    
    def test_get_valid_configs(self):
        """Test getting all valid configurations."""
        valid = self.constraints.get_valid_configs()
        # All configs should be valid with default constraints
        self.assertEqual(len(valid), self.space.size)
    
    def test_dynamic_constraint(self):
        """Test adding dynamic constraints."""
        self.constraints.add_dynamic_constraint(
            "test_constraint",
            {"min_sum": 10}
        )
        
        # Config with sum < 10 should fail
        config = self.space.get_config((0, 1, 2, 3))  # sum = 6
        result = self.constraints.check_config(config)
        self.assertIn("test_constraint", result.failed)
        
        # Config with sum >= 10 should pass
        config = self.space.get_config((5, 6, 7, 8))  # sum = 26
        result = self.constraints.check_config(config)
        self.assertNotIn("test_constraint", result.failed)


if __name__ == "__main__":
    unittest.main()
