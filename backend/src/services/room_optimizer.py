"""
Intelligent Room Optimizer
Automatically adjusts room count based on available land size to prevent overlaps
and ensure optimal floor plan generation.
"""

from typing import List, Dict, Tuple, Optional
from loguru import logger

from ..models.schemas import LandInputSchema, RoomSchema
from .building_rules import SriLankanBuildingRules


class RoomOptimizer:
    """
    Intelligent room optimizer that adjusts room requirements based on land size.

    Key Features:
    - Pre-checks if requested rooms can fit in available land
    - Automatically reduces room count if space is insufficient
    - Provides clear feedback about adjustments
    - Prevents overlaps by ensuring adequate space per room
    """

    # Minimum space per room type (includes circulation space)
    # These are realistic minimum sizes with margins
    MIN_SPACE_WITH_MARGIN = {
        'bedroom': 12.0,  # 9.3 + margin
        'master_bedroom': 14.0,  # 11.1 + margin
        'toilet': 4.0,  # 2.8 + margin
        'kitchen': 7.0,  # 5.6 + margin
        'living': 13.0,  # 11.1 + margin
        'dining': 11.0,  # 9.3 + margin
    }

    # Room priorities (higher = more important, kept when reducing)
    # CRITICAL: Living and Dining are HIGH priority - reduce ONLY extra bedrooms first!
    ROOM_PRIORITY = {
        'master_bedroom': 100,  # NEVER reduce
        'kitchen': 95,           # Essential
        'living': 90,            # HIGH priority - keep unless absolutely necessary
        'dining': 85,            # HIGH priority - keep unless absolutely necessary
        'toilet': 80,            # Keep at least 1
        'bedroom': 70,           # REDUCE FIRST - can go from 3→2→1→0
        'garden': 50,            # Lowest priority
    }

    def __init__(self, land_input: LandInputSchema):
        """
        Initialize room optimizer.

        Args:
            land_input: Original land input with user requirements
        """
        self.original_input = land_input
        self.buildable = SriLankanBuildingRules.get_buildable_area(
            land_input.length,
            land_input.width,
            land_input.total_area
        )
        self.adjustments = []  # Track all adjustments made

    def optimize_room_count(self) -> Tuple[LandInputSchema, List[str]]:
        """
        Optimize room count to fit available land.

        Returns:
            Tuple of (optimized_land_input, list_of_adjustment_messages)
        """
        logger.info("Starting intelligent room optimization...")

        # Create a copy to modify
        optimized = self.original_input.model_copy()
        messages = []

        # Calculate available space
        buildable_area = self.buildable['area']
        usable_area = buildable_area * 0.75  # Use only 75% to allow circulation

        logger.info(f"Buildable area: {buildable_area:.2f} sqm, Usable: {usable_area:.2f} sqm")

        # Calculate required space for current requirements
        required_space = self._calculate_required_space(optimized)

        logger.info(f"Required space: {required_space:.2f} sqm")

        if required_space <= usable_area:
            # All rooms fit!
            messages.append(
                f"[OK] All requested rooms fit comfortably in the available space "
                f"({required_space:.1f} sqm of {usable_area:.1f} sqm available)"
            )
            return optimized, messages

        # Need to reduce rooms
        shortage = required_space - usable_area
        messages.append(
            f"[WARNING] Insufficient space: Need {required_space:.1f} sqm but only "
            f"{usable_area:.1f} sqm available (shortage: {shortage:.1f} sqm)"
        )

        # Try to fit by reducing rooms intelligently
        optimized, reduction_msgs = self._reduce_rooms_intelligently(
            optimized, usable_area
        )
        messages.extend(reduction_msgs)

        # Verify final configuration fits
        final_required = self._calculate_required_space(optimized)
        if final_required > usable_area:
            messages.append(
                f"[WARNING] Even after reductions, space is tight "
                f"({final_required:.1f} sqm / {usable_area:.1f} sqm). "
                f"Floor plan may be cramped."
            )
        else:
            messages.append(
                f"[OK] Optimized layout fits: {final_required:.1f} sqm / {usable_area:.1f} sqm available"
            )

        return optimized, messages

    def _calculate_required_space(self, land_input: LandInputSchema) -> float:
        """
        Calculate total space needed for all rooms.

        Args:
            land_input: Land input with room requirements

        Returns:
            Total required area in square meters
        """
        total = 0.0

        # Bedrooms
        if land_input.bedrooms > 0:
            # First bedroom is master
            total += self.MIN_SPACE_WITH_MARGIN['master_bedroom']
            # Rest are regular bedrooms
            total += (land_input.bedrooms - 1) * self.MIN_SPACE_WITH_MARGIN['bedroom']

        # Toilets
        total += land_input.toilets * self.MIN_SPACE_WITH_MARGIN['toilet']

        # Kitchen (always required)
        total += self.MIN_SPACE_WITH_MARGIN['kitchen']

        # Living room
        if land_input.living_room > 0:
            total += self.MIN_SPACE_WITH_MARGIN['living']

        # Dining room
        if land_input.dining_room > 0:
            total += self.MIN_SPACE_WITH_MARGIN['dining']

        # Garden (if specified)
        if land_input.garden_area > 0:
            total += land_input.garden_area

        # Add 20% for circulation (corridors, etc.)
        total *= 1.20

        return total

    def _reduce_rooms_intelligently(
        self,
        land_input: LandInputSchema,
        available_space: float
    ) -> Tuple[LandInputSchema, List[str]]:
        """
        Reduce rooms intelligently based on priority.

        Strategy:
        1. Never reduce below 1 bedroom + 1 toilet + 1 kitchen (minimum viable house)
        2. Reduce in priority order: garden > dining > living > extra bedrooms > extra toilets
        3. Keep master bedroom always

        Args:
            land_input: Current land input
            available_space: Available space in sqm

        Returns:
            Tuple of (reduced_land_input, messages)
        """
        messages = []
        modified = land_input.model_copy()

        # NEW PRIORITY: Reduce BEDROOMS FIRST, keep Living + Dining as long as possible!
        # Reduction steps (in order of priority - least important first)
        steps = []

        # Step 1: Remove garden if exists (lowest priority)
        if modified.garden_area > 0:
            steps.append({
                'action': 'remove_garden',
                'description': f"Removed garden ({modified.garden_area:.1f} sqm)",
                'space_freed': modified.garden_area * 1.2
            })

        # Step 2: Reduce EXTRA BEDROOMS FIRST (3→2→1, keep at least master bedroom)
        # This is the MAIN reduction strategy
        if modified.bedrooms > 1:
            for i in range(modified.bedrooms - 1, 0, -1):
                steps.append({
                    'action': f'remove_bedroom_{i}',
                    'description': f"Reduced bedrooms from {i+1} to {i} (kept master + {i-1} bedroom{'s' if i > 1 else ''})",
                    'space_freed': self.MIN_SPACE_WITH_MARGIN['bedroom'] * 1.2,
                    'bedrooms_after': i
                })

        # Step 3: Reduce extra toilets if still needed (keep at least 1)
        if modified.toilets > 1:
            for i in range(modified.toilets - 1, 0, -1):
                if i == 1:
                    break  # Keep at least 1 toilet
                steps.append({
                    'action': f'remove_toilet_{i}',
                    'description': f"Reduced toilets from {i+1} to {i}",
                    'space_freed': self.MIN_SPACE_WITH_MARGIN['toilet'] * 1.2,
                    'toilets_after': i
                })

        # Step 4: Remove dining room ONLY if absolutely necessary
        if modified.dining_room > 0:
            steps.append({
                'action': 'remove_dining',
                'description': "Removed dining room (last resort)",
                'space_freed': self.MIN_SPACE_WITH_MARGIN['dining'] * 1.2
            })

        # Step 5: Remove living room ONLY as absolute last resort
        if modified.living_room > 0:
            steps.append({
                'action': 'remove_living',
                'description': "Removed living room (absolute last resort)",
                'space_freed': self.MIN_SPACE_WITH_MARGIN['living'] * 1.2
            })

        # Apply steps until we fit
        current_space = self._calculate_required_space(modified)

        for step in steps:
            if current_space <= available_space:
                break  # We fit! Stop reducing

            # Apply this reduction step
            action = step['action']

            if action == 'remove_garden':
                modified.garden_area = 0
                messages.append(f"[REDUCED] {step['description']} to save space")

            elif action == 'remove_dining':
                modified.dining_room = 0
                messages.append(f"[REDUCED] {step['description']} to save space")

            elif action == 'remove_living':
                modified.living_room = 0
                messages.append(f"[REDUCED] {step['description']} to save space")

            elif action.startswith('remove_bedroom_'):
                modified.bedrooms = step['bedrooms_after']
                messages.append(
                    f"[REDUCED] {step['description']} - insufficient space for {step['bedrooms_after']+1} bedrooms"
                )

            elif action.startswith('remove_toilet_'):
                modified.toilets = step['toilets_after']
                messages.append(
                    f"[REDUCED] {step['description']} - insufficient space for {step['toilets_after']+1} toilets"
                )

            # Recalculate required space
            current_space = self._calculate_required_space(modified)
            logger.info(f"After {step['description']}: Required space = {current_space:.2f} sqm")

        # Summary
        if len(messages) > 0:
            messages.insert(0, "[INFO] Intelligent room optimization applied:")

        return modified, messages

    def get_room_distribution_analysis(self, land_input: LandInputSchema) -> Dict:
        """
        Analyze how rooms will be distributed in the available space.

        Args:
            land_input: Land input to analyze

        Returns:
            Dictionary with distribution analysis
        """
        required_space = self._calculate_required_space(land_input)
        buildable_area = self.buildable['area']
        usable_area = buildable_area * 0.75

        # Calculate space per room
        total_rooms = (
            land_input.bedrooms +
            land_input.toilets +
            1 +  # kitchen
            land_input.living_room +
            land_input.dining_room
        )

        avg_space_per_room = usable_area / total_rooms if total_rooms > 0 else 0

        # Check if rooms will be cramped
        status = "optimal"
        if avg_space_per_room < 8:
            status = "very_cramped"
        elif avg_space_per_room < 12:
            status = "cramped"
        elif avg_space_per_room > 25:
            status = "spacious"

        return {
            'buildable_area': buildable_area,
            'usable_area': usable_area,
            'required_space': required_space,
            'remaining_space': usable_area - required_space,
            'space_utilization_percent': (required_space / usable_area * 100) if usable_area > 0 else 0,
            'total_rooms': total_rooms,
            'avg_space_per_room': avg_space_per_room,
            'status': status,
            'fits_comfortably': required_space <= usable_area,
            'buildable_dimensions': {
                'width': self.buildable['width'],
                'length': self.buildable['length'],
            }
        }

    @staticmethod
    def get_recommendations(analysis: Dict) -> List[str]:
        """
        Get recommendations based on space analysis.

        Args:
            analysis: Space analysis dictionary

        Returns:
            List of recommendation messages
        """
        recommendations = []

        if analysis['status'] == 'very_cramped':
            recommendations.append(
                "[WARNING] Rooms will be very cramped. Consider reducing room count or "
                "using a larger land plot."
            )
        elif analysis['status'] == 'cramped':
            recommendations.append(
                "[INFO] Rooms will be compact but functional. Ensure good space planning."
            )
        elif analysis['status'] == 'optimal':
            recommendations.append(
                "[OK] Good space distribution. Rooms will be comfortable."
            )
        elif analysis['status'] == 'spacious':
            recommendations.append(
                "[OK] Excellent space availability. Rooms will be very spacious."
            )

        if analysis['space_utilization_percent'] > 90:
            recommendations.append(
                "[WARNING] Very high space utilization. Limited flexibility in layout."
            )
        elif analysis['space_utilization_percent'] < 50:
            recommendations.append(
                "[INFO] Low space utilization. Consider adding more rooms or features."
            )

        return recommendations
