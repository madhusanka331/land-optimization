import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center">
                <span className="text-2xl font-bold text-primary-600">AI Land Optimization</span>
              </Link>
            </div>

            <div className="flex items-center space-x-2">
              <Link
                to="/"
                className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                  isActive('/')
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Home
              </Link>

              <Link
                to="/calculate"
                className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                  isActive('/calculate')
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Calculate
              </Link>

              <Link
                to="/optimize"
                className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                  isActive('/optimize')
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Optimize
              </Link>

              <Link
                to="/history"
                className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                  location.pathname.startsWith('/history')
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                History
              </Link>

              <Link
                to="/best"
                className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                  isActive('/best')
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                🏆 Best
              </Link>

              <Link
                to="/compare"
                className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                  isActive('/compare')
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Compare
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>AI Land Optimization System - Powered by Genetic Algorithms</p>
            <p className="mt-1">Backend API: http://localhost:8000</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
