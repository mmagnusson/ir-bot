import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import IntakeForm from './pages/IntakeForm';
import Investigation from './pages/Investigation';
import Containment from './pages/Containment';
import Summary from './pages/Summary';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<IntakeForm />} />
        <Route path="/investigation/:incidentId" element={<Investigation />} />
        <Route path="/containment/:incidentId" element={<Containment />} />
        <Route path="/summary/:incidentId" element={<Summary />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
