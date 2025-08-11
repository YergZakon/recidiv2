import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PersonSearch from './pages/PersonSearch';
import PersonList from './pages/PersonList';
import TimelineMap from './pages/TimelineMap';
import RegionStatus from './pages/RegionStatus';
import Forecasting from './pages/Forecasting';

function App() {
  return (
    <div className="App">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            style: {
              background: '#059669',
            },
          },
          error: {
            style: {
              background: '#dc2626',
            },
          },
        }}
      />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="search" element={<PersonSearch />} />
          <Route path="persons" element={<PersonList />} />
          <Route path="forecasts" element={<Forecasting />} />
          <Route path="timeline-map" element={<TimelineMap />} />
          <Route path="regions" element={<RegionStatus />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;