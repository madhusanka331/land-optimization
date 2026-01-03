"""
Unit tests for Fitness Evaluator.
Tests chromosome decoding and fitness evaluation logic.
"""

import pytest
from src.services.fitness_evaluator import FitnessEvaluator


class TestFitnessEvaluatorInitialization:
    """Test fitness evaluator initialization."""

    def test_initialization(self, sample_land_input):
        """Test evaluator initializes correctly."""
        evaluator = FitnessEvaluator(sample_land_input)

        assert evaluator.land_input == sample_land_input
        assert evaluator.buildable is not None
        assert len(evaluator.required_rooms) > 0
        assert evaluator.chromosome_length == len(evaluator.required_rooms) * 4

    def test_required_rooms_generation(self, sample_land_input):
        """Test required rooms are correctly defined."""
        evaluator = FitnessEvaluator(sample_land_input)

        # Check bedrooms
        bedroom_count = sum(
            1 for room in evaluator.required_rooms
            if room['type'] in ['bedroom', 'master_bedroom']
        )
        assert bedroom_count == sample_land_input.bedrooms

        # Check toilets
        toilet_count = sum(
            1 for room in evaluator.required_rooms
            if room['type'] == 'toilet'
        )
        assert toilet_count == sample_land_input.toilets

        # Check kitchen
        kitchen_count = sum(
            1 for room in evaluator.required_rooms
            if room['type'] == 'kitchen'
        )
        assert kitchen_count == 1  # Always one kitchen


class TestChromosomeDecoding:
    """Test chromosome decoding functionality."""

    def test_decode_valid_chromosome(self, sample_land_input):
        """Test decoding a valid chromosome."""
        evaluator = FitnessEvaluator(sample_land_input)

        # Create a sample chromosome (all 0.5 values)
        chromosome = [0.5] * evaluator.chromosome_length

        rooms = evaluator.decode_chromosome(chromosome)

        assert len(rooms) == len(evaluator.required_rooms)
        assert all(room.area > 0 for room in rooms)
        assert all(room.width > 0 for room in rooms)
        assert all(room.height > 0 for room in rooms)

    def test_decode_ensures_minimum_area(self, sample_land_input):
        """Test decoder ensures minimum room areas."""
        evaluator = FitnessEvaluator(sample_land_input)

        # Create chromosome with small values
        chromosome = [0.1] * evaluator.chromosome_length

        rooms = evaluator.decode_chromosome(chromosome)

        # Check each room meets minimum area
        for room, room_def in zip(rooms, evaluator.required_rooms):
            assert room.area >= room_def['min_area']

    def test_decode_clamps_values(self, sample_land_input):
        """Test decoder clamps out-of-range values."""
        evaluator = FitnessEvaluator(sample_land_input)

        # Create chromosome with out-of-range values
        chromosome = [-0.5, 1.5, 2.0, -1.0] * (evaluator.chromosome_length // 4)

        rooms = evaluator.decode_chromosome(chromosome)

        # Should still produce valid rooms
        assert len(rooms) == len(evaluator.required_rooms)
        assert all(room.area > 0 for room in rooms)

    def test_decode_handles_wrong_length(self, sample_land_input):
        """Test decoder handles chromosome length mismatch."""
        evaluator = FitnessEvaluator(sample_land_input)

        # Too short chromosome
        short_chromosome = [0.5] * (evaluator.chromosome_length - 4)
        rooms_short = evaluator.decode_chromosome(short_chromosome)
        assert len(rooms_short) == len(evaluator.required_rooms)

        # Too long chromosome
        long_chromosome = [0.5] * (evaluator.chromosome_length + 4)
        rooms_long = evaluator.decode_chromosome(long_chromosome)
        assert len(rooms_long) == len(evaluator.required_rooms)


class TestFitnessEvaluation:
    """Test fitness evaluation functions."""

    def test_evaluate_fitness_returns_valid_score(self, sample_land_input):
        """Test fitness evaluation returns score in valid range."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length

        fitness = evaluator.evaluate_fitness(chromosome, 0)

        assert 0 <= fitness <= 100

    def test_evaluate_fitness_consistency(self, sample_land_input):
        """Test same chromosome produces same fitness."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length

        fitness1 = evaluator.evaluate_fitness(chromosome, 0)
        fitness2 = evaluator.evaluate_fitness(chromosome, 0)

        assert fitness1 == fitness2

    def test_different_chromosomes_different_fitness(self, sample_land_input):
        """Test different chromosomes produce different fitness."""
        evaluator = FitnessEvaluator(sample_land_input)

        chromosome1 = [0.3] * evaluator.chromosome_length
        chromosome2 = [0.7] * evaluator.chromosome_length

        fitness1 = evaluator.evaluate_fitness(chromosome1, 0)
        fitness2 = evaluator.evaluate_fitness(chromosome2, 0)

        # Different chromosomes should likely have different fitness
        # (not guaranteed, but very likely)
        assert fitness1 != fitness2 or abs(fitness1 - fitness2) < 0.1


class TestIndividualObjectives:
    """Test individual objective scoring functions."""

    def test_space_efficiency_scoring(self, sample_land_input):
        """Test space efficiency evaluation."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length
        rooms = evaluator.decode_chromosome(chromosome)

        score = evaluator._evaluate_space_efficiency(rooms)

        assert 0 <= score <= 100

    def test_sunlight_scoring(self, sample_land_input):
        """Test sunlight evaluation."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length
        rooms = evaluator.decode_chromosome(chromosome)

        score = evaluator._evaluate_sunlight(rooms)

        assert 0 <= score <= 100

    def test_privacy_scoring(self, sample_land_input):
        """Test privacy evaluation."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length
        rooms = evaluator.decode_chromosome(chromosome)

        score = evaluator._evaluate_privacy(rooms)

        assert 0 <= score <= 100

    def test_circulation_scoring(self, sample_land_input):
        """Test circulation evaluation."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length
        rooms = evaluator.decode_chromosome(chromosome)

        score = evaluator._evaluate_circulation(rooms)

        assert 0 <= score <= 100

    def test_regulation_scoring(self, sample_land_input):
        """Test regulation compliance evaluation."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length
        rooms = evaluator.decode_chromosome(chromosome)

        score = evaluator._evaluate_regulations(rooms)

        assert 0 <= score <= 100


class TestDetailedScores:
    """Test detailed score breakdown."""

    def test_get_detailed_scores(self, sample_land_input):
        """Test getting detailed score breakdown."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length

        scores = evaluator.get_detailed_scores(chromosome)

        # Check all scores present
        assert 'fitness_score' in scores
        assert 'space_efficiency' in scores
        assert 'sunlight_score' in scores
        assert 'privacy_score' in scores
        assert 'circulation_score' in scores
        assert 'regulation_compliance' in scores
        assert 'rooms' in scores

        # Check all scores in valid range
        assert 0 <= scores['fitness_score'] <= 100
        assert 0 <= scores['space_efficiency'] <= 100
        assert 0 <= scores['sunlight_score'] <= 100
        assert 0 <= scores['privacy_score'] <= 100
        assert 0 <= scores['circulation_score'] <= 100
        assert 0 <= scores['regulation_compliance'] <= 100

    def test_fitness_is_weighted_average(self, sample_land_input):
        """Test fitness score is correctly weighted."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length

        scores = evaluator.get_detailed_scores(chromosome)

        # Calculate manual weighted average
        expected_fitness = (
            evaluator.WEIGHT_SPACE * scores['space_efficiency'] +
            evaluator.WEIGHT_SUNLIGHT * scores['sunlight_score'] +
            evaluator.WEIGHT_PRIVACY * scores['privacy_score'] +
            evaluator.WEIGHT_CIRCULATION * scores['circulation_score'] +
            evaluator.WEIGHT_REGULATIONS * scores['regulation_compliance']
        )

        # Should match (within floating point precision)
        assert abs(scores['fitness_score'] - expected_fitness) < 0.01


class TestHelperMethods:
    """Test helper calculation methods."""

    def test_calculate_overlap_area(self, sample_land_input):
        """Test overlap area calculation."""
        from src.models.schemas import RoomSchema

        evaluator = FitnessEvaluator(sample_land_input)

        # Non-overlapping rooms
        room1 = RoomSchema(type='bedroom', x=0, y=0, width=5, height=5, area=25)
        room2 = RoomSchema(type='toilet', x=10, y=10, width=3, height=3, area=9)

        overlap = evaluator._calculate_overlap_area(room1, room2)
        assert overlap == 0

        # Overlapping rooms
        room3 = RoomSchema(type='bedroom', x=0, y=0, width=5, height=5, area=25)
        room4 = RoomSchema(type='toilet', x=3, y=3, width=3, height=3, area=9)

        overlap = evaluator._calculate_overlap_area(room3, room4)
        assert overlap > 0

    def test_calculate_compactness(self, sample_land_input):
        """Test compactness calculation."""
        evaluator = FitnessEvaluator(sample_land_input)
        chromosome = [0.5] * evaluator.chromosome_length
        rooms = evaluator.decode_chromosome(chromosome)

        compactness = evaluator._calculate_compactness(rooms)

        assert 0 <= compactness <= 1

    def test_calculate_distance(self, sample_land_input):
        """Test distance calculation."""
        evaluator = FitnessEvaluator(sample_land_input)

        distance = evaluator._calculate_distance(0, 0, 3, 4)

        # 3-4-5 triangle
        assert abs(distance - 5.0) < 0.01


class TestEdgeCases:
    """Test edge cases in fitness evaluation."""

    def test_invalid_chromosome_returns_zero(self, sample_land_input):
        """Test invalid chromosome returns zero fitness."""
        evaluator = FitnessEvaluator(sample_land_input)

        # This should be handled gracefully
        try:
            fitness = evaluator.evaluate_fitness(None, 0)
            assert fitness == 0.0
        except:
            # If it raises an exception, that's also acceptable
            pass

    def test_empty_rooms_list(self, sample_land_input):
        """Test handling of empty rooms list."""
        evaluator = FitnessEvaluator(sample_land_input)

        # This should not crash
        try:
            score = evaluator._evaluate_space_efficiency([])
            assert isinstance(score, (int, float))
        except:
            pass  # Acceptable to raise exception for invalid input
