import { useState } from 'react';

export default function SearchFilters({ onSearch, onReset }) {
  const [filters, setFilters] = useState({
    bedrooms: '',
    minArea: '',
    maxArea: '',
    minFitness: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value === '' ? '' : parseFloat(value) || value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Filter out empty values
    const activeFilters = Object.entries(filters).reduce((acc, [key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        acc[key] = value;
      }
      return acc;
    }, {});
    onSearch(activeFilters);
  };

  const handleReset = () => {
    setFilters({
      bedrooms: '',
      minArea: '',
      maxArea: '',
      minFitness: '',
    });
    onReset();
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Search Filters</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bedrooms
          </label>
          <input
            type="number"
            name="bedrooms"
            value={filters.bedrooms}
            onChange={handleChange}
            min="0"
            max="10"
            placeholder="Any"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Area (m²)
          </label>
          <input
            type="number"
            name="minArea"
            value={filters.minArea}
            onChange={handleChange}
            min="0"
            placeholder="Any"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Area (m²)
          </label>
          <input
            type="number"
            name="maxArea"
            value={filters.maxArea}
            onChange={handleChange}
            min="0"
            placeholder="Any"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Fitness Score
          </label>
          <input
            type="number"
            name="minFitness"
            value={filters.minFitness}
            onChange={handleChange}
            min="0"
            max="100"
            step="1"
            placeholder="Any"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div className="flex gap-3 mt-4">
        <button
          type="submit"
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Apply Filters
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Reset
        </button>
      </div>
    </form>
  );
}
