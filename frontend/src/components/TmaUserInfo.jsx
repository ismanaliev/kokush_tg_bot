import React, { useEffect, useState } from 'react'
import { useTma } from '../context/TmaContext'
import { getTmaUserInfo } from '../api/tmaApi'

export const TmaUserInfo = () => {
  const { user, isReady, getTmaData } = useTma()
  const [userInfo, setUserInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isReady && user) {
      fetchUserInfo()
    }
  }, [isReady, user])

  const fetchUserInfo = async () => {
    try {
      setLoading(true)
      setError(null)
      const info = await getTmaUserInfo()
      setUserInfo(info)
    } catch (err) {
      setError(err.message)
      console.error('Failed to fetch user info:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!isReady) {
    return <div className="text-center p-4">Loading Telegram Mini App...</div>
  }

  if (!user) {
    return <div className="text-center p-4">Please open this app from Telegram</div>
  }

  const tmaData = getTmaData()

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Welcome, {user.first_name}!</h2>
      
      <div className="bg-gray-50 p-4 rounded mb-4">
        <h3 className="font-semibold mb-2">Telegram Info:</h3>
        <p><span className="font-medium">ID:</span> {user.id}</p>
        <p><span className="font-medium">Username:</span> @{user.username || 'N/A'}</p>
        <p><span className="font-medium">Is Bot:</span> {user.is_bot ? 'Yes' : 'No'}</p>
      </div>

      {loading && <div className="text-blue-600 mb-4">Loading user data from backend...</div>}
      
      {error && <div className="text-red-600 mb-4">Error: {error}</div>}
      
      {userInfo && !loading && (
        <div className="bg-blue-50 p-4 rounded">
          <h3 className="font-semibold mb-2">Backend User Profile:</h3>
          <p><span className="font-medium">User ID:</span> {userInfo.id}</p>
          <p><span className="font-medium">Role:</span> {userInfo.role}</p>
          <p><span className="font-medium">Name:</span> {userInfo.name}</p>
          <p><span className="font-medium">Phone:</span> {userInfo.phone || 'Not set'}</p>
        </div>
      )}

      {!userInfo && !loading && !error && (
        <button
          onClick={fetchUserInfo}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Fetch User Info
        </button>
      )}
    </div>
  )
}

export default TmaUserInfo
