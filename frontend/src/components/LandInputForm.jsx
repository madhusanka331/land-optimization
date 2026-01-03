import { useState } from 'react';
import { SAMPLE_LANDS, DIRECTION_OPTIONS } from '../data/sampleLands';

export default function LandInputForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    length: 20.0,
    width: 15.0,
    bedrooms: 3,
    toilets: 2,
    kitchen: 1,
    living_room: 1,
    dining_room: 1,
    front_direction: 'north',
    road_side: 'north',
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null,
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.length || formData.length <= 0) {
      newErrors.length = 'Length must be greater than 0';
    }
    if (!formData.width || formData.width <= 0) {
      newErrors.width = 'Width must be greater than 0';
    }
    if (!formData.bedrooms || formData.bedrooms < 1) {
      newErrors.bedrooms = 'At least 1 bedroom required';
    }
    if (!formData.toilets || formData.toilets < 1) {
      newErrors.toilets = 'At least 1 toilet required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const loadSample = (sampleKey) => {
    const sample = SAMPLE_LANDS[sampleKey];
    if (sample) {
      setFormData(sample.data);
      setErrors({});
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Sample Data Selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Load Sample Data
        </label>
        <select
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          onChange={(e) => loadSample(e.target.value)}
          defaultValue=""
        >
          <option value="">-- Select a sample --</option>
          {Object.entries(SAMPLE_LANDS).map(([key, sample]) => (
            <option key={key} value={key}>
              {sample.name} - {sample.expectedResult}
            </option>
          ))}
        </select>
      </div>

      {/* Land Dimensions */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-4">Land Dimensions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Length (meters)
            </label>
            <input
              type="number"
              name="length"
              value={formData.length}
              onChange={handleChange}
              step="0.1"
              min="1"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                errors.length ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.length && (
              <p className="mt-1 text-sm text-red-600">{errors.length}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Width (meters)
            </label>
            <input
              type="number"
              name="width"
              value={formData.width}
              onChange={handleChange}
              step="0.1"
              min="1"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                errors.width ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.width && (
              <p className="mt-1 text-sm text-red-600">{errors.width}</p>
            )}
          </div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          Total Area: {(formData.length * formData.width).toFixed(2)} m²
        </div>
      </div>

      {/* Room Requirements */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-4">Room Requirements</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bedrooms
            </label>
            <input
              type="number"
              name="bedrooms"
              value={formData.bedrooms}
              onChange={handleChange}
              min="1"
              max="10"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                errors.bedrooms ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.bedrooms && (
              <p className="mt-1 text-sm text-red-600">{errors.bedrooms}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Toilets
            </label>
            <input
              type="number"
              name="toilets"
              value={formData.toilets}
              onChange={handleChange}
              min="1"
              max="10"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                errors.toilets ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.toilets && (
              <p className="mt-1 text-sm text-red-600">{errors.toilets}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kitchen
            </label>
            <select
              name="kitchen"
              value={formData.kitchen}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Living Room
            </label>
            <select
              name="living_room"
              value={formData.living_room}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dining Room
            </label>
            <select
              name="dining_room"
              value={formData.dining_room}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </div>
        </div>
      </div>

      {/* Direction Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-4">Direction Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Front Direction
            </label>
            <select
              name="front_direction"
              value={formData.front_direction}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              {DIRECTION_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Road Side
            </label>
            <select
              name="road_side"
              value={formData.road_side}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              {DIRECTION_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Processing...' : 'Calculate / Optimize'}
      </button>
    </form>
  );
}
