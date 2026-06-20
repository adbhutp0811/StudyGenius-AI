import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()
export function useTheme() { return useContext(ThemeContext) }

export function ThemeProvider({ children }) {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  return <ThemeContext.Provider value={{ darkMode, toggleDarkMode: () => setDarkMode(p => !p) }}>{children}</ThemeContext.Provider>
}
