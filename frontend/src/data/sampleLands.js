// Sample land data matching backend sample_test_data.py
export const SAMPLE_LANDS = {
  tiny_plot: {
    name: "Tiny Plot (10m × 8m)",
    description: "Very small land - will require significant room reduction",
    expectedResult: "FAILS - Not enough space",
    data: {
      length: 10.0,
      width: 8.0,
      bedrooms: 3,
      toilets: 2,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  small_plot: {
    name: "Small Plot (15m × 12m)",
    description: "Small residential plot - typical urban lot",
    expectedResult: "TIGHT FIT - Room reduction needed",
    data: {
      length: 15.0,
      width: 12.0,
      bedrooms: 3,
      toilets: 2,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  medium_plot: {
    name: "Medium Plot (20m × 15m)",
    description: "Medium-sized suburban lot",
    expectedResult: "COMFORTABLE - All rooms fit",
    data: {
      length: 20.0,
      width: 15.0,
      bedrooms: 3,
      toilets: 2,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  large_plot: {
    name: "Large Plot (25m × 20m)",
    description: "Large residential plot",
    expectedResult: "SPACIOUS - Plenty of extra space",
    data: {
      length: 25.0,
      width: 20.0,
      bedrooms: 4,
      toilets: 3,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  luxury_plot: {
    name: "Luxury Plot (30m × 25m)",
    description: "Luxury estate - plenty of space",
    expectedResult: "ESTATE - Enormous extra space",
    data: {
      length: 30.0,
      width: 25.0,
      bedrooms: 5,
      toilets: 4,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  narrow_plot: {
    name: "Narrow Plot (25m × 10m)",
    description: "Long and narrow plot - challenging layout",
    expectedResult: "CHALLENGING - Linear layout",
    data: {
      length: 25.0,
      width: 10.0,
      bedrooms: 3,
      toilets: 2,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  wide_plot: {
    name: "Wide Plot (15m × 20m)",
    description: "Wide and shallow plot",
    expectedResult: "COMFORTABLE - Good flexibility",
    data: {
      length: 15.0,
      width: 20.0,
      bedrooms: 3,
      toilets: 2,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },

  square_plot: {
    name: "Square Plot (18m × 18m)",
    description: "Perfect square plot - optimal for layout",
    expectedResult: "OPTIMAL - Best efficiency",
    data: {
      length: 18.0,
      width: 18.0,
      bedrooms: 3,
      toilets: 2,
      kitchen: 1,
      living_room: 1,
      dining_room: 1,
      front_direction: "north",
      road_side: "north"
    }
  },
};

export const DIRECTION_OPTIONS = [
  { value: 'north', label: 'North' },
  { value: 'south', label: 'South' },
  { value: 'east', label: 'East' },
  { value: 'west', label: 'West' },
];
