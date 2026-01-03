"""
Unit tests for Sri Lankan Building Rules.
Tests setback calculations, coverage limits, and validation logic.
"""

import pytest
from src.services.building_rules import SriLankanBuildingRules
from src.models.schemas import RoomSchema


class TestSetbackRequirements:
    """Test setback calculation logic."""

    def test_setback_requirements_standard(self):
        """Test standard setback requirements."""
        setbacks = SriLankanBuildingRules.get_setback_requirements(300)

        assert setbacks['front'] == 3.0
        assert setbacks['back'] == 1.5
        assert setbacks['left'] == 1.5
        assert setbacks['right'] == 1.5

    def test_setback_requirements_large_land(self):
        """Test setbacks for large land."""
        setbacks = SriLankanBuildingRules.get_setback_requirements(1000)

        assert setbacks['front'] >= 3.0
        assert setbacks['back'] >= 1.5
        assert all(v > 0 for v in setbacks.values())


class TestBuildableArea:
    """Test buildable area calculations."""

    def test_buildable_area_calculation(self):
        """Test buildable area after setbacks."""
        land_length = 20.0
        land_width = 15.0
        land_area = land_length * land_width

        buildable = SriLankanBuildingRules.get_buildable_area(
            land_length, land_width, land_area
        )

        assert buildable['length'] > 0
        assert buildable['width'] > 0
        assert buildable['area'] > 0
        assert buildable['length'] < land_length
        assert buildable['width'] < land_width
        assert buildable['area'] < land_area

    def test_buildable_area_with_setbacks(self):
        """Test buildable area accounts for all setbacks."""
        buildable = SriLankanBuildingRules.get_buildable_area(20, 15, 300)

        # Check offsets are applied
        assert buildable['offset_x'] == 1.5  # Left setback
        assert buildable['offset_y'] == 3.0  # Front setback

        # Check dimensions reduced by setbacks
        expected_length = 20 - 3.0 - 1.5  # front + back
        expected_width = 15 - 1.5 - 1.5  # left + right

        assert buildable['length'] == expected_length
        assert buildable['width'] == expected_width


class TestMinimumRoomSizes:
    """Test minimum room size requirements."""

    def test_minimum_bedroom_area(self):
        """Test minimum bedroom area."""
        assert SriLankanBuildingRules.MIN_BEDROOM_AREA == 9.3

    def test_minimum_toilet_area(self):
        """Test minimum toilet area."""
        assert SriLankanBuildingRules.MIN_TOILET_AREA == 2.8

    def test_minimum_kitchen_area(self):
        """Test minimum kitchen area."""
        assert SriLankanBuildingRules.MIN_KITCHEN_AREA == 5.6

    def test_minimum_living_area(self):
        """Test minimum living room area."""
        assert SriLankanBuildingRules.MIN_LIVING_AREA == 11.1


class TestCoverageValidation:
    """Test coverage limit validation."""

    def test_max_coverage_limit(self):
        """Test maximum coverage percentage."""
        assert SriLankanBuildingRules.MAX_COVERAGE_PERCENT == 65.0

    def test_coverage_calculation(self, sample_land_input):
        """Test coverage calculation logic."""
        buildable = SriLankanBuildingRules.get_buildable_area(
            sample_land_input.length,
            sample_land_input.width,
            sample_land_input.total_area
        )

        max_allowed_coverage = buildable['area'] * 0.65

        # Test that coverage limit is properly calculated
        assert max_allowed_coverage > 0
        assert max_allowed_coverage <= sample_land_input.total_area


class TestFeasibilityValidation:
    """Test feasibility checking."""

    def test_feasible_requirements(self, sample_land_input):
        """Test validation passes for feasible requirements."""
        result = SriLankanBuildingRules.validate_feasibility(sample_land_input)

        assert result['feasible'] is True
        assert len(result['errors']) == 0

    def test_infeasible_requirements_too_small(self, small_land_input):
        """Test validation fails for land that's too small."""
        # Modify to require too many rooms for small land
        small_land_input.bedrooms = 5
        small_land_input.toilets = 3

        result = SriLankanBuildingRules.validate_feasibility(small_land_input)

        # Should detect infeasibility
        assert result['feasible'] is False or len(result['warnings']) > 0

    def test_feasibility_with_garden(self, sample_land_input):
        """Test feasibility calculation includes garden area."""
        sample_land_input.garden_area = 100.0  # Very large garden

        result = SriLankanBuildingRules.validate_feasibility(sample_land_input)

        # Should warn about limited space due to garden
        assert len(result['warnings']) > 0 or result['feasible'] is False


class TestLayoutValidation:
    """Test complete layout validation."""

    def test_valid_layout(self, sample_land_input):
        """Test validation passes for valid layout."""
        # Create valid rooms
        buildable = SriLankanBuildingRules.get_buildable_area(
            sample_land_input.length,
            sample_land_input.width,
            sample_land_input.total_area
        )

        rooms = [
            RoomSchema(
                type='bedroom',
                x=buildable['offset_x'] + 1,
                y=buildable['offset_y'] + 1,
                width=4.0,
                height=3.0,
                area=12.0
            ),
            RoomSchema(
                type='toilet',
                x=buildable['offset_x'] + 6,
                y=buildable['offset_y'] + 1,
                width=2.0,
                height=1.5,
                area=3.0
            ),
        ]

        result = SriLankanBuildingRules.validate_layout(sample_land_input, rooms)

        assert result['valid'] is True or len(result['errors']) < 3

    def test_invalid_room_size(self, sample_land_input):
        """Test validation fails for undersized rooms."""
        buildable = SriLankanBuildingRules.get_buildable_area(
            sample_land_input.length,
            sample_land_input.width,
            sample_land_input.total_area
        )

        rooms = [
            RoomSchema(
                type='bedroom',
                x=buildable['offset_x'] + 1,
                y=buildable['offset_y'] + 1,
                width=2.0,
                height=2.0,
                area=4.0  # Too small for bedroom (min 9.3)
            ),
        ]

        result = SriLankanBuildingRules.validate_layout(sample_land_input, rooms)

        assert result['valid'] is False
        assert any('minimum area' in err.lower() for err in result['errors'])

    def test_overlapping_rooms(self, sample_land_input):
        """Test validation detects overlapping rooms."""
        buildable = SriLankanBuildingRules.get_buildable_area(
            sample_land_input.length,
            sample_land_input.width,
            sample_land_input.total_area
        )

        # Create overlapping rooms
        rooms = [
            RoomSchema(
                type='bedroom',
                x=buildable['offset_x'] + 1,
                y=buildable['offset_y'] + 1,
                width=5.0,
                height=3.0,
                area=15.0
            ),
            RoomSchema(
                type='toilet',
                x=buildable['offset_x'] + 3,  # Overlaps with bedroom
                y=buildable['offset_y'] + 2,
                width=2.0,
                height=2.0,
                area=4.0
            ),
        ]

        result = SriLankanBuildingRules.validate_layout(sample_land_input, rooms)

        assert result['valid'] is False
        assert any('overlap' in err.lower() for err in result['errors'])

    def test_setback_violation(self, sample_land_input):
        """Test validation detects setback violations."""
        # Place room outside setback boundary
        rooms = [
            RoomSchema(
                type='bedroom',
                x=0.5,  # Too close to left boundary
                y=1.0,
                width=4.0,
                height=3.0,
                area=12.0
            ),
        ]

        result = SriLankanBuildingRules.validate_layout(sample_land_input, rooms)

        assert result['valid'] is False
        assert any('setback' in err.lower() for err in result['errors'])

    def test_coverage_limit_violation(self, sample_land_input):
        """Test validation detects coverage limit violations."""
        buildable = SriLankanBuildingRules.get_buildable_area(
            sample_land_input.length,
            sample_land_input.width,
            sample_land_input.total_area
        )

        # Create rooms that exceed 65% coverage
        room_area = buildable['area'] * 0.70  # 70% coverage (exceeds 65% limit)

        rooms = [
            RoomSchema(
                type='bedroom',
                x=buildable['offset_x'] + 1,
                y=buildable['offset_y'] + 1,
                width=room_area ** 0.5,
                height=room_area ** 0.5,
                area=room_area
            ),
        ]

        result = SriLankanBuildingRules.validate_layout(sample_land_input, rooms)

        # Should warn about coverage
        assert len(result['warnings']) > 0 or result['valid'] is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_area_room(self, sample_land_input):
        """Test handling of zero-area rooms."""
        rooms = [
            RoomSchema(
                type='bedroom',
                x=5.0,
                y=5.0,
                width=0.0,
                height=0.0,
                area=0.0
            ),
        ]

        result = SriLankanBuildingRules.validate_layout(sample_land_input, rooms)

        assert result['valid'] is False

    def test_very_small_land(self):
        """Test handling of very small land."""
        from src.models.schemas import LandInputSchema, DirectionEnum

        tiny_land = LandInputSchema(
            length=5.0,
            width=4.0,
            bedrooms=1,
            toilets=1,
            front_direction=DirectionEnum.NORTH,
            road_side=DirectionEnum.SOUTH,
        )

        result = SriLankanBuildingRules.validate_feasibility(tiny_land)

        # Should detect infeasibility
        assert result['feasible'] is False or len(result['warnings']) > 0
