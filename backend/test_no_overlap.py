"""
Test to verify ZERO overlap floor plans are generated.
Uses production settings (200 generations, 100 population).
"""

from src.models.schemas import LandInputSchema, DirectionEnum
from src.services.genetic_optimizer import GeneticOptimizer
from src.services.visualization_service import VisualizationService
from src.services.building_rules import SriLankanBuildingRules
from loguru import logger


def check_overlaps(layout):
    """Check if layout has any overlapping rooms."""
    rooms = layout.rooms
    overlaps = []

    for i, room1 in enumerate(rooms):
        for j, room2 in enumerate(rooms[i+1:], i+1):
            if SriLankanBuildingRules._rooms_overlap(room1, room2):
                overlap_msg = f"Room {i+1} ({room1.type}) overlaps with Room {j+1} ({room2.type})"
                overlaps.append(overlap_msg)

    return overlaps


def test_no_overlap():
    """Test that floor plans have ZERO overlaps."""
    print("="*80)
    print("TESTING: ZERO OVERLAP FLOOR PLAN GENERATION")
    print("="*80)

    # Test with medium-sized land (should fit all rooms)
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

    print(f"\nLand: {land_input.length}m × {land_input.width}m")
    print(f"Rooms: {land_input.bedrooms}BR, {land_input.toilets}T, Living, Dining, Kitchen\n")

    # Run optimization with PRODUCTION settings (200 generations, 100 population)
    print("Running optimization with PRODUCTION settings:")
    print("  - Generations: 200 (increased from 100)")
    print("  - Population: 100 (increased from 50)")
    print("  - Overlap penalty: MAXIMUM (fitness = 0.0 if any overlap)")
    print("\nThis may take 1-2 minutes...\n")

    optimizer = GeneticOptimizer(land_input=land_input)
    layout = optimizer.optimize()

    print(f"\n{'='*80}")
    print("OPTIMIZATION COMPLETE")
    print(f"{'='*80}")
    print(f"Fitness Score: {layout.fitness_score:.1f}/100")
    print(f"Efficiency: {layout.efficiency_score:.1f}%")
    print(f"Total Built Area: {layout.total_built_area:.1f} m²")
    print(f"Coverage: {layout.coverage_percentage:.1f}%")

    # Check for overlaps
    print(f"\n{'='*80}")
    print("OVERLAP CHECK")
    print(f"{'='*80}")

    overlaps = check_overlaps(layout)

    if len(overlaps) == 0:
        print("[OK] SUCCESS: NO OVERLAPS DETECTED!")
        print("   All rooms are properly separated.")
    else:
        print(f"[FAIL] FAILURE: {len(overlaps)} OVERLAPS DETECTED!")
        for overlap in overlaps:
            print(f"   - {overlap}")

    # Show room details
    print(f"\n{'='*80}")
    print("ROOM LAYOUT DETAILS")
    print(f"{'='*80}")
    for i, room in enumerate(layout.rooms, 1):
        print(f"{i}. {room.type.replace('_', ' ').title():20} "
              f"| Position: ({room.x:.1f}, {room.y:.1f}) "
              f"| Size: {room.width:.1f}m × {room.height:.1f}m "
              f"| Area: {room.area:.1f} m²")

    # Generate visualization
    print(f"\n{'='*80}")
    print("GENERATING VISUALIZATION")
    print(f"{'='*80}")
    vis_service = VisualizationService()
    vis_path = vis_service.generate_floor_plan(
        land_input=land_input,
        layout=layout,
        filename="test_no_overlap_production.png"
    )
    print(f"[SAVED] Floor plan saved: {vis_path}")

    # Return test result
    if len(overlaps) == 0:
        print(f"\n{'='*80}")
        print("[PASS] TEST PASSED: Zero overlap floor plan generated successfully!")
        print(f"{'='*80}\n")
        return True
    else:
        print(f"\n{'='*80}")
        print("[FAIL] TEST FAILED: Overlaps still present")
        print(f"{'='*80}\n")
        return False


if __name__ == "__main__":
    success = test_no_overlap()
    exit(0 if success else 1)
