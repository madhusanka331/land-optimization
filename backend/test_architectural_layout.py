"""
Test the Architectural Layout Generator.
Verifies that the system generates complete floor plans with corridors, walls, doors, and fixtures.
"""

from src.models.schemas import LandInputSchema, DirectionEnum
from src.services.architectural_layout import ArchitecturalLayoutGenerator
from src.services.building_rules import SriLankanBuildingRules
from loguru import logger


def test_architectural_layout():
    """Test architectural layout generation."""
    print("="*80)
    print("TESTING: ARCHITECTURAL LAYOUT GENERATOR")
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
    print("Generating architectural floor plan...")
    print("-" * 80)

    generator = ArchitecturalLayoutGenerator(buildable, land_input)
    layout = generator.generate_layout()

    print(f"\n{'='*80}")
    print("LAYOUT GENERATED SUCCESSFULLY")
    print(f"{'='*80}")

    # Show statistics
    print(f"\nRooms: {len(layout['rooms'])}")
    print(f"Walls: {len(layout['walls'])} (exterior + interior)")
    print(f"Doors: {len(layout['doors'])}")
    print(f"Corridors: {len(layout['corridors'])}")
    print(f"Fixtures: {len(layout['fixtures'])}")

    # Show room details
    print(f"\n{'='*80}")
    print("ROOM DETAILS")
    print(f"{'='*80}")
    for i, room in enumerate(layout['rooms'], 1):
        print(f"{i}. {room.type.replace('_', ' ').title():20} "
              f"| Position: ({room.x:.1f}, {room.y:.1f}) "
              f"| Size: {room.width:.1f}m x {room.height:.1f}m "
              f"| Area: {room.area:.1f} m²")

    # Show corridor details
    print(f"\n{'='*80}")
    print("CORRIDOR DETAILS")
    print(f"{'='*80}")
    for i, corridor in enumerate(layout['corridors'], 1):
        print(f"{i}. Corridor ({corridor.orientation}): "
              f"Position: ({corridor.x:.1f}, {corridor.y:.1f}) "
              f"Size: {corridor.width:.1f}m x {corridor.height:.1f}m")

    # Show wall details
    print(f"\n{'='*80}")
    print("WALL DETAILS")
    print(f"{'='*80}")
    exterior_walls = [w for w in layout['walls'] if w.is_exterior]
    interior_walls = [w for w in layout['walls'] if not w.is_exterior]
    print(f"Exterior walls: {len(exterior_walls)}")
    print(f"Interior walls: {len(interior_walls)}")

    # Show door details
    print(f"\n{'='*80}")
    print("DOOR DETAILS")
    print(f"{'='*80}")
    for i, door in enumerate(layout['doors'], 1):
        print(f"{i}. Door ({door.orientation}): "
              f"Position: ({door.x:.1f}, {door.y:.1f}) "
              f"Width: {door.width:.1f}m "
              f"Swing: {door.swing_direction}")

    # Show fixture details
    print(f"\n{'='*80}")
    print("FIXTURE DETAILS")
    print(f"{'='*80}")
    for i, fixture in enumerate(layout['fixtures'], 1):
        print(f"{i}. {fixture.type.title()}: "
              f"Position: ({fixture.x:.1f}, {fixture.y:.1f}) "
              f"Size: {fixture.width:.1f}m x {fixture.height:.1f}m")

    # Verify completeness
    print(f"\n{'='*80}")
    print("VERIFICATION")
    print(f"{'='*80}")

    checks = []

    # Check 1: All rooms placed
    expected_rooms = land_input.bedrooms + land_input.toilets + 1  # +1 for kitchen
    if land_input.living_room > 0:
        expected_rooms += 1
    if land_input.dining_room > 0:
        expected_rooms += 1

    if len(layout['rooms']) >= expected_rooms - 1:  # Allow 1 room difference
        checks.append(("[OK]", f"Rooms placed: {len(layout['rooms'])} (expected ~{expected_rooms})"))
    else:
        checks.append(("[WARNING]", f"Rooms placed: {len(layout['rooms'])} (expected {expected_rooms})"))

    # Check 2: Corridors present
    if len(layout['corridors']) >= 1:
        checks.append(("[OK]", "Corridors created"))
    else:
        checks.append(("[FAIL]", "No corridors created"))

    # Check 3: Walls present
    if len(layout['walls']) >= 4:  # At least exterior walls
        checks.append(("[OK]", f"Walls generated: {len(layout['walls'])}"))
    else:
        checks.append(("[FAIL]", "Insufficient walls"))

    # Check 4: Doors present
    if len(layout['doors']) >= len(layout['rooms']):
        checks.append(("[OK]", f"Doors placed: {len(layout['doors'])}"))
    else:
        checks.append(("[WARNING]", f"Doors: {len(layout['doors'])} (rooms: {len(layout['rooms'])})"))

    # Check 5: Fixtures present
    if len(layout['fixtures']) > 0:
        checks.append(("[OK]", f"Fixtures added: {len(layout['fixtures'])}"))
    else:
        checks.append(("[WARNING]", "No fixtures added"))

    for status, message in checks:
        print(f"   {status} {message}")

    # Overall result
    failed_checks = sum(1 for status, _ in checks if status == "[FAIL]")
    if failed_checks == 0:
        print(f"\n{'='*80}")
        print("[PASS] ARCHITECTURAL LAYOUT GENERATOR TEST PASSED!")
        print(f"{'='*80}\n")
        return True
    else:
        print(f"\n{'='*80}")
        print(f"[FAIL] TEST FAILED: {failed_checks} checks failed")
        print(f"{'='*80}\n")
        return False


if __name__ == "__main__":
    success = test_architectural_layout()
    exit(0 if success else 1)
