import { useState, useEffect } from 'react';
import { optimizationAPI } from '../services/api';
import OptimizationCard from '../components/OptimizationCard';
import SearchFilters from '../components/SearchFilters';
import LoadingSpinner from '../components/LoadingSpinner';

export default function HistoryPage() {
  const [optimizations, setOptimizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    setIsSearching(false);

    try {
      const data = await optimizationAPI.getHistory(50);
      setOptimizations(data);
    } catch (err) {
      setError(err.message || 'Failed to load optimization history');
      console.error('Error loading history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (filters) => {
    setLoading(true);
    setError(null);
    setIsSearching(true);

    try {
      const data = await optimizationAPI.searchOptimizations(filters);
      setOptimizations(data);
    } catch (err) {
      setError(err.message || 'Failed to search optimizations');
      console.error('Error searching:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    loadHistory();
  };

  const handleDelete = async (id) => {
    try {
      await optimizationAPI.deleteOptimization(id);
      // Remove from list
      setOptimizations(prev => prev.filter(opt => opt.id !== id));
    } catch (err) {
      alert('Failed to delete optimization: ' + err.message);
      console.error('Error deleting:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Optimization History</h1>
        <p className="text-gray-600">
          View and manage your saved optimizations. Click on any optimization to see details.
        </p>
      </div>

      {/* Search Filters */}
      <SearchFilters onSearch={handleSearch} onReset={handleReset} />

      {/* Results */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {isSearching ? 'Search Results' : 'All Optimizations'} ({optimizations.length})
          </h2>
          <button
            onClick={loadHistory}
            className="px-4 py-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
          >
            Refresh
          </button>
        </div>

        {loading && <LoadingSpinner message="Loading optimizations..." />}

        {error && (
          <div className="bg-red-50 border-2 border-red-500 p-6 rounded-lg">
            <h3 className="font-bold text-red-900 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {!loading && !error && optimizations.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg mb-4">
              {isSearching ? 'No optimizations match your search criteria' : 'No optimizations found'}
            </p>
            <p className="text-gray-400 text-sm">
              {isSearching
                ? 'Try adjusting your filters'
                : 'Run an optimization with "Save to Database" enabled to see it here'
              }
            </p>
          </div>
        )}

        {!loading && !error && optimizations.length > 0 && (
          <div className="grid grid-cols-1 gap-4">
            {optimizations.map((optimization) => (
              <OptimizationCard
                key={optimization.id}
                optimization={optimization}
                onDelete={handleDelete}
                showActions={true}
              />
            ))}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">How to Save Optimizations</h3>
        <p className="text-sm text-blue-800">
          To save optimizations to the database, enable "Save to Database" on the Optimize page.
          Saved optimizations appear here and can be viewed, searched, and compared.
        </p>
      </div>
    </div>
  );
}
