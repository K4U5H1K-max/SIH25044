import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import HamburgerMenu from './HamburgerMenu';
import FarmingDashboard from './FarmingDashboard';
import ChatInterface from './ChatInterface';
import LanguageSelection from './LanguageSelection';

const MainPage: React.FC = () => {
  const { isMenuOpen, setIsMenuOpen } = useAppContext();
  const [showLanguageSelection, setShowLanguageSelection] = useState(false);

  if (showLanguageSelection) {
    return (
      <LanguageSelection onComplete={() => setShowLanguageSelection(false)} />
    );
  }

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      <div className="relative flex h-screen">
        {/* Hamburger Menu */}
        {isMenuOpen && (
          <HamburgerMenu
            onClose={() => setIsMenuOpen(false)}
            onChangeLanguage={() => {
              setShowLanguageSelection(true);
              setIsMenuOpen(false);
            }}
          />
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col lg:flex-row p-4 space-y-4 lg:space-y-0 lg:space-x-4">
          {/* Left Side - Chat Interface */}
          <div className="flex-1 flex flex-col">
            {/* Hamburger Menu Button */}
            <div className="flex justify-start mb-4">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-3 bg-white text-gray-700 rounded-xl hover:bg-gray-100 transition-all duration-200 shadow-lg lg:hidden xl:block"
              >
                <Menu className="w-6 h-6" />
              </button>
            </div>

            {/* Chat Interface */}
            <div className="flex-1">
              <ChatInterface />
            </div>
          </div>

          {/* Right Side - Farming Dashboard */}
          <div className="w-full lg:w-96 xl:w-80">
            <FarmingDashboard />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
