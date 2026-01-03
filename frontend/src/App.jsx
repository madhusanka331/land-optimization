import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import CalculatePage from './pages/CalculatePage';
import OptimizePage from './pages/OptimizePage';
import HistoryPage from './pages/HistoryPage';
import OptimizationDetailPage from './pages/OptimizationDetailPage';
import BestOptimizationsPage from './pages/BestOptimizationsPage';
import ComparePage from './pages/ComparePage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/calculate" element={<CalculatePage />} />
          <Route path="/optimize" element={<OptimizePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/history/:id" element={<OptimizationDetailPage />} />
          <Route path="/best" element={<BestOptimizationsPage />} />
          <Route path="/compare" element={<ComparePage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
