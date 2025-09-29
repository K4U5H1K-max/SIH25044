import React from 'react';
import { LogOut, Globe } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import { Language } from '../types';

const LanguageSelection: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const { language, setLanguage, setUser } = useAppContext();

  const languages = [
    { code: 'en' as Language, name: 'English', nativeName: 'English' },
    { code: 'hi' as Language, name: 'Hindi', nativeName: 'हिन्दी' },
    { code: 'ta' as Language, name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'te' as Language, name: 'Telugu', nativeName: 'తెలుగు' },
    { code: 'kn' as Language, name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
    { code: 'od' as Language, name: 'Odia', nativeName: 'ଓଡ଼ିଆ' }
  ];

  const handleLanguageSelect = (langCode: Language) => {
    setLanguage(langCode);
    onComplete();
  };

  const handleSignOut = () => {
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 relative overflow-hidden">
      {/* Animated Wheat Field Background */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `url('https://img.freepik.com/premium-photo/green-farm-field-evening-sunset_1127-21666.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      />
      
      {/* Animated overlay for wheat swaying effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-amber-500/50 to-green-600/10 animate-pulse" />
      
      {/* Sign Out Button */}
      <div className="absolute top-4 left-4 z-10">
        <button
          onClick={handleSignOut}
          className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm text-gray-700 px-4 py-2 rounded-xl hover:bg-white/90 transition-all duration-200 shadow-lg"
        >
          <LogOut className="w-4 h-4" />
          <span className="text-sm font-medium">Sign Out</span>
        </button>
      </div>

      <div className="relative flex items-center justify-center min-h-screen p-4">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-amber-500 to-amber-600 rounded-3xl mb-6 shadow-2xl">
              <Globe className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Select Your Language
            </h1>
            <p className="text-xl text-gray-600 max-w-md mx-auto">
              Choose your preferred language to continue with your agricultural assistant
            </p>
          </div>

          {/* Language Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageSelect(lang.code)}
                className={`
                  group relative bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-white/20 
                  hover:shadow-2xl hover:scale-105 transition-all duration-300 transform
                  ${language === lang.code ? 'ring-4 ring-green-500 bg-green-50/80' : ''}
                `}
              >
                <div className="text-center">
                  <div className="text-3xl mb-3 font-bold text-gray-800">
                    {lang.nativeName}
                  </div>
                  <div className="text-sm text-gray-600 font-medium">
                    {lang.name}
                  </div>
                </div>
                
                {/* Hover effect overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-amber-500/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </button>
            ))}
          </div>

          {/* Continue Button */}
          <div className="text-center mt-12">
            <button
              onClick={onComplete}
              disabled={!language}
              className="px-8 py-4 bg-gradient-to-r from-green-600 to-green-500 text-white font-semibold rounded-2xl shadow-lg hover:from-green-700 hover:to-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
            >
              Continue to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageSelection;