import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './styles/global.css';
import Assessment from './pages/Assessment';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Assessment />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
