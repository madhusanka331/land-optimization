"""
Test Professional Floor Plan Generation
Generate floor plans matching the reference images style.
"""

from src.models.schemas import LandInputSchema, DirectionEnum, LayoutOutputSchema
from src.services.architectural_layout import ArchitecturalLayoutGenerator
from src.services.building_rules import SriLankanBuildingRules
from src.services.visualization_service import VisualizationService
from loguru import logger


def test_professional_floor_plan():
    """Generate a professional floor plan like the reference images."""
    print("=" * 80)
    print("GENERATING PROFESSIONAL FLOOR PLAN")
    print("=" * 80)

    # Test with a medium-sized house (similar to reference images)
    land_input = LandInputSchema(
        length=12.0,  # ~40 feet
        width=9.0,    # ~30 feet
        bedrooms=3,
        toilets=2,
        kitchen=1,
        living_room=1,
        dining_room=1,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH,
    )

    print(f"\nLand: {land_input.length}m x {land_input.width}m (~{land_input.length*3.28:.0f}' x {land_input.width*3.28:.0f}')")
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
    print("Generating architectural floor plan...")
    print("-" * 80)

    generator = ArchitecturalLayoutGenerator(buildable, land_input)
    layout_data = generator.generate_layout()

    print(f"\nLayout generated:")
    print(f"  - Rooms: {len(layout_data['rooms'])}")
    print(f"  - Walls: {len(layout_data['walls'])}")
    print(f"  - Doors: {len(layout_data['doors'])}")
    print(f"  - Corridors: {len(layout_data['corridors'])}")
    print(f"  - Fixtures: {len(layout_data['fixtures'])}")

    # Calculate total built area
    total_built_area = sum(room.area for room in layout_data['rooms'])
    land_area = land_input.length * land_input.width
    coverage_percentage = (total_built_area / land_area) * 100

    # Create LayoutOutputSchema for visualization
    layout = LayoutOutputSchema(
        rooms=layout_data['rooms'],
        fitness_score=85.0,
        efficiency_score=80.0,
        sunlight_score=85.0,
        privacy_score=90.0,
        regulation_compliance=95.0,
        total_built_area=total_built_area,
        coverage_percentage=coverage_percentage,
        architectural_elements=layout_data
    )

    # Generate professional visualization
    print("\n" + "=" * 80)
    print("GENERATING PROFESSIONAL VISUALIZATION")
    print("=" * 80)

    viz_service = VisualizationService(output_dir="./output")

    # Generate the floor plan with professional styling
    output_path = viz_service.generate_floor_plan(
        land_input=land_input,
        layout=layout,
        filename="professional_floor_plan.png",
        show_dimensions=False,  # Dimensions shown inside rooms only
        show_labels=True,
        show_setbacks=False,  # Don't show setback lines for clean look
        show_architectural=True,
        dpi=300  # High resolution for professional output
    )

    print(f"\n✓ Professional floor plan generated!")
    print(f"  Location: {output_path}")
    print(f"\nCompare this with the reference floor plans in backend/output/")
    print("=" * 80)

    return output_path


if __name__ == "__main__":
    try:
        result = test_professional_floor_plan()
        print(f"\n✅ SUCCESS! Floor plan saved at: {result}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
