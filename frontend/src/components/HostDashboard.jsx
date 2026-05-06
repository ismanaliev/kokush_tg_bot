import React, { useState, useEffect } from 'react'
import axios from 'axios'

function HostDashboard() {
  const [beds, setBeds] = useState([])
  const [hostelId, setHostelId] = useState(1) // In real app, get from user context
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchBeds()
  }, [])

  const fetchBeds = async () => {
    // In real app, fetch current beds for the hostel
    // For now, show sample data
    setBeds([
      { id: 1, bed_type: 'Одноместная', available_count: 5, total_count: 10, price_per_night: 500 },
      { id: 2, bed_type: 'Двуместная', available_count: 2, total_count: 5, price_per_night: 800 }
    ])
  }

  const updateBedCount = async (bedId, change) => {
    const updatedBeds = beds.map(bed => {
      if (bed.id === bedId) {
        const newCount = Math.max(0, Math.min(bed.total_count, bed.available_count + change))
        return { ...bed, available_count: newCount }
      }
      return bed
    })
    setBeds(updatedBeds)

    // Save to backend
    setLoading(true)
    try {
      await axios.put(`/api/hostels/${hostelId}/beds`, updatedBeds)
    } catch (error) {
      console.error('Error updating beds:', error)
      // Revert on error
      fetchBeds()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8">Управление хостелом</h2>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Количество кроватей</h3>

        {beds.map((bed) => (
          <div key={bed.id} className="flex items-center justify-between py-4 border-b border-gray-200 last:border-b-0">
            <div>
              <h4 className="font-medium">{bed.bed_type}</h4>
              <p className="text-sm text-gray-600">
                Доступно: {bed.available_count}/{bed.total_count} • Цена: {bed.price_per_night} сом/ночь
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => updateBedCount(bed.id, -1)}
                disabled={loading || bed.available_count <= 0}
                className="bg-red-500 text-white w-12 h-12 rounded-full text-2xl font-bold hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
              >
                -1
              </button>

              <span className="text-2xl font-bold w-8 text-center">
                {bed.available_count}
              </span>

              <button
                onClick={() => updateBedCount(bed.id, 1)}
                disabled={loading || bed.available_count >= bed.total_count}
                className="bg-green-500 text-white w-12 h-12 rounded-full text-2xl font-bold hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
              >
                +1
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4">Верификация хостела</h3>

        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
            <p className="text-gray-600 mb-2">Фото туалета</p>
            <input
              type="file"
              accept="image/*"
              className="w-full"
            />
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
            <p className="text-gray-600 mb-2">Фото кухни</p>
            <input
              type="file"
              accept="image/*"
              className="w-full"
            />
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
            <p className="text-gray-600 mb-2">Фото спальной зоны</p>
            <input
              type="file"
              accept="image/*"
              className="w-full"
            />
          </div>

          <button className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors text-lg font-semibold">
            Отправить на верификацию
          </button>
        </div>
      </div>
    </div>
  )
}

export default HostDashboard