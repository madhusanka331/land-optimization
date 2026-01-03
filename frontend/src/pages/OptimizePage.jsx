import { useState } from 'react';
import LandInputForm from '../components/LandInputForm';
import BuildableAreaResults from '../components/BuildableAreaResults';
import VisualizationDisplay from '../components/VisualizationDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import { optimizationAPI } from '../services/api';

export default function OptimizePage() {
  const [loading, setLoading] = useState(false);
  const [buildableResults, setBuildableResults] = useState(null);
  const [visualizations, setVisualizations] = useState(null);
  const [error, setError] = useState(null);
  const [saveToDb, setSaveToDb] = useState(true); // Enable by default
  const [validationResult, setValidationResult] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setBuildableResults(null);
    setVisualizations(null);
    setValidationResult(null);

    try {
      // Step 0: Validate input first
      const validation = await optimizationAPI.validateLandInput(formData);
      setValidationResult(validation);

      if (!validation.valid) {
        setError('Validation failed: ' + validation.errors.join(', '));
        setLoading(false);
        return;
      }

      // Step 1: Calculate buildable area
      const buildableResponse = await optimizationAPI.calculateBuildableArea(formData);
      setBuildableResults(buildableResponse);

      // Step 2: Run full optimization if rooms will fit
      if (buildableResponse.feasibility?.will_fit) {
        const optimizationResponse = await optimizationAPI.runOptimization(formData, saveToDb);

        // Set visualization URLs
        setVisualizations({
          landPlotUrl: optimizationResponse.land_plot_url,
          floorPlanUrl: optimizationResponse.floor_plan_url,
          executionTime: optimizationResponse.execution_time_seconds,
          fitnessScore: optimizationResponse.layout?.fitness_score,
          warnings: optimizationResponse.warnings,
        });
      }
    } catch (err) {
      setError(err.message || 'Failed to run optimization');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Full Optimization</h1>
        <p className="text-gray-600">
          Generate optimized floor plans with AI-powered room placement, architectural elements, and professional visualizations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Input Form */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-lg shadow-md sticky top-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Land Input</h2>

            {/* Save to Database Toggle */}
            <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={saveToDb}
                  onChange={(e) => setSaveToDb(e.target.checked)}
                  className="w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                />
                <div>
                  <p className="font-medium text-gray-900">Save to Database</p>
                  <p className="text-xs text-gray-600">
                    Save this optimization for history, comparison, and leaderboard
                  </p>
                </div>
              </label>
            </div>

            <LandInputForm onSubmit={handleSubmit} loading={loading} />
          </div>
        </div>

        {/* Right Column - Results */}
        <div className="lg:col-span-2 space-y-8">
          {loading && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <LoadingSpinner message="Running optimization... This may take 10-30 seconds..." />
              <div className="mt-4 text-center text-sm text-gray-600">
                <p>Step 0: Validating input parameters...</p>
                <p>Step 1: Calculating buildable area...</p>
                <p>Step 2: Running genetic algorithm optimization...</p>
                <p>Step 3: Generating architectural layout...</p>
                <p>Step 4: Creating visualizations...</p>
                {saveToDb && <p className="text-primary-600 font-medium">Step 5: Saving to database...</p>}
              </div>
            </div>
          )}

          {/* Validation Warnings */}
          {validationResult && validationResult.warnings && validationResult.warnings.length > 0 && (
            <div className="bg-yellow-50 border-2 border-yellow-500 p-6 rounded-lg">
              <h3 className="font-bold text-yellow-900 mb-2">Validation Warnings</h3>
              <ul className="space-y-1">
                {validationResult.warnings.map((warning, index) => (
                  <li key={index} className="text-yellow-700 text-sm">⚠️ {warning}</li>
                ))}
              </ul>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border-2 border-red-500 p-6 rounded-lg">
              <h3 className="font-bold text-red-900 mb-2">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {buildableResults && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Buildable Area Analysis</h2>
              <BuildableAreaResults results={buildableResults} />
            </div>
          )}

          {visualizations && (
            <div>
              <VisualizationDisplay
                landPlotUrl={visualizations.landPlotUrl}
                floorPlanUrl={visualizations.floorPlanUrl}
              />

              {/* Optimization Stats */}
              <div className="bg-white p-6 rounded-lg shadow-md mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Execution Time</p>
                    <p className="text-lg font-medium">
                      {visualizations.executionTime?.toFixed(2)} seconds
                    </p>
                  </div>
                  {visualizations.fitnessScore && (
                    <div>
                      <p className="text-sm text-gray-600">Fitness Score</p>
                      <p className="text-lg font-medium">
                        {visualizations.fitnessScore?.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>

                {visualizations.warnings && visualizations.warnings.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Warnings:</p>
                    <div className="space-y-1">
                      {visualizations.warnings.map((warning, index) => (
                        <p key={index} className="text-sm text-orange-600">
                          ⚠️ {warning}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {buildableResults && !buildableResults.feasibility?.will_fit && (
            <div className="bg-yellow-50 border-2 border-yellow-500 p-6 rounded-lg">
              <h3 className="font-bold text-yellow-900 mb-2">Cannot Generate Floor Plan</h3>
              <p className="text-yellow-800">
                The land is too small to fit the requested rooms even after optimization.
                Floor plan generation has been skipped.
              </p>
              <p className="text-sm text-yellow-700 mt-2">
                Try increasing land size or reducing room requirements.
              </p>
            </div>
          )}

          {!loading && !error && !buildableResults && (
            <div className="bg-gray-50 p-12 rounded-lg text-center">
              <p className="text-gray-500">
                Fill in the form and click "Calculate / Optimize" to start optimization
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">What does full optimization do?</h3>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• Calculates buildable area and validates feasibility</li>
          <li>• Runs genetic algorithm to find optimal room placement</li>
          <li>• Generates building perimeter walls and interior walls</li>
          <li>• Creates corridors for room connectivity</li>
          <li>• Places doors with swing arcs</li>
          <li>• Adds windows for natural light</li>
          <li>• Includes fixtures (toilet, sink, bed, stove, etc.)</li>
          <li>• Produces TWO outputs: Land plot + Detailed floor plan</li>
        </ul>
      </div>
    </div>
  );
}
