import { useState, useEffect } from 'react';
import { optimizationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ComparePage() {
  const [optimizations, setOptimizations] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [comparisonData, setComparisonData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOptimizations();
  }, []);

  const loadOptimizations = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await optimizationAPI.getHistory(100);
      setOptimizations(data);
    } catch (err) {
      setError(err.message || 'Failed to load optimizations');
      console.error('Error loading optimizations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOptimization = (id) => {
    setSelectedIds(prev => {
      if (prev.includes(id)) {
        return prev.filter(selectedId => selectedId !== id);
      } else if (prev.length < 4) {
        return [...prev, id];
      }
      return prev;
    });
  };

  const handleCompare = async () => {
    if (selectedIds.length < 2) {
      alert('Please select at least 2 optimizations to compare');
      return;
    }

    setComparing(true);
    setError(null);

    try {
      const detailsPromises = selectedIds.map(id =>
        optimizationAPI.getOptimizationById(id)
      );
      const details = await Promise.all(detailsPromises);
      setComparisonData(details);
    } catch (err) {
      setError(err.message || 'Failed to load comparison data');
      console.error('Error loading comparison:', err);
    } finally {
      setComparing(false);
    }
  };

  const handleClearSelection = () => {
    setSelectedIds([]);
    setComparisonData([]);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <LoadingSpinner message="Loading optimizations..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Compare Optimizations</h1>
        <p className="text-gray-600">
          Select 2-4 optimizations to compare side-by-side
        </p>
      </div>

      {/* Selection Panel */}
      {comparisonData.length === 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Select Optimizations ({selectedIds.length}/4)
            </h2>
            {selectedIds.length > 0 && (
              <div className="flex gap-2">
                <button
                  onClick={handleCompare}
                  disabled={selectedIds.length < 2}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Compare Selected ({selectedIds.length})
                </button>
                <button
                  onClick={handleClearSelection}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Clear
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border-2 border-red-500 p-4 rounded-lg mb-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {optimizations.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No saved optimizations found</p>
              <p className="text-gray-400 text-sm mt-2">
                Run optimizations with "Save to Database" enabled first
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {optimizations.map(opt => (
                <div
                  key={opt.id}
                  onClick={() => handleSelectOptimization(opt.id)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedIds.includes(opt.id)
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">
                      #{opt.id} - {opt.land_dimensions}
                    </h3>
                    {selectedIds.includes(opt.id) && (
                      <span className="text-primary-600">✓</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Fitness: {opt.fitness_score?.toFixed(1)}/100</p>
                    <p>{opt.bedrooms} BR, {opt.toilets} T</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Comparison View */}
      {comparing && <LoadingSpinner message="Loading comparison data..." />}

      {!comparing && comparisonData.length > 0 && (
        <>
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">
              Comparison Results ({comparisonData.length} optimizations)
            </h2>
            <button
              onClick={handleClearSelection}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Start New Comparison
            </button>
          </div>

          {/* Scores Comparison */}
          <div className="bg-white p-6 rounded-lg shadow-md overflow-x-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Scores Comparison</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4">Metric</th>
                  {comparisonData.map(opt => (
                    <th key={opt.id} className="text-center py-3 px-4">
                      Optimization #{opt.id}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Fitness Score</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4 font-bold text-primary-600">
                      {opt.scores.fitness.toFixed(1)}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <td className="py-3 px-4 font-medium">Efficiency</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.scores.efficiency.toFixed(1)}%
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Sunlight</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.scores.sunlight.toFixed(1)}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <td className="py-3 px-4 font-medium">Privacy</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.scores.privacy.toFixed(1)}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Compliance</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.scores.regulation_compliance.toFixed(1)}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          {/* Parameters Comparison */}
          <div className="bg-white p-6 rounded-lg shadow-md overflow-x-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Parameters Comparison</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4">Parameter</th>
                  {comparisonData.map(opt => (
                    <th key={opt.id} className="text-center py-3 px-4">
                      Optimization #{opt.id}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Land Dimensions</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.land_input.length}m × {opt.land_input.width}m
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <td className="py-3 px-4 font-medium">Total Area</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.land_input.area} m²
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Bedrooms</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.land_input.bedrooms}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <td className="py-3 px-4 font-medium">Toilets</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.land_input.toilets}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Execution Time</td>
                  {comparisonData.map(opt => (
                    <td key={opt.id} className="text-center py-3 px-4">
                      {opt.metadata.execution_time?.toFixed(2)}s
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          {/* Winner Declaration */}
          <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-bold mb-2">🏆 Best Optimization</h3>
            {(() => {
              const bestOpt = comparisonData.reduce((best, current) =>
                current.scores.fitness > best.scores.fitness ? current : best
              );
              return (
                <p className="text-lg">
                  Optimization #{bestOpt.id} with fitness score of {bestOpt.scores.fitness.toFixed(1)}/100
                </p>
              );
            })()}
          </div>
        </>
      )}

      {/* Info */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">How to Compare</h3>
        <ol className="text-sm text-blue-800 space-y-1 ml-4">
          <li>1. Select 2-4 optimizations from the list above</li>
          <li>2. Click "Compare Selected" to see side-by-side comparison</li>
          <li>3. Review scores and parameters to find the best solution</li>
          <li>4. Click "Start New Comparison" to compare different optimizations</li>
        </ol>
      </div>
    </div>
  );
}
