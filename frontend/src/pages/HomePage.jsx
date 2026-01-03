import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white p-8 rounded-lg shadow-lg">
        <h1 className="text-4xl font-bold mb-4">AI Land Optimization System</h1>
        <p className="text-xl text-primary-100">
          Intelligent floor plan generation using genetic algorithms and Sri Lankan building codes
        </p>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Calculate Buildable Area</h2>
          <p className="text-gray-600 mb-4">
            Enter land dimensions and room requirements to calculate buildable area, setbacks, and feasibility.
          </p>
          <Link
            to="/calculate"
            className="inline-block px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Calculate Now
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Full Optimization</h2>
          <p className="text-gray-600 mb-4">
            Generate optimized floor plans with AI-powered room placement, walls, doors, and fixtures.
          </p>
          <Link
            to="/optimize"
            className="inline-block px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Optimize Now
          </Link>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">How It Works</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Input Land Dimensions</h3>
              <p className="text-gray-600">Enter length, width, and room requirements</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Calculate Buildable Area</h3>
              <p className="text-gray-600">
                System applies Sri Lankan building codes (setbacks: Front 3m, Rear 1.5m, Sides 1.5m)
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Intelligent Room Optimization</h3>
              <p className="text-gray-600">
                AI adjusts room count if space is insufficient (reduces bedrooms, then dining, then living)
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
              4
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Generate Floor Plan</h3>
              <p className="text-gray-600">
                Genetic algorithm optimizes room placement, generates walls, doors, windows, and fixtures
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Features */}
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start gap-3">
            <span className="text-green-500 text-xl">✓</span>
            <div>
              <h4 className="font-medium text-gray-900">Sri Lankan Building Codes</h4>
              <p className="text-sm text-gray-600">Compliant setbacks and regulations</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-green-500 text-xl">✓</span>
            <div>
              <h4 className="font-medium text-gray-900">Intelligent Optimization</h4>
              <p className="text-sm text-gray-600">Automatic room reduction when needed</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-green-500 text-xl">✓</span>
            <div>
              <h4 className="font-medium text-gray-900">Genetic Algorithm</h4>
              <p className="text-sm text-gray-600">AI-powered optimal room placement</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-green-500 text-xl">✓</span>
            <div>
              <h4 className="font-medium text-gray-900">Professional Visualizations</h4>
              <p className="text-sm text-gray-600">Land plot + detailed floor plan</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-green-500 text-xl">✓</span>
            <div>
              <h4 className="font-medium text-gray-900">Architectural Elements</h4>
              <p className="text-sm text-gray-600">Walls, doors, windows, fixtures</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-green-500 text-xl">✓</span>
            <div>
              <h4 className="font-medium text-gray-900">8 Sample Scenarios</h4>
              <p className="text-sm text-gray-600">Tiny to luxury plot sizes</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sample Data Info */}
      <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
        <h2 className="text-xl font-bold text-blue-900 mb-3">Sample Data Available</h2>
        <p className="text-blue-800 mb-4">
          Test the system with 8 pre-configured land sizes from tiny (10m×8m) to luxury (30m×25m).
          Select from the dropdown in the input form.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
          <div className="text-blue-900">• Tiny (10m×8m)</div>
          <div className="text-blue-900">• Small (15m×12m)</div>
          <div className="text-blue-900">• Medium (20m×15m)</div>
          <div className="text-blue-900">• Large (25m×20m)</div>
          <div className="text-blue-900">• Luxury (30m×25m)</div>
          <div className="text-blue-900">• Narrow (25m×10m)</div>
          <div className="text-blue-900">• Wide (15m×20m)</div>
          <div className="text-blue-900">• Square (18m×18m)</div>
        </div>
      </div>
    </div>
  );
}
