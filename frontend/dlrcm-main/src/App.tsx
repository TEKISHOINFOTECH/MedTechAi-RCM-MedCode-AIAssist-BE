import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { UploadEDI } from './pages/UploadEDI';
import { ClaimsReview } from './pages/ClaimsReview';
import { ClaimEdit } from './pages/ClaimEdit';
import { Settings } from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Header />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<UploadEDI />} />
          <Route path="/claims" element={<ClaimsReview />} />
          <Route path="/claims/:fileId" element={<ClaimsReview />} />
          <Route path="/claims/edit/:claimId" element={<ClaimEdit />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;