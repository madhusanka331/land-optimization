"""
Input Validation Service
Validates user inputs and provides helpful feedback before optimization
"""

from typing import Dict, List
from src.models.schemas import LandInputSchema
from src.services.building_rules import SriLankanBuildingRules


class ValidationService:
    """
    Validates user input and checks feasibility
    Provides helpful error messages and warnings
    """

    def __init__(self):
        self.rules = SriLankanBuildingRules()

    def validate_input(self, land_input: LandInputSchema) -> Dict:
        """
        Comprehensive input validation

        Args:
            land_input: User's land input data

        Returns:
            Dictionary with validation status, errors, warnings, and feasibility
        """
        errors = []
        warnings = []

        # 1. Basic dimension validation
        dim_errors, dim_warnings = self._validate_dimensions(land_input)
        errors.extend(dim_errors)
        warnings.extend(dim_warnings)

        # 2. Requirements validation
        req_errors, req_warnings = self._validate_requirements(land_input)
        errors.extend(req_errors)
        warnings.extend(req_warnings)

        # 3. Aspect ratio and shape validation
        shape_warnings = self._validate_shape(land_input)
        warnings.extend(shape_warnings)

        # 4. Direction and orientation validation
        dir_warnings = self._validate_direction(land_input)
        warnings.extend(dir_warnings)

        # 5. Feasibility check using building rules
        feasibility = self.rules.validate_feasibility(land_input)

        # Merge feasibility errors
        errors.extend(feasibility['errors'])
        warnings.extend(feasibility['warnings'])

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'feasibility': feasibility
        }

    def _validate_dimensions(self, land_input: LandInputSchema) -> tuple:
        """Validate land dimensions"""
        errors = []
        warnings = []

        # Check for zero or negative dimensions
        if land_input.length <= 0:
            errors.append("Land length must be positive")

        if land_input.width <= 0:
            errors.append("Land width must be positive")

        # Calculate total area if not provided
        total_area = land_input.total_area or (land_input.length * land_input.width)

        # Check for unreasonably small land
        if total_area and total_area < 50:
            errors.append(
                f"Land area too small ({total_area:.1f}m²). "
                "Minimum 50m² recommended for residential construction"
            )
        elif total_area and total_area < 100:
            warnings.append(
                f"Small land size ({total_area:.1f}m²). "
                "May be challenging to fit all requirements"
            )

        # Check for unreasonably large land
        if total_area and total_area > 2000:
            warnings.append(
                f"Very large land ({total_area:.1f}m²). "
                "Consider dividing into multiple plots or adding more features"
            )

        # Check minimum dimensions
        if land_input.length < 5 or land_input.width < 5:
            warnings.append(
                "At least one dimension is very narrow (<5m). "
                "This may limit layout options"
            )

        return errors, warnings

    def _validate_requirements(self, land_input: LandInputSchema) -> tuple:
        """Validate room requirements"""
        errors = []
        warnings = []

        total_rooms = (land_input.bedrooms + land_input.toilets +
                      land_input.kitchen + land_input.living_room +
                      land_input.dining_room)

        # Check for zero rooms
        if total_rooms == 0:
            errors.append("At least one room is required")

        # Check for too many rooms
        if total_rooms > 15:
            errors.append(
                f"Too many rooms requested ({total_rooms}). "
                "Maximum 15 recommended for residential buildings"
            )
        elif total_rooms > 10:
            warnings.append(
                f"Large number of rooms ({total_rooms}). "
                "Ensure land size is adequate"
            )

        # Toilet requirements
        if land_input.toilets < 1:
            errors.append("At least 1 toilet is required")
        elif land_input.toilets > 5:
            errors.append("Maximum 5 toilets allowed")

        # Bedroom-to-toilet ratio check
        if land_input.bedrooms > 0 and land_input.toilets > 0:
            ratio = land_input.bedrooms / land_input.toilets

            if ratio > 3:
                warnings.append(
                    f"Low toilet-to-bedroom ratio ({land_input.toilets} toilet(s) "
                    f"for {land_input.bedrooms} bedroom(s)). "
                    "Consider adding more toilets for convenience"
                )

        # Kitchen check
        if land_input.kitchen < 1:
            warnings.append(
                "No kitchen specified. Most residential buildings require a kitchen"
            )
        elif land_input.kitchen > 2:
            warnings.append(
                f"Multiple kitchens ({land_input.kitchen}) is unusual for residential"
            )

        # Living room check
        if land_input.living_room < 1 and land_input.bedrooms > 1:
            warnings.append(
                "No living room specified. Recommended for multi-bedroom houses"
            )

        # Garden area validation
        total_area = land_input.total_area or (land_input.length * land_input.width)
        if land_input.garden_area > 0 and total_area:
            garden_percentage = (land_input.garden_area / total_area) * 100

            if garden_percentage > 50:
                warnings.append(
                    f"Garden area ({land_input.garden_area:.1f}m², "
                    f"{garden_percentage:.1f}%) is very large. "
                    "This may limit building space"
                )
            elif land_input.garden_area > total_area:
                errors.append(
                    f"Garden area ({land_input.garden_area:.1f}m²) exceeds "
                    f"total land area ({total_area:.1f}m²)"
                )

        # Parking spaces
        if land_input.parking_spaces > 5:
            warnings.append(
                f"Large number of parking spaces ({land_input.parking_spaces}). "
                "Ensure adequate land area"
            )

        return errors, warnings

    def _validate_shape(self, land_input: LandInputSchema) -> List[str]:
        """Validate land shape and aspect ratio"""
        warnings = []

        # Calculate aspect ratio (check for None values)
        if land_input.length is not None and land_input.width is not None:
            aspect_ratio = max(land_input.length, land_input.width) / \
                          min(land_input.length, land_input.width)
        else:
            return warnings  # Skip validation if dimensions are None

        if aspect_ratio > 5:
            warnings.append(
                f"Very elongated land shape (aspect ratio {aspect_ratio:.1f}:1). "
                "This may significantly limit layout options and room arrangements"
            )
        elif aspect_ratio > 3:
            warnings.append(
                f"Elongated land shape (aspect ratio {aspect_ratio:.1f}:1). "
                "Layout will be constrained by land proportions"
            )

        # Check for irregular shapes
        if land_input.shape == "irregular":
            warnings.append(
                "Irregular land shape specified. Actual buildable area may vary "
                "from calculated area. Manual verification recommended"
            )

        # Check if nearly square
        if 0.9 <= aspect_ratio <= 1.1:
            # This is actually good - no warning needed
            pass

        return warnings

    def _validate_direction(self, land_input: LandInputSchema) -> List[str]:
        """Validate direction and orientation"""
        warnings = []

        # Check if front direction and road side are the same
        # (they usually should be, but might differ in some cases)
        if land_input.front_direction != land_input.road_side:
            warnings.append(
                f"Front direction ({land_input.front_direction}) differs from "
                f"road side ({land_input.road_side}). Ensure this is intentional"
            )

        # Recommendations based on direction (for Sri Lankan context)
        if land_input.front_direction in ['south', 'southwest']:
            warnings.append(
                f"South-facing plots receive intense afternoon sun in Sri Lanka. "
                "Ensure adequate shading and ventilation in the design"
            )

        if land_input.front_direction in ['north', 'northeast']:
            # Actually beneficial in Sri Lankan context - no warning needed
            pass

        return warnings

    def check_minimum_land_size(self, bedrooms: int, toilets: int) -> Dict:
        """
        Calculate minimum land size needed for basic requirements

        Args:
            bedrooms: Number of bedrooms
            toilets: Number of toilets

        Returns:
            Dictionary with minimum land size and recommendation
        """
        min_size = self.rules.get_min_land_size(bedrooms, toilets)

        return {
            'minimum_land_size': min_size,
            'recommended_land_size': min_size * 1.3,  # 30% buffer
            'message': (
                f"For {bedrooms} bedroom(s) and {toilets} toilet(s), "
                f"minimum land size is approximately {min_size:.0f}m². "
                f"Recommended: {min_size * 1.3:.0f}m² for comfortable layout"
            )
        }

    def validate_before_optimization(self, land_input: LandInputSchema) -> Dict:
        """
        Final validation before running optimization
        This is the last check before expensive GA computation

        Args:
            land_input: User's land input

        Returns:
            Dictionary with validation result and detailed feedback
        """
        # Run full validation
        validation = self.validate_input(land_input)

        # Add additional pre-optimization checks
        if validation['valid']:
            # Estimate optimization time
            total_rooms = (land_input.bedrooms + land_input.toilets +
                          land_input.kitchen + land_input.living_room +
                          land_input.dining_room)

            # More rooms = longer optimization time
            estimated_time = 5 + (total_rooms * 0.5)  # Rough estimate

            validation['optimization_estimate'] = {
                'total_rooms': total_rooms,
                'estimated_time_seconds': estimated_time,
                'complexity': 'low' if total_rooms <= 5 else 'medium' if total_rooms <= 8 else 'high'
            }

            # Check if optimization is likely to succeed
            feasibility = validation['feasibility']
            remaining_percentage = (feasibility['remaining_area'] /
                                   feasibility['buildable_area'] * 100)

            if remaining_percentage < 10:
                validation['warnings'].append(
                    "Very tight fit. Optimization may struggle to find good layouts. "
                    "Consider reducing requirements or increasing land size"
                )
            elif remaining_percentage < 20:
                validation['warnings'].append(
                    "Limited space available. Optimization will prioritize efficiency"
                )

        return validation

    def get_optimization_suggestions(self, land_input: LandInputSchema) -> List[str]:
        """
        Provide suggestions to improve optimization results

        Args:
            land_input: User's land input

        Returns:
            List of helpful suggestions
        """
        suggestions = []

        # Check coverage
        feasibility = self.rules.validate_feasibility(land_input)

        if feasibility['is_feasible']:
            coverage = feasibility['coverage_if_built']

            if coverage > 60:
                suggestions.append(
                    "Consider reducing room count or sizes to improve ventilation and outdoor space"
                )

            if coverage < 40:
                suggestions.append(
                    "Land is underutilized. Consider adding more rooms or features"
                )

        # Room-specific suggestions
        if land_input.bedrooms > 2 and land_input.dining_room == 0:
            suggestions.append(
                "For larger homes, a separate dining room is recommended"
            )

        if land_input.bedrooms >= 3 and land_input.toilets < 2:
            suggestions.append(
                "Consider adding another toilet for homes with 3+ bedrooms"
            )

        total_area = land_input.total_area or (land_input.length * land_input.width)
        if land_input.garden_area == 0 and total_area and total_area > 150:
            suggestions.append(
                "Consider allocating space for a garden for better aesthetics and ventilation"
            )

        # Direction-based suggestions
        if land_input.front_direction in ['east', 'northeast']:
            suggestions.append(
                "East-facing plots are ideal in Sri Lanka. "
                "Bedrooms on the east side will get pleasant morning sun"
            )

        return suggestions
