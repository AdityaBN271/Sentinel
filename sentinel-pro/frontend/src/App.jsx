import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Calibrate from './pages/Calibrate';
import ConfigurationLibrary from './pages/ConfigurationLibrary';
import './App.css';

function App() {
  // Simple auth check wrapper can be added here or inside components
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/calibrate" element={<Calibrate />} />
      <Route path="/library" element={<ConfigurationLibrary />} />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
