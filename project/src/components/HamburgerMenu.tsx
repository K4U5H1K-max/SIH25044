import React from 'react';
import { X, ImageIcon, Globe, LogOut } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import { getTranslation } from '../utils/translations';
import GalleryModal from './GalleryModal';

interface HamburgerMenuProps {
  onClose: () => void;
  onChangeLanguage: () => void;
}

const HamburgerMenu: React.FC<HamburgerMenuProps> = ({ onClose, onChangeLanguage }) => {
  const { language, setUser } = useAppContext();
  const [showGallery, setShowGallery] = React.useState(false);

  const handleSignOut = () => {
    setUser(null);
    onClose();
  };

  const handleGallery = () => {
    setShowGallery(true);
  };

  return (
    <>
      <div className="fixed inset-0 z-50 lg:relative lg:inset-auto">
      {/* Backdrop for mobile */}
      <div 
        className="absolute inset-0 bg-black/20 lg:hidden" 
        onClick={onClose}
      />
      
      {/* Menu Panel */}
      <div className="absolute top-0 left-0 h-full w-80 bg-white/95 backdrop-blur-md shadow-2xl border-r border-white/20 lg:relative lg:w-64">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200/50">
          <h2 className="text-xl font-semibold text-gray-800">Menu</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-gray-100/80 transition-colors lg:hidden"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Menu Items */}
        <nav className="p-4 space-y-2">
          <button
            onClick={handleGallery}
            className="w-full flex items-center space-x-3 p-4 rounded-xl hover:bg-green-50/80 hover:text-green-700 transition-colors text-left group"
          >
            <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
              <ImageIcon className="w-5 h-5 text-green-600" />
            </div>
            <span className="font-medium">{getTranslation(language, 'gallery')}</span>
          </button>

          <button
            onClick={onChangeLanguage}
            className="w-full flex items-center space-x-3 p-4 rounded-xl hover:bg-blue-50/80 hover:text-blue-700 transition-colors text-left group"
          >
            <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
              <Globe className="w-5 h-5 text-blue-600" />
            </div>
            <span className="font-medium">{getTranslation(language, 'changeLanguage')}</span>
          </button>

          <button
            onClick={handleSignOut}
            className="w-full flex items-center space-x-3 p-4 rounded-xl hover:bg-red-50/80 hover:text-red-700 transition-colors text-left group"
          >
            <div className="p-2 bg-red-100 rounded-lg group-hover:bg-red-200 transition-colors">
              <LogOut className="w-5 h-5 text-red-600" />
            </div>
            <span className="font-medium">{getTranslation(language, 'signOut')}</span>
          </button>
        </nav>
      </div>
      </div>

      {/* Gallery Modal */}
      <GalleryModal 
        isOpen={showGallery}
        onClose={() => setShowGallery(false)}
      />
    </>
  );
};

export default HamburgerMenu;