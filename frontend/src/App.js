import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import ManualPrediction from './components/Prediction/ManualPrediction';
import ExcelUpload from './components/Prediction/ExcelUpload';
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
          <Route path="/predict/manual" element={<ManualPrediction />} />
          <Route path="/predict/excel" element={<ExcelUpload />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
