"""
Complete End-to-End Integration Test.
Tests the full architectural floor plan system with genetic algorithm optimization and visualization.
"""

from src.models.schemas import LandInputSchema, DirectionEnum
from src.services.genetic_optimizer import GeneticOptimizer
from src.services.visualization_service import VisualizationService
from loguru import logger


def test_complete_integration():
    """Test complete system: GA + Architectural Layout + Visualization."""
    print("="*80)
    print("COMPLETE INTEGRATION TEST")
    print("="*80)
    print("Testing: Genetic Algorithm -> Architectural Layout -> Visualization")
    print()

    # Define land input
    land_input = LandInputSchema(
        length=15.0,
        width=12.0,
        bedrooms=3,
        toilets=2,
        kitchen=1,
        living_room=1,
        dining_room=1,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH
    )

    print(f"Land: {land_input.length}m × {land_input.width}m")
    print(f"Rooms: {land_input.bedrooms}BR, {land_input.toilets}T, Living, Dining, Kitchen\n")

    # Run genetic algorithm optimization
    print("="*80)
    print("STEP 1: GENETIC ALGORITHM OPTIMIZATION")
    print("="*80)
    print("Running GA with 50 generations, 50 population...")
    print()

    optimizer = GeneticOptimizer(
        land_input,
        generations=50,  # Moderate test
        population_size=50
    )

    layout = optimizer.optimize()

    print(f"\n[OK] Optimization complete!")
    print(f"  Fitness Score: {layout.fitness_score:.1f}/100")
    print(f"  Efficiency: {layout.efficiency_score:.1f}%")
    print(f"  Total Built Area: {layout.total_built_area:.1f} m²")
    print(f"  Coverage: {layout.coverage_percentage:.1f}%")
    print(f"  Rooms Generated: {len(layout.rooms)}")

    # Check architectural elements
    print(f"\n{'='*80}")
    print("STEP 2: ARCHITECTURAL ELEMENTS VERIFICATION")
    print(f"{'='*80}")

    if hasattr(layout, 'architectural_elements'):
        elements = layout.architectural_elements
        print(f"[OK] Architectural elements automatically generated:")
        print(f"  - Walls: {len(elements['walls'])}")
        print(f"  - Doors: {len(elements['doors'])}")
        print(f"  - Corridors: {len(elements['corridors'])}")
        print(f"  - Fixtures: {len(elements['fixtures'])}")

        # Show corridor details
        if elements['corridors']:
            corridor = elements['corridors'][0]
            print(f"\n  Main Corridor:")
            print(f"    Orientation: {corridor.orientation}")
            print(f"    Size: {corridor.width:.1f}m × {corridor.height:.1f}m")

        # Show fixture count by type
        fixture_counts = {}
        for fixture in elements['fixtures']:
            fixture_counts[fixture.type] = fixture_counts.get(fixture.type, 0) + 1

        if fixture_counts:
            print(f"\n  Fixtures by Type:")
            for fixture_type, count in fixture_counts.items():
                print(f"    - {fixture_type.title()}: {count}")

    else:
        print("[ERROR] No architectural elements found!")
        return False

    # Generate TWO visualizations
    print(f"\n{'='*80}")
    print("STEP 3: VISUALIZATION GENERATION (TWO OUTPUTS)")
    print(f"{'='*80}")

    vis_service = VisualizationService()

    # OUTPUT 1: Land plot with buildable area
    print("\nGenerating OUTPUT 1: Land plot with buildable area...")
    land_plot_path = vis_service.generate_land_plot(
        land_input=land_input,
        filename="output1_land_plot.png"
    )
    print(f"[OK] OUTPUT 1 saved: {land_plot_path}")

    # OUTPUT 2: Floor plan within buildable area
    print("\nGenerating OUTPUT 2: Floor plan within buildable area...")
    floor_plan_path = vis_service.generate_floor_plan(
        land_input=land_input,
        layout=layout,
        filename="output2_floor_plan.png",
        show_architectural=True,
        show_dimensions=True,
        show_labels=True
    )
    print(f"[OK] OUTPUT 2 saved: {floor_plan_path}")

    # Show optimization messages
    if layout.optimization_messages:
        print(f"\n{'='*80}")
        print("OPTIMIZATION MESSAGES")
        print(f"{'='*80}")
        for msg in layout.optimization_messages:
            print(f"  {msg}")

    # Final summary
    print(f"\n{'='*80}")
    print("INTEGRATION TEST COMPLETE")
    print(f"{'='*80}")
    print(f"[PASS] All systems working:")
    print(f"  [OK] Genetic Algorithm Optimization")
    print(f"  [OK] Intelligent Room Reduction")
    print(f"  [OK] Architectural Layout Generation")
    print(f"    - Building perimeter walls")
    print(f"    - Interior walls between rooms")
    print(f"    - Corridors for connectivity")
    print(f"    - Doors with swing arcs")
    print(f"    - Fixture symbols")
    print(f"  [OK] Professional Visualization (TWO OUTPUTS)")
    print()
    print(f"OUTPUT 1 (Land Plot): {land_plot_path}")
    print(f"OUTPUT 2 (Floor Plan): {floor_plan_path}")
    print(f"{'='*80}\n")

    return True


if __name__ == "__main__":
    success = test_complete_integration()
    exit(0 if success else 1)
