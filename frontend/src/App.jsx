import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { TmaProvider } from './context/TmaContext'
import HostelList from './components/HostelList'
import HostDashboard from './components/HostDashboard'
import SupportChat from './components/SupportChat'
import './App.css'

function App() {
  return (
    <TmaProvider>
      <Router>
        <div className="min-h-screen bg-gray-100">
          <header className="bg-blue-600 text-white p-4">
            <h1 className="text-2xl font-bold text-center">KG Hostel</h1>
          </header>

          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<HostelList />} />
              <Route path="/host-dashboard" element={<HostDashboard />} />
              <Route path="/support" element={<SupportChat />} />
            </Routes>
          </main>
        </div>
      </Router>
    </TmaProvider>
  )
}

export default App