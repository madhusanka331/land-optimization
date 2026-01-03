export default function BuildableAreaResults({ results }) {
  if (!results) return null;

  const { land, setbacks, buildable_area, room_requirements, feasibility } = results;
  const willFit = feasibility?.will_fit;

  return (
    <div className="space-y-6">
      {/* Feasibility Status Banner */}
      <div className={`p-4 rounded-lg ${
        willFit
          ? 'bg-green-50 border-2 border-green-500'
          : 'bg-red-50 border-2 border-red-500'
      }`}>
        <div className="flex items-center gap-3">
          <span className="text-2xl">
            {willFit ? '✅' : '❌'}
          </span>
          <div>
            <h3 className={`font-bold text-lg ${
              willFit ? 'text-green-900' : 'text-red-900'
            }`}>
              {feasibility?.status}
            </h3>
            <p className={`text-sm ${
              willFit ? 'text-green-700' : 'text-red-700'
            }`}>
              {willFit
                ? `Extra Space: ${feasibility?.space_remaining?.toFixed(2)} m²`
                : `Shortage: ${feasibility?.space_remaining?.toFixed(2)} m²`
              }
            </p>
          </div>
        </div>
      </div>

      {/* Land Information */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="font-semibold text-lg text-gray-900 mb-4">Land Information</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Length</p>
            <p className="text-lg font-medium">{land?.length?.toFixed(1)} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Width</p>
            <p className="text-lg font-medium">{land?.width?.toFixed(1)} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Area</p>
            <p className="text-lg font-medium">{land?.total_area?.toFixed(2)} m²</p>
          </div>
        </div>
      </div>

      {/* Setbacks */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="font-semibold text-lg text-gray-900 mb-4">Mandatory Setbacks</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Front</p>
            <p className="text-lg font-medium">{setbacks?.front} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Rear</p>
            <p className="text-lg font-medium">{setbacks?.rear} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Left</p>
            <p className="text-lg font-medium">{setbacks?.left} m</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Right</p>
            <p className="text-lg font-medium">{setbacks?.right} m</p>
          </div>
        </div>
      </div>

      {/* Buildable Area */}
      <div className="bg-blue-50 p-6 rounded-lg shadow-md border-2 border-blue-200">
        <h3 className="font-semibold text-lg text-blue-900 mb-4">Buildable Area (After Setbacks)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-blue-700">Length</p>
            <p className="text-lg font-medium text-blue-900">{buildable_area?.length?.toFixed(1)} m</p>
          </div>
          <div>
            <p className="text-sm text-blue-700">Width</p>
            <p className="text-lg font-medium text-blue-900">{buildable_area?.width?.toFixed(1)} m</p>
          </div>
          <div>
            <p className="text-sm text-blue-700">Total Buildable</p>
            <p className="text-lg font-medium text-blue-900">{buildable_area?.total_sqm?.toFixed(2)} m²</p>
          </div>
          <div>
            <p className="text-sm text-blue-700">Usable (75%)</p>
            <p className="text-lg font-medium text-blue-900">{buildable_area?.usable_sqm?.toFixed(2)} m²</p>
          </div>
        </div>
      </div>

      {/* Room Requirements Comparison */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="font-semibold text-lg text-gray-900 mb-4">Room Requirements</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Requested */}
          <div className="space-y-2">
            <h4 className="font-medium text-gray-700">Requested</h4>
            <div className="space-y-1 text-sm">
              <p>Bedrooms: {room_requirements?.requested?.bedrooms}</p>
              <p>Toilets: {room_requirements?.requested?.toilets}</p>
              <p>Kitchen: {room_requirements?.requested?.kitchen ? 'Yes' : 'No'}</p>
              <p>Living Room: {room_requirements?.requested?.living_room ? 'Yes' : 'No'}</p>
              <p>Dining Room: {room_requirements?.requested?.dining_room ? 'Yes' : 'No'}</p>
            </div>
          </div>

          {/* Optimized */}
          <div className="space-y-2">
            <h4 className="font-medium text-gray-700">Optimized (System Adjusted)</h4>
            <div className="space-y-1 text-sm">
              <p className={
                room_requirements?.optimized?.bedrooms !== room_requirements?.requested?.bedrooms
                  ? 'text-orange-600 font-medium'
                  : ''
              }>
                Bedrooms: {room_requirements?.optimized?.bedrooms}
                {room_requirements?.optimized?.bedrooms !== room_requirements?.requested?.bedrooms && ' ⚠️'}
              </p>
              <p className={
                room_requirements?.optimized?.toilets !== room_requirements?.requested?.toilets
                  ? 'text-orange-600 font-medium'
                  : ''
              }>
                Toilets: {room_requirements?.optimized?.toilets}
                {room_requirements?.optimized?.toilets !== room_requirements?.requested?.toilets && ' ⚠️'}
              </p>
              <p className={
                room_requirements?.optimized?.kitchen !== room_requirements?.requested?.kitchen
                  ? 'text-orange-600 font-medium'
                  : ''
              }>
                Kitchen: {room_requirements?.optimized?.kitchen ? 'Yes' : 'No'}
                {room_requirements?.optimized?.kitchen !== room_requirements?.requested?.kitchen && ' ⚠️'}
              </p>
              <p className={
                room_requirements?.optimized?.living_room !== room_requirements?.requested?.living_room
                  ? 'text-orange-600 font-medium'
                  : ''
              }>
                Living Room: {room_requirements?.optimized?.living_room ? 'Yes' : 'No'}
                {room_requirements?.optimized?.living_room !== room_requirements?.requested?.living_room && ' ⚠️'}
              </p>
              <p className={
                room_requirements?.optimized?.dining_room !== room_requirements?.requested?.dining_room
                  ? 'text-orange-600 font-medium'
                  : ''
              }>
                Dining Room: {room_requirements?.optimized?.dining_room ? 'Yes' : 'No'}
                {room_requirements?.optimized?.dining_room !== room_requirements?.requested?.dining_room && ' ⚠️'}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 p-3 bg-gray-50 rounded">
          <p className="text-sm font-medium text-gray-700">
            Total Required Space: {room_requirements?.total_required_sqm?.toFixed(2)} m²
          </p>
        </div>
      </div>

      {/* Optimization Messages */}
      {feasibility?.messages && feasibility.messages.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="font-semibold text-lg text-gray-900 mb-4">Optimization Messages</h3>
          <div className="space-y-2">
            {feasibility.messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded text-sm ${
                  msg.includes('[OK]') || msg.includes('All requested')
                    ? 'bg-green-50 text-green-800'
                    : msg.includes('[WARNING]')
                    ? 'bg-yellow-50 text-yellow-800'
                    : msg.includes('[REDUCED]')
                    ? 'bg-orange-50 text-orange-800'
                    : msg.includes('[INFO]')
                    ? 'bg-blue-50 text-blue-800'
                    : 'bg-gray-50 text-gray-800'
                }`}
              >
                {msg}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
