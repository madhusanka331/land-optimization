"""
Test Architectural Floor Plan Visualization.
Generates and visualizes a complete architectural floor plan with walls, doors, corridors, and fixtures.
"""

from src.models.schemas import LandInputSchema, DirectionEnum, LayoutOutputSchema
from src.services.architectural_layout import ArchitecturalLayoutGenerator
from src.services.visualization_service import VisualizationService
from src.services.building_rules import SriLankanBuildingRules
from loguru import logger


def test_architectural_visualization():
    """Test complete architectural floor plan generation and visualization."""
    print("="*80)
    print("TESTING: ARCHITECTURAL FLOOR PLAN VISUALIZATION")
    print("="*80)

    # Test with medium-sized land
    land_input = LandInputSchema(
        length=15.0,
        width=12.0,
        bedrooms=3,
        toilets=2,
        kitchen=1,
        living_room=1,
        dining_room=1,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH,
    )

    print(f"\nLand: {land_input.length}m x {land_input.width}m")
    print(f"Rooms: {land_input.bedrooms}BR, {land_input.toilets}T, Living, Dining, Kitchen\n")

    # Calculate buildable area
    buildable = SriLankanBuildingRules.get_buildable_area(
        land_input.length,
        land_input.width,
        land_input.length * land_input.width
    )

    print(f"Buildable Area: {buildable['width']:.1f}m x {buildable['length']:.1f}m")
    print(f"Offset: ({buildable['offset_x']:.1f}, {buildable['offset_y']:.1f})\n")

    # Generate architectural layout
    print("Generating architectural floor plan with walls, doors, corridors, fixtures...")
    print("-" * 80)

    generator = ArchitecturalLayoutGenerator(buildable, land_input)
    architectural_layout = generator.generate_layout()

    print(f"\n{'='*80}")
    print("LAYOUT GENERATED")
    print(f"{'='*80}")
    print(f"Rooms: {len(architectural_layout['rooms'])}")
    print(f"Walls: {len(architectural_layout['walls'])}")
    print(f"Doors: {len(architectural_layout['doors'])}")
    print(f"Corridors: {len(architectural_layout['corridors'])}")
    print(f"Fixtures: {len(architectural_layout['fixtures'])}")

    # Create LayoutOutputSchema with architectural elements
    total_built = sum(room.area for room in architectural_layout['rooms'])
    buildable_area_sqm = buildable['width'] * buildable['length']
    land_area = land_input.total_area or (land_input.length * land_input.width)

    layout = LayoutOutputSchema(
        rooms=architectural_layout['rooms'],
        total_built_area=total_built,
        buildable_area=buildable_area_sqm,
        land_area=land_area,
        fitness_score=85.0,  # Mock fitness score
        efficiency_score=75.0,
        vastu_score=80.0,
        sunlight_score=75.0,
        privacy_score=70.0,
        regulation_compliance=True,
        coverage_percentage=(total_built / land_area) * 100,
        optimization_messages=["Architectural floor plan generated with corridors and walls"],
    )

    # Generate visualization
    print(f"\n{'='*80}")
    print("GENERATING VISUALIZATION")
    print(f"{'='*80}")

    vis_service = VisualizationService()

    # Temporarily add architectural elements to layout (using __dict__ to bypass Pydantic validation)
    layout.__dict__['architectural_elements'] = architectural_layout

    vis_path = vis_service.generate_floor_plan(
        land_input=land_input,
        layout=layout,
        filename="architectural_floor_plan.png",
        show_architectural=True,
        show_dimensions=True,
        show_labels=True
    )

    print(f"\n[SUCCESS] Architectural floor plan visualization saved: {vis_path}")

    # Show summary
    print(f"\n{'='*80}")
    print("ARCHITECTURAL FLOOR PLAN SUMMARY")
    print(f"{'='*80}")
    print(f"  Land: {land_input.length}m x {land_input.width}m ({land_area:.1f} m²)")
    print(f"  Buildable: {buildable['width']:.1f}m x {buildable['length']:.1f}m ({buildable_area_sqm:.1f} m²)")
    print(f"  Built: {layout.total_built_area:.1f} m²")
    print(f"  Coverage: {layout.coverage_percentage:.1f}%")
    print()
    print(f"  Rooms: {len(architectural_layout['rooms'])}")
    print(f"  Corridors: {len(architectural_layout['corridors'])}")
    print(f"  Walls: {len(architectural_layout['walls'])} (exterior + interior)")
    print(f"  Doors: {len(architectural_layout['doors'])}")
    print(f"  Fixtures: {len(architectural_layout['fixtures'])} (toilets, sinks, stove, fridge)")
    print()
    print(f"  Visualization: {vis_path}")

    print(f"\n{'='*80}")
    print("[PASS] ARCHITECTURAL VISUALIZATION TEST PASSED!")
    print(f"{'='*80}\n")

    return True


if __name__ == "__main__":
    success = test_architectural_visualization()
    exit(0 if success else 1)
