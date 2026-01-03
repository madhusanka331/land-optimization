"""
Test script for intelligent room optimization.
Demonstrates how the system handles different land sizes and room requirements.
"""

from src.models.schemas import LandInputSchema, DirectionEnum
from src.services.room_optimizer import RoomOptimizer
from src.services.genetic_optimizer import GeneticOptimizer
from src.services.visualization_service import VisualizationService
from loguru import logger


def test_scenario(name: str, land_input: LandInputSchema):
    """Test a specific scenario."""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {name}")
    print(f"{'='*80}")
    total_area = land_input.total_area or (land_input.length * land_input.width)
    print(f"Land: {land_input.length}m × {land_input.width}m ({total_area:.1f} m²)")
    print(f"Requested: {land_input.bedrooms} bedrooms, {land_input.toilets} toilets, "
          f"{land_input.living_room} living, {land_input.dining_room} dining")

    # Test room optimizer
    print("\n--- ROOM OPTIMIZATION ---")
    optimizer_service = RoomOptimizer(land_input)
    optimized_input, messages = optimizer_service.optimize_room_count()

    for msg in messages:
        print(f"  {msg}")

    print(f"\nOptimized: {optimized_input.bedrooms} bedrooms, {optimized_input.toilets} toilets, "
          f"{optimized_input.living_room} living, {optimized_input.dining_room} dining")

    # Get space analysis
    analysis = optimizer_service.get_room_distribution_analysis(optimized_input)
    print(f"\n--- SPACE ANALYSIS ---")
    print(f"  Buildable Area: {analysis['buildable_area']:.1f} m²")
    print(f"  Usable Area: {analysis['usable_area']:.1f} m²")
    print(f"  Required Space: {analysis['required_space']:.1f} m²")
    print(f"  Space Utilization: {analysis['space_utilization_percent']:.1f}%")
    print(f"  Avg Space per Room: {analysis['avg_space_per_room']:.1f} m²")
    print(f"  Status: {analysis['status']}")

    # Get recommendations
    recommendations = RoomOptimizer.get_recommendations(analysis)
    if recommendations:
        print(f"\n--- RECOMMENDATIONS ---")
        for rec in recommendations:
            print(f"  {rec}")

    # Run genetic algorithm (quick test with fewer generations)
    print("\n--- RUNNING GENETIC ALGORITHM ---")
    ga_optimizer = GeneticOptimizer(
        land_input=land_input,
        generations=20,  # Quick test
        population_size=30,
    )

    layout = ga_optimizer.optimize()

    print(f"\n--- RESULTS ---")
    print(f"  Fitness Score: {layout.fitness_score:.1f}/100")
    print(f"  Efficiency: {layout.efficiency_score:.1f}%")
    print(f"  Sunlight: {layout.sunlight_score:.1f}%")
    print(f"  Privacy: {layout.privacy_score:.1f}%")
    print(f"  Regulation Compliance: {layout.regulation_compliance:.1f}%")
    print(f"  Total Built Area: {layout.total_built_area:.1f} m²")
    print(f"  Coverage: {layout.coverage_percentage:.1f}%")

    # Check for overlaps
    print(f"\n--- ROOM DETAILS ---")
    for i, room in enumerate(layout.rooms, 1):
        print(f"  {i}. {room.type.replace('_', ' ').title()}: "
              f"{room.width:.1f}m × {room.height:.1f}m = {room.area:.1f} m² "
              f"at ({room.x:.1f}, {room.y:.1f})")

    # Generate visualization
    print(f"\n--- GENERATING VISUALIZATION ---")
    vis_service = VisualizationService()
    vis_path = vis_service.generate_floor_plan(
        land_input=land_input,
        layout=layout,
        filename=f"test_{name.lower().replace(' ', '_')}.png"
    )
    print(f"  Saved to: {vis_path}")

    return layout


def main():
    """Run all test scenarios."""
    print("="*80)
    print("INTELLIGENT ROOM OPTIMIZATION TEST SUITE")
    print("="*80)

    # Scenario 1: Small land with too many room requests
    scenario1 = LandInputSchema(
        length=10.0,
        width=8.0,
        bedrooms=3,
        toilets=2,
        kitchen=1,
        living_room=1,
        dining_room=1,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH,
    )
    test_scenario("Small Land - Too Many Rooms", scenario1)

    # Scenario 2: Medium land with reasonable requests
    scenario2 = LandInputSchema(
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
    test_scenario("Medium Land - Perfect Fit", scenario2)

    # Scenario 3: Large land with minimal requests
    scenario3 = LandInputSchema(
        length=20.0,
        width=15.0,
        bedrooms=2,
        toilets=1,
        kitchen=1,
        living_room=1,
        dining_room=0,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH,
    )
    test_scenario("Large Land - Spacious Layout", scenario3)

    # Scenario 4: Very small land
    scenario4 = LandInputSchema(
        length=8.0,
        width=6.0,
        bedrooms=2,
        toilets=1,
        kitchen=1,
        living_room=0,
        dining_room=0,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH,
    )
    test_scenario("Very Small Land - Minimal House", scenario4)

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED!")
    print("="*80)
    print("\nCheck the 'output' folder for generated floor plan visualizations.")


if __name__ == "__main__":
    main()
