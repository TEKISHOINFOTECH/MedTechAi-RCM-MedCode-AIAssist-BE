import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { UploadEDI } from './pages/UploadEDI';
import { ClaimsReview } from './pages/ClaimsReview';
import { Settings } from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Header />
        <div className="max-w-7xl mx-auto px-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadEDI />} />
            <Route path="/claims" element={<ClaimsReview />} />
            <Route path="/claims/:fileId" element={<ClaimsReview />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;