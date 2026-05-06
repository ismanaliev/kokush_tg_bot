import React, { createContext, useContext, useEffect, useState } from 'react'

const TmaContext = createContext()

export const TmaProvider = ({ children }) => {
  const [tmaInitData, setTmaInitData] = useState(null)
  const [user, setUser] = useState(null)
  const [isReady, setIsReady] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Import TMA SDK
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-web-app.js'
    script.onload = () => {
      if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp
        
        // Initialize TMA
        tg.ready()
        
        // Get init data
        const initData = tg.initData
        const initDataUnsafe = tg.initDataUnsafe
        
        setTmaInitData(initData)
        
        if (initDataUnsafe && initDataUnsafe.user) {
          setUser(initDataUnsafe.user)
          // Store in localStorage for API requests
          localStorage.setItem('tmaInitData', initData)
          localStorage.setItem('telegramUserId', initDataUnsafe.user.id)
        }
        
        setIsReady(true)
      }
    }
    script.onerror = () => {
      setError('Failed to load Telegram Web App SDK')
      setIsReady(true) // Still mark as ready to not block app
    }
    document.head.appendChild(script)
  }, [])

  const getTmaData = () => {
    return {
      initData: tmaInitData,
      user: user,
      isInTma: !!tmaInitData
    }
  }

  const expandApp = () => {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.expand()
    }
  }

  const closeApp = () => {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.close()
    }
  }

  const showAlert = (message) => {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.showAlert(message)
    } else {
      alert(message)
    }
  }

  const showConfirm = (message) => {
    if (window.Telegram && window.Telegram.WebApp) {
      return new Promise((resolve) => {
        window.Telegram.WebApp.showConfirm(message, resolve)
      })
    } else {
      return Promise.resolve(confirm(message))
    }
  }

  const value = {
    tmaInitData,
    user,
    isReady,
    error,
    getTmaData,
    expandApp,
    closeApp,
    showAlert,
    showConfirm
  }

  return <TmaContext.Provider value={value}>{children}</TmaContext.Provider>
}

export const useTma = () => {
  const context = useContext(TmaContext)
  if (!context) {
    throw new Error('useTma must be used within TmaProvider')
  }
  return context
}
