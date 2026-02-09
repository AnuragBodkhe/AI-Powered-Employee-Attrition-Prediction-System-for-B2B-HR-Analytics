import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import Employees from './components/Employees/Employees';
import Analytics from './components/Analytics/Analytics';
import ManualPrediction from './components/Prediction/ManualPrediction';
import ExcelUpload from './components/Prediction/ExcelUpload';
import Results from './components/Results/Results';
import Reports from './components/Reports/Reports';
import Settings from './components/Settings/Settings';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/employees" element={<Employees />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/predict/manual" element={<ManualPrediction />} />
          <Route path="/predict/excel" element={<ExcelUpload />} />
          <Route path="/results" element={<Results />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
