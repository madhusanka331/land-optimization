import { useState, useEffect } from 'react';
import { optimizationAPI } from '../services/api';
import OptimizationCard from '../components/OptimizationCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function BestOptimizationsPage() {
  const [optimizations, setOptimizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minFitness, setMinFitness] = useState(70);
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    loadBestOptimizations();
  }, [minFitness, limit]);

  const loadBestOptimizations = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await optimizationAPI.getBestOptimizations(limit, minFitness);
      setOptimizations(data);
    } catch (err) {
      setError(err.message || 'Failed to load best optimizations');
      console.error('Error loading best optimizations:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white p-8 rounded-lg shadow-lg">
        <h1 className="text-4xl font-bold mb-2">🏆 Best Optimizations Leaderboard</h1>
        <p className="text-yellow-100 text-lg">
          Top-rated floor plan optimizations sorted by fitness score
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Leaderboard Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Minimum Fitness Score
            </label>
            <input
              type="number"
              value={minFitness}
              onChange={(e) => setMinFitness(parseFloat(e.target.value))}
              min="0"
              max="100"
              step="5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
            <p className="text-xs text-gray-500 mt-1">Show optimizations with fitness ≥ {minFitness}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number of Results
            </label>
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
              <option value={50}>Top 50</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Leaderboard ({optimizations.length} optimizations)
          </h2>
          <button
            onClick={loadBestOptimizations}
            className="px-4 py-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
          >
            Refresh
          </button>
        </div>

        {loading && <LoadingSpinner message="Loading best optimizations..." />}

        {error && (
          <div className="bg-red-50 border-2 border-red-500 p-6 rounded-lg">
            <h3 className="font-bold text-red-900 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {!loading && !error && optimizations.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg mb-4">No optimizations found</p>
            <p className="text-gray-400 text-sm">
              Try lowering the minimum fitness score or run more optimizations
            </p>
          </div>
        )}

        {!loading && !error && optimizations.length > 0 && (
          <div className="space-y-4">
            {optimizations.map((optimization, index) => (
              <div key={optimization.id} className="relative">
                {/* Rank Badge */}
                <div className="absolute -left-3 -top-3 z-10">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-lg ${
                    index === 0 ? 'bg-yellow-500' :
                    index === 1 ? 'bg-gray-400' :
                    index === 2 ? 'bg-orange-600' :
                    'bg-primary-600'
                  }`}>
                    {index === 0 ? '🥇' :
                     index === 1 ? '🥈' :
                     index === 2 ? '🥉' :
                     `#${index + 1}`
                    }
                  </div>
                </div>

                <OptimizationCard
                  optimization={optimization}
                  showActions={false}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">About the Leaderboard</h3>
        <p className="text-sm text-blue-800 mb-2">
          The leaderboard shows the best floor plan optimizations based on their fitness score.
          Fitness score combines multiple factors:
        </p>
        <ul className="text-sm text-blue-800 space-y-1 ml-4">
          <li>• Room placement efficiency</li>
          <li>• Space utilization</li>
          <li>• Sunlight exposure</li>
          <li>• Privacy levels</li>
          <li>• Building regulation compliance</li>
        </ul>
      </div>
    </div>
  );
}
