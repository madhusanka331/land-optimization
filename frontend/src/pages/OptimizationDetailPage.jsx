import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { optimizationAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function OptimizationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOptimization();
  }, [id]);

  const loadOptimization = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await optimizationAPI.getOptimizationById(id);
      setOptimization(data);
    } catch (err) {
      setError(err.message || 'Failed to load optimization details');
      console.error('Error loading optimization:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this optimization?')) {
      return;
    }

    try {
      await optimizationAPI.deleteOptimization(id);
      navigate('/history');
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <LoadingSpinner message="Loading optimization details..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-red-50 border-2 border-red-500 p-6 rounded-lg">
          <h3 className="font-bold text-red-900 mb-2">Error</h3>
          <p className="text-red-700">{error}</p>
          <Link to="/history" className="text-primary-600 hover:underline mt-4 inline-block">
            ← Back to History
          </Link>
        </div>
      </div>
    );
  }

  if (!optimization) {
    return null;
  }

  const { land_input, scores, metadata, layout_data } = optimization;

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex items-start justify-between">
          <div>
            <Link to="/history" className="text-primary-600 hover:underline text-sm mb-2 inline-block">
              ← Back to History
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Optimization #{id}
            </h1>
            <p className="text-gray-600">
              {land_input.length}m × {land_input.width}m ({land_input.area} m²)
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Scores */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Optimization Scores</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Fitness Score</p>
            <p className="text-3xl font-bold text-primary-600">{scores.fitness.toFixed(1)}</p>
            <p className="text-xs text-gray-500">/ 100</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Efficiency</p>
            <p className="text-3xl font-bold text-green-600">{scores.efficiency.toFixed(1)}</p>
            <p className="text-xs text-gray-500">%</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Sunlight</p>
            <p className="text-3xl font-bold text-yellow-600">{scores.sunlight.toFixed(1)}</p>
            <p className="text-xs text-gray-500">/ 100</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Privacy</p>
            <p className="text-3xl font-bold text-blue-600">{scores.privacy.toFixed(1)}</p>
            <p className="text-xs text-gray-500">/ 100</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Compliance</p>
            <p className="text-3xl font-bold text-purple-600">{scores.regulation_compliance.toFixed(1)}</p>
            <p className="text-xs text-gray-500">/ 100</p>
          </div>
        </div>
      </div>

      {/* Land Input */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Land Parameters</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Length</p>
            <p className="text-lg font-medium">{land_input.length} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Width</p>
            <p className="text-lg font-medium">{land_input.width} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Area</p>
            <p className="text-lg font-medium">{land_input.area} m²</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Garden Area</p>
            <p className="text-lg font-medium">{land_input.garden_area} m²</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Bedrooms</p>
            <p className="text-lg font-medium">{land_input.bedrooms}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Toilets</p>
            <p className="text-lg font-medium">{land_input.toilets}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Living Room</p>
            <p className="text-lg font-medium">{land_input.living_room ? 'Yes' : 'No'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Dining Room</p>
            <p className="text-lg font-medium">{land_input.dining_room ? 'Yes' : 'No'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Front Direction</p>
            <p className="text-lg font-medium capitalize">{land_input.front_direction}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Road Side</p>
            <p className="text-lg font-medium capitalize">{land_input.road_side}</p>
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Optimization Metadata</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Generations</p>
            <p className="text-lg font-medium">{metadata.generations}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Execution Time</p>
            <p className="text-lg font-medium">{metadata.execution_time?.toFixed(2)} seconds</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Created At</p>
            <p className="text-lg font-medium">
              {new Date(metadata.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Layout Data */}
      {layout_data && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Layout Data</h2>
          <div className="bg-gray-50 p-4 rounded overflow-x-auto">
            <pre className="text-sm text-gray-700">
              {JSON.stringify(JSON.parse(layout_data), null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
