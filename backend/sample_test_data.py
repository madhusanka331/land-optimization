"""
Sample Test Data - Different Land Sizes
========================================
Test various land sizes to see how buildable area and room optimization changes.
Use this to understand the differences between small, medium, and large plots.
"""

from src.models.schemas import LandInputSchema, DirectionEnum
from src.services.building_rules import SriLankanBuildingRules
from src.services.room_optimizer import RoomOptimizer


# Sample data sets for testing different scenarios
SAMPLE_LANDS = {
    "tiny_plot": {
        "name": "Tiny Plot (10m × 8m)",
        "description": "Very small land - will require significant room reduction",
        "data": {
            "length": 10.0,
            "width": 8.0,
            "bedrooms": 3,
            "toilets": 2,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "small_plot": {
        "name": "Small Plot (15m × 12m)",
        "description": "Small residential plot - typical urban lot",
        "data": {
            "length": 15.0,
            "width": 12.0,
            "bedrooms": 3,
            "toilets": 2,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "medium_plot": {
        "name": "Medium Plot (20m × 15m)",
        "description": "Medium-sized suburban lot",
        "data": {
            "length": 20.0,
            "width": 15.0,
            "bedrooms": 3,
            "toilets": 2,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "large_plot": {
        "name": "Large Plot (25m × 20m)",
        "description": "Large residential plot",
        "data": {
            "length": 25.0,
            "width": 20.0,
            "bedrooms": 4,
            "toilets": 3,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "luxury_plot": {
        "name": "Luxury Plot (30m × 25m)",
        "description": "Luxury estate - plenty of space",
        "data": {
            "length": 30.0,
            "width": 25.0,
            "bedrooms": 5,
            "toilets": 4,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "narrow_plot": {
        "name": "Narrow Plot (25m × 10m)",
        "description": "Long and narrow plot - challenging layout",
        "data": {
            "length": 25.0,
            "width": 10.0,
            "bedrooms": 3,
            "toilets": 2,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "wide_plot": {
        "name": "Wide Plot (15m × 20m)",
        "description": "Wide and shallow plot",
        "data": {
            "length": 15.0,
            "width": 20.0,
            "bedrooms": 3,
            "toilets": 2,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },

    "square_plot": {
        "name": "Square Plot (18m × 18m)",
        "description": "Perfect square plot - optimal for layout",
        "data": {
            "length": 18.0,
            "width": 18.0,
            "bedrooms": 3,
            "toilets": 2,
            "kitchen": 1,
            "living_room": 1,
            "dining_room": 1,
            "front_direction": "north",
            "road_side": "north"
        }
    },
}


def analyze_land(land_key: str, land_data: dict, show_details: bool = True):
    """
    Analyze a land plot and show buildable area calculation.

    Args:
        land_key: Key from SAMPLE_LANDS
        land_data: Land configuration dict
        show_details: Whether to show detailed breakdown
    """
    info = SAMPLE_LANDS[land_key]
    data = info["data"]

    # Create land input
    land_input = LandInputSchema(**data)

    # Calculate buildable area
    total_area = data["length"] * data["width"]
    buildable = SriLankanBuildingRules.get_buildable_area(
        data["length"],
        data["width"],
        total_area
    )

    # Calculate usable area
    usable_area = buildable['area'] * 0.75

    # Optimize rooms
    room_optimizer = RoomOptimizer(land_input)
    optimized_land_input, messages = room_optimizer.optimize_room_count()

    # Calculate required space
    required_space = 0

    # Master bedroom
    required_space += 14.4

    # Regular bedrooms
    required_space += (optimized_land_input.bedrooms - 1) * 10.8

    # Toilets
    required_space += optimized_land_input.toilets * 4.4

    # Kitchen, living, dining
    if optimized_land_input.kitchen:
        required_space += 10.8
    if optimized_land_input.living_room:
        required_space += 14.4
    if optimized_land_input.dining_room:
        required_space += 10.8

    # Check if fits
    will_fit = required_space <= usable_area

    print(f"\n{'='*80}")
    print(f"{info['name']}")
    print(f"{'='*80}")
    print(f"{info['description']}")
    print(f"\nLAND DIMENSIONS:")
    print(f"   Size: {data['length']}m x {data['width']}m")
    print(f"   Total Area: {total_area:.1f} m2")

    if show_details:
        print(f"\nSETBACKS:")
        setbacks = buildable['setbacks']
        print(f"   Front: {setbacks['front']}m")
        print(f"   Rear: {setbacks['back']}m")
        print(f"   Left: {setbacks['left']}m")
        print(f"   Right: {setbacks['right']}m")

    print(f"\nBUILDABLE AREA:")
    print(f"   Dimensions: {buildable['length']:.1f}m x {buildable['width']:.1f}m")
    print(f"   Total Buildable: {buildable['area']:.1f} m2")
    print(f"   Usable (75%): {usable_area:.1f} m2")

    print(f"\nROOM REQUIREMENTS:")
    print(f"   Requested: {data['bedrooms']}BR, {data['toilets']}T, K, L, D")
    print(f"   Optimized: {optimized_land_input.bedrooms}BR, {optimized_land_input.toilets}T, K, L, D")
    print(f"   Required Space: {required_space:.1f} m2")

    print(f"\nFEASIBILITY:")
    if will_fit:
        extra = usable_area - required_space
        print(f"   Status: ROOMS WILL FIT! [OK]")
        print(f"   Extra Space: {extra:.1f} m2")
        print(f"   Coverage: {(required_space/usable_area)*100:.1f}%")
    else:
        shortage = required_space - usable_area
        print(f"   Status: NOT ENOUGH SPACE [WARNING]")
        print(f"   Shortage: {shortage:.1f} m2")

    if messages and show_details:
        print(f"\nMESSAGES:")
        for msg in messages:
            print(f"   {msg}")

    return {
        "land_key": land_key,
        "total_area": total_area,
        "buildable_area": buildable['area'],
        "usable_area": usable_area,
        "required_space": required_space,
        "will_fit": will_fit,
        "bedrooms_original": data['bedrooms'],
        "bedrooms_optimized": optimized_land_input.bedrooms,
    }


def compare_all_lands():
    """Compare all sample lands in a summary table."""
    print("\n" + "="*100)
    print("COMPARISON OF ALL LAND SIZES")
    print("="*100)

    results = []

    for land_key in SAMPLE_LANDS.keys():
        result = analyze_land(land_key, SAMPLE_LANDS[land_key], show_details=False)
        results.append(result)

    # Summary table
    print("\n" + "="*100)
    print("SUMMARY TABLE")
    print("="*100)
    print(f"{'Land Type':<20} {'Total':<10} {'Buildable':<12} {'Usable':<10} {'Required':<10} {'Fits?':<8} {'BR':<8}")
    print(f"{'':<20} {'(m²)':<10} {'(m²)':<12} {'(m²)':<10} {'(m²)':<10} {'':<8} {'Orig→Opt':<8}")
    print("-"*100)

    for result in results:
        land_name = SAMPLE_LANDS[result['land_key']]['name'].split('(')[0].strip()
        fits_icon = "✓" if result['will_fit'] else "✗"
        br_change = f"{result['bedrooms_original']}→{result['bedrooms_optimized']}"

        print(f"{land_name:<20} "
              f"{result['total_area']:<10.1f} "
              f"{result['buildable_area']:<12.1f} "
              f"{result['usable_area']:<10.1f} "
              f"{result['required_space']:<10.1f} "
              f"{fits_icon:<8} "
              f"{br_change:<8}")

    print("="*100)


def show_api_request_examples():
    """Show example API requests for different land sizes."""
    print("\n" + "="*100)
    print("API REQUEST EXAMPLES")
    print("="*100)

    for land_key, info in SAMPLE_LANDS.items():
        print(f"\n## {info['name']}")
        print(f"# {info['description']}")
        print(f"\ncurl -X POST 'http://localhost:8000/api/v1/optimization/calculate-buildable-area' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{")
        print(f"  \"length\": {info['data']['length']},")
        print(f"  \"width\": {info['data']['width']},")
        print(f"  \"bedrooms\": {info['data']['bedrooms']},")
        print(f"  \"toilets\": {info['data']['toilets']},")
        print(f"  \"kitchen\": {info['data']['kitchen']},")
        print(f"  \"living_room\": {info['data']['living_room']},")
        print(f"  \"dining_room\": {info['data']['dining_room']},")
        print(f"  \"front_direction\": \"{info['data']['front_direction']}\",")
        print(f"  \"road_side\": \"{info['data']['road_side']}\"")
        print(f"}}'")
        print()


def show_swagger_test_data():
    """Show formatted data for Swagger UI testing."""
    print("\n" + "="*100)
    print("SWAGGER UI TEST DATA")
    print("="*100)
    print("\nCopy-paste these JSON objects into Swagger UI:\n")

    for land_key, info in SAMPLE_LANDS.items():
        print(f"// {info['name']} - {info['description']}")
        print("{")
        print(f"  \"length\": {info['data']['length']},")
        print(f"  \"width\": {info['data']['width']},")
        print(f"  \"bedrooms\": {info['data']['bedrooms']},")
        print(f"  \"toilets\": {info['data']['toilets']},")
        print(f"  \"kitchen\": {info['data']['kitchen']},")
        print(f"  \"living_room\": {info['data']['living_room']},")
        print(f"  \"dining_room\": {info['data']['dining_room']},")
        print(f"  \"front_direction\": \"{info['data']['front_direction']}\",")
        print(f"  \"road_side\": \"{info['data']['road_side']}\"")
        print("}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "compare":
            # Show comparison table only
            compare_all_lands()
        elif sys.argv[1] == "api":
            # Show API examples
            show_api_request_examples()
        elif sys.argv[1] == "swagger":
            # Show Swagger test data
            show_swagger_test_data()
        elif sys.argv[1] in SAMPLE_LANDS:
            # Analyze specific land
            analyze_land(sys.argv[1], SAMPLE_LANDS[sys.argv[1]], show_details=True)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("\nAvailable options:")
            print("  python sample_test_data.py compare    - Show comparison table")
            print("  python sample_test_data.py api        - Show API examples")
            print("  python sample_test_data.py swagger    - Show Swagger test data")
            print(f"  python sample_test_data.py <land_key> - Analyze specific land")
            print(f"\nAvailable land keys: {', '.join(SAMPLE_LANDS.keys())}")
    else:
        # Default: show all analyses
        print("AI LAND OPTIMIZATION - SAMPLE TEST DATA")
        print("="*100)

        # Analyze each land
        for land_key in SAMPLE_LANDS.keys():
            analyze_land(land_key, SAMPLE_LANDS[land_key], show_details=True)

        # Show comparison
        compare_all_lands()

        print("\n" + "="*100)
        print("USAGE:")
        print("  python sample_test_data.py           - Show all analyses (default)")
        print("  python sample_test_data.py compare   - Show comparison table only")
        print("  python sample_test_data.py api       - Show API request examples")
        print("  python sample_test_data.py swagger   - Show Swagger UI test data")
        print("  python sample_test_data.py tiny_plot - Analyze specific land size")
        print("="*100)
