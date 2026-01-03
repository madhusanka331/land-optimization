import { Link } from 'react-router-dom';

export default function OptimizationCard({ optimization, onDelete, showActions = true }) {
  const handleDelete = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (window.confirm('Are you sure you want to delete this optimization?')) {
      onDelete(optimization.id);
    }
  };

  const getFitnessColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-50';
    if (score >= 75) return 'text-blue-600 bg-blue-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Link
      to={`/history/${optimization.id}`}
      className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {optimization.land_dimensions || `${optimization.land_input?.length}×${optimization.land_input?.width}m`}
            </h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getFitnessColor(optimization.fitness_score)}`}>
              {optimization.fitness_score?.toFixed(1)} / 100
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
            <div>
              <p className="text-gray-600">Land Area</p>
              <p className="font-medium">{optimization.land_area?.toFixed(0) || optimization.land_input?.area?.toFixed(0)} m²</p>
            </div>
            <div>
              <p className="text-gray-600">Bedrooms</p>
              <p className="font-medium">{optimization.bedrooms || optimization.land_input?.bedrooms}</p>
            </div>
            <div>
              <p className="text-gray-600">Toilets</p>
              <p className="font-medium">{optimization.toilets || optimization.land_input?.toilets}</p>
            </div>
            {optimization.efficiency_score && (
              <div>
                <p className="text-gray-600">Efficiency</p>
                <p className="font-medium">{optimization.efficiency_score.toFixed(1)}%</p>
              </div>
            )}
          </div>

          <div className="mt-3 text-xs text-gray-500">
            Created: {formatDate(optimization.created_at)}
          </div>
        </div>

        {showActions && (
          <div className="ml-4 flex flex-col gap-2">
            <Link
              to={`/history/${optimization.id}`}
              className="px-3 py-1 bg-primary-600 text-white rounded text-sm hover:bg-primary-700"
              onClick={(e) => e.stopPropagation()}
            >
              View
            </Link>
            {onDelete && (
              <button
                onClick={handleDelete}
                className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
              >
                Delete
              </button>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}
