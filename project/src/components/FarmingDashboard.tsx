import React from 'react';
import { TrendingUp, Droplets, Gauge, Sprout, Shield } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import { getTranslation } from '../utils/translations';

const FarmingDashboard: React.FC = () => {
  const { dashboardData, language } = useAppContext();

  // Check if data has been initialized (non-zero values or custom fertilizer message)
  const hasUserData = dashboardData.yieldPrediction > 0 || 
    dashboardData.successRate > 0 || 
    !dashboardData.fertilizerRecommendation.includes('Chat with AI');

  const metrics = [
    {
      key: 'yieldPrediction',
      label: getTranslation(language, 'yieldPrediction'),
      value: hasUserData ? `${dashboardData.yieldPrediction}t` : '--',
      suffix: hasUserData ? getTranslation(language, 'perAcre') : 'Pending data',
      icon: TrendingUp,
      color: 'from-green-500 to-green-600',
      bg: 'bg-green-50'
    },
    {
      key: 'successRate',
      label: getTranslation(language, 'successRate'),
      value: hasUserData ? `${dashboardData.successRate}%` : '--',
      suffix: hasUserData ? '' : 'Pending data',
      icon: Gauge,
      color: 'from-blue-500 to-blue-600',
      bg: 'bg-blue-50'
    },
    {
      key: 'waterRequirement',
      label: getTranslation(language, 'waterRequirement'),
      value: hasUserData ? dashboardData.waterRequirement.toString() : '--',
      suffix: hasUserData ? getTranslation(language, 'litersPerDay') : 'Pending data',
      icon: Droplets,
      color: 'from-cyan-500 to-cyan-600',
      bg: 'bg-cyan-50'
    },
    {
      key: 'irrigationPercentage',
      label: getTranslation(language, 'irrigationPercentage'),
      value: hasUserData ? `${dashboardData.irrigationPercentage}%` : '--',
      suffix: hasUserData ? '' : 'Pending data',
      icon: Droplets,
      color: 'from-teal-500 to-teal-600',
      bg: 'bg-teal-50'
    },
    {
      key: 'fertilizerRecommendation',
      label: getTranslation(language, 'fertilizerRecommendation'),
      value: dashboardData.fertilizerRecommendation,
      suffix: '',
      icon: Sprout,
      color: 'from-amber-500 to-amber-600',
      bg: 'bg-amber-50'
    },
    {
      key: 'pestManagementCost',
      label: getTranslation(language, 'pestManagementCost'),
      value: hasUserData ? `${getTranslation(language, 'rupees')}${dashboardData.pestManagementCost}` : '--',
      suffix: hasUserData ? '' : 'Pending data',
      icon: Shield,
      color: 'from-purple-500 to-purple-600',
      bg: 'bg-purple-50'
    }
  ];

  return (
    <div className="h-full bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 overflow-y-auto">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-green-600 to-green-500 rounded-xl">
          <TrendingUp className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">
          {getTranslation(language, 'dashboard')}
        </h2>
      </div>

      {!hasUserData && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <p className="text-sm text-blue-700 font-medium">
              Complete the chat conversation to see your personalized farming dashboard
            </p>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div
              key={metric.key}
              className={`${metric.bg} rounded-xl p-4 border border-white/40 hover:shadow-lg transition-all duration-200 group`}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-3 bg-gradient-to-br ${metric.color} rounded-lg group-hover:scale-110 transition-transform duration-200`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-600 truncate">
                    {metric.label}
                  </p>
                  <div className="flex items-baseline space-x-1">
                    <p className="text-xl font-bold text-gray-900">
                      {metric.value}
                    </p>
                    {metric.suffix && (
                      <p className="text-sm text-gray-500">
                        {metric.suffix}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FarmingDashboard;