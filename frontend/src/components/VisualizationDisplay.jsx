export default function VisualizationDisplay({ landPlotUrl, floorPlanUrl }) {
  if (!landPlotUrl && !floorPlanUrl) return null;

  const downloadImage = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-900">Generated Visualizations</h2>

      {/* OUTPUT 1: Land Plot */}
      {landPlotUrl && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              OUTPUT 1: Land Plot with Buildable Area
            </h3>
            <button
              onClick={() => downloadImage(landPlotUrl, 'land_plot.png')}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              Download Land Plot
            </button>
          </div>
          <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
            <img
              src={landPlotUrl}
              alt="Land Plot with Buildable Area"
              className="w-full h-auto"
            />
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Shows the total land with buildable area highlighted (after setbacks)
          </p>
        </div>
      )}

      {/* OUTPUT 2: Floor Plan */}
      {floorPlanUrl && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              OUTPUT 2: Optimized Floor Plan
            </h3>
            <button
              onClick={() => downloadImage(floorPlanUrl, 'floor_plan.png')}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              Download Floor Plan
            </button>
          </div>
          <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
            <img
              src={floorPlanUrl}
              alt="Optimized Floor Plan"
              className="w-full h-auto"
            />
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Complete floor plan with rooms, walls, doors, windows, and fixtures
          </p>
        </div>
      )}
    </div>
  );
}
