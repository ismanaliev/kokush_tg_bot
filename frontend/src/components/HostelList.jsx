import React, { useState, useEffect } from 'react'
import axios from 'axios'

function HostelList() {
  const [hostels, setHostels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHostels()
  }, [])

  const fetchHostels = async () => {
    try {
      const response = await axios.get('/api/hostels')
      setHostels(response.data)
    } catch (error) {
      console.error('Error fetching hostels:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Загрузка...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8">Доступные хостелы</h2>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {hostels.map((hostel) => (
          <div key={hostel.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-semibold">{hostel.name}</h3>
              {hostel.is_partner && (
                <span className="bg-blue-500 text-white px-2 py-1 rounded text-sm">
                  Партнер
                </span>
              )}
            </div>

            <p className="text-gray-600 mb-4">{hostel.description}</p>
            <p className="text-sm text-gray-500 mb-2">{hostel.address}</p>

            <div className="flex justify-between items-center mb-4">
              <span className="text-sm">
                Доступно: {hostel.available_beds}/{hostel.total_beds}
              </span>
              {hostel.is_verified && (
                <span className="text-green-600 text-sm">✓ Верифицирован</span>
              )}
            </div>

            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors">
              Забронировать
            </button>
          </div>
        ))}
      </div>

      {hostels.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Хостелы не найдены
        </div>
      )}
    </div>
  )
}

export default HostelList