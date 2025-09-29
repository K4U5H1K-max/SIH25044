import React from 'react';

export const EnvDebugger: React.FC = () => {
  const apiBase = import.meta.env.VITE_API_BASE;
  const mode = import.meta.env.MODE;
  const isDev = import.meta.env.DEV;
  const isProd = import.meta.env.PROD;

  return (
    <div className="fixed bottom-4 right-4 bg-black bg-opacity-80 text-white p-4 rounded-lg text-xs max-w-sm">
      <h3 className="font-bold mb-2">🔧 Environment Debug</h3>
      <div className="space-y-1">
        <div><strong>VITE_API_BASE:</strong> <span className="text-yellow-300">{apiBase || 'undefined'}</span></div>
        <div><strong>MODE:</strong> <span className="text-blue-300">{mode}</span></div>
        <div><strong>DEV:</strong> <span className="text-green-300">{isDev ? 'true' : 'false'}</span></div>
        <div><strong>PROD:</strong> <span className="text-red-300">{isProd ? 'true' : 'false'}</span></div>
      </div>
    </div>
  );
};