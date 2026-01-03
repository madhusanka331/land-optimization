import { useState } from 'react';
import LandInputForm from '../components/LandInputForm';
import BuildableAreaResults from '../components/BuildableAreaResults';
import LoadingSpinner from '../components/LoadingSpinner';
import { optimizationAPI } from '../services/api';

export default function CalculatePage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await optimizationAPI.calculateBuildableArea(formData);
      setResults(response);
    } catch (err) {
      setError(err.message || 'Failed to calculate buildable area');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Calculate Buildable Area</h1>
        <p className="text-gray-600">
          Enter your land dimensions and room requirements to calculate buildable area and check feasibility.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Input Form */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Land Input</h2>
          <LandInputForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Right Column - Results */}
        <div>
          {loading && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <LoadingSpinner message="Calculating buildable area..." />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border-2 border-red-500 p-6 rounded-lg">
              <h3 className="font-bold text-red-900 mb-2">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {results && <BuildableAreaResults results={results} />}

          {!loading && !error && !results && (
            <div className="bg-gray-50 p-12 rounded-lg text-center">
              <p className="text-gray-500">
                Fill in the form and click "Calculate / Optimize" to see results
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">What does this do?</h3>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• Calculates total land area from dimensions</li>
          <li>• Applies mandatory setbacks (Front: 3m, Rear: 1.5m, Sides: 1.5m)</li>
          <li>• Determines buildable area (land minus setbacks)</li>
          <li>• Calculates usable area (75% of buildable for rooms)</li>
          <li>• Checks if requested rooms will fit</li>
          <li>• Intelligently reduces rooms if space is insufficient</li>
          <li>• Shows exact space remaining or shortage</li>
        </ul>
      </div>
    </div>
  );
}
