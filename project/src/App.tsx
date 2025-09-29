import React, { useState } from 'react';
import { AppProvider, useAppContext } from './contexts/AppContext';
import LoginPage from './components/LoginPage';
import LanguageSelection from './components/LanguageSelection';
import MainPage from './components/MainPage';

const AppContent: React.FC = () => {
  const { user } = useAppContext();
  const [hasSelectedLanguage, setHasSelectedLanguage] = useState(false);

  if (!user) {
    return <LoginPage />;
  }

  if (!hasSelectedLanguage) {
    return <LanguageSelection onComplete={() => setHasSelectedLanguage(true)} />;
  }

  return <MainPage />;
};

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;