"""
Simple script to calculate buildable area from land dimensions.
Shows how the system determines if rooms will fit on your land.
"""

from src.services.building_rules import SriLankanBuildingRules
from src.services.room_optimizer import RoomOptimizer
from src.models.schemas import LandInputSchema, DirectionEnum


def calculate_buildable_area(length: float, width: float, bedrooms: int, toilets: int):
    """
    Calculate buildable area and check if rooms will fit.

    Args:
        length: Land length in meters
        width: Land width in meters
        bedrooms: Number of bedrooms required
        toilets: Number of toilets required
    """
    print("="*80)
    print("BUILDABLE AREA CALCULATION")
    print("="*80)

    # Create land input
    land_input = LandInputSchema(
        length=length,
        width=width,
        bedrooms=bedrooms,
        toilets=toilets,
        kitchen=1,
        living_room=1,
        dining_room=1,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.NORTH
    )

    # Step 1: Calculate total land area
    total_land_area = length * width
    print(f"\n1. LAND DIMENSIONS")
    print(f"   Length: {length}m")
    print(f"   Width: {width}m")
    print(f"   Total Area: {total_land_area:.1f} m²")

    # Step 2: Calculate buildable area (after setbacks)
    buildable = SriLankanBuildingRules.get_buildable_area(
        length, width, total_land_area
    )

    print(f"\n2. SETBACKS (Mandatory empty spaces)")
    setbacks = buildable['setbacks']
    print(f"   Front Setback: {setbacks['front']}m")
    print(f"   Rear Setback: {setbacks['back']}m")
    print(f"   Left Setback: {setbacks['left']}m")
    print(f"   Right Setback: {setbacks['right']}m")

    print(f"\n3. BUILDABLE AREA (After applying setbacks)")
    print(f"   Length: {buildable['length']:.1f}m")
    print(f"   Width: {buildable['width']:.1f}m")
    print(f"   Total Buildable: {buildable['area']:.1f} m²")
    print(f"   Position: ({buildable['offset_x']:.1f}m, {buildable['offset_y']:.1f}m)")

    # Step 3: Calculate usable area (75% of buildable for circulation)
    usable_area = buildable['area'] * 0.75
    print(f"\n4. USABLE AREA (75% of buildable - allows for walls, corridors)")
    print(f"   Usable Area: {usable_area:.1f} m²")

    # Step 4: Calculate required space for rooms
    room_optimizer = RoomOptimizer(land_input)
    optimized_land_input, messages = room_optimizer.optimize_room_count()

    # Calculate room areas
    optimized_rooms = []

    # Master bedroom
    optimized_rooms.append({"type": "master_bedroom", "area": 14.4})

    # Regular bedrooms
    for i in range(optimized_land_input.bedrooms - 1):
        optimized_rooms.append({"type": f"bedroom_{i+2}", "area": 10.8})

    # Toilets
    for i in range(optimized_land_input.toilets):
        optimized_rooms.append({"type": f"toilet_{i+1}", "area": 4.4})

    # Kitchen
    if optimized_land_input.kitchen:
        optimized_rooms.append({"type": "kitchen", "area": 10.8})

    # Living room
    if optimized_land_input.living_room:
        optimized_rooms.append({"type": "living", "area": 14.4})

    # Dining room
    if optimized_land_input.dining_room:
        optimized_rooms.append({"type": "dining", "area": 10.8})

    total_required = sum(room['area'] for room in optimized_rooms)

    print(f"\n5. ROOM REQUIREMENTS")
    print(f"   Requested:")
    print(f"     - Bedrooms: {bedrooms}")
    print(f"     - Toilets: {toilets}")
    print(f"     - Kitchen: 1")
    print(f"     - Living Room: 1")
    print(f"     - Dining Room: 1")

    print(f"\n   Optimized Rooms:")
    for room in optimized_rooms:
        print(f"     - {room['type']}: {room['area']:.1f} m²")

    print(f"\n   Total Required Space: {total_required:.1f} m²")

    # Step 5: Check feasibility
    will_fit = total_required <= usable_area
    space_diff = usable_area - total_required

    print(f"\n6. FEASIBILITY CHECK")
    print(f"   Usable Area: {usable_area:.1f} m²")
    print(f"   Required Space: {total_required:.1f} m²")

    if will_fit:
        print(f"   [OK] STATUS: ROOMS WILL FIT!")
        print(f"   Extra Space: {space_diff:.1f} m²")
    else:
        print(f"   [WARNING] STATUS: NOT ENOUGH SPACE!")
        print(f"   Shortage: {-space_diff:.1f} m²")

    if messages:
        print(f"\n7. OPTIMIZATION MESSAGES:")
        for msg in messages:
            print(f"   {msg}")

    print("\n" + "="*80 + "\n")

    return {
        "total_land": total_land_area,
        "buildable_area": buildable['area'],
        "usable_area": usable_area,
        "required_space": total_required,
        "will_fit": will_fit,
        "space_remaining": space_diff if will_fit else -space_diff
    }


if __name__ == "__main__":
    # Example 1: Small land - 15m x 12m with 3BR
    print("\nEXAMPLE 1: Small Land")
    result1 = calculate_buildable_area(
        length=15.0,
        width=12.0,
        bedrooms=3,
        toilets=2
    )

    # Example 2: Medium land - 20m x 15m with 3BR
    print("\nEXAMPLE 2: Medium Land")
    result2 = calculate_buildable_area(
        length=20.0,
        width=15.0,
        bedrooms=3,
        toilets=2
    )

    # Example 3: Large land - 25m x 20m with 4BR
    print("\nEXAMPLE 3: Large Land")
    result3 = calculate_buildable_area(
        length=25.0,
        width=20.0,
        bedrooms=4,
        toilets=3
    )
