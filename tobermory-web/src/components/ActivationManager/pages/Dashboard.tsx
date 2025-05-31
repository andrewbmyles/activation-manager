import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Monitor, TrendingUp, DollarSign, ArrowUp, ArrowDown } from 'lucide-react';
import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';
import { audiences, platforms, distributions, analyticsData } from '../data/sampleData';
import { PlatformLogo } from '../PlatformLogo';
import { AudienceIcon } from '../AudienceIcon';

export function Dashboard() {
  const navigate = useNavigate();
  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const totalAudiences = audiences.length;
      const totalReach = audiences.reduce((sum, aud) => sum + aud.estimatedSize, 0);
      const activeDistributions = distributions.filter(d => d.status === 'in_progress').length;
      const totalSpend = analyticsData.reduce((sum, data) => sum + data.spend, 0);
      
      return {
        totalAudiences,
        totalReach,
        activeDistributions,
        totalSpend,
        changes: {
          audiences: 12,
          reach: -5,
          distributions: 25,
          spend: 8,
        }
      };
    },
  });

  const statCards = [
    {
      title: 'Total Audiences',
      value: stats?.totalAudiences || 0,
      change: stats?.changes.audiences || 0,
      icon: Users,
      color: 'primary',
    },
    {
      title: 'Total Reach',
      value: (stats?.totalReach || 0).toLocaleString(),
      change: stats?.changes.reach || 0,
      icon: Monitor,
      color: 'green',
    },
    {
      title: 'Active Distributions',
      value: stats?.activeDistributions || 0,
      change: stats?.changes.distributions || 0,
      icon: TrendingUp,
      color: 'purple',
    },
    {
      title: 'Total Spend',
      value: `$${(stats?.totalSpend || 0).toLocaleString()}`,
      change: stats?.changes.spend || 0,
      icon: DollarSign,
      color: 'orange',
    },
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      primary: 'bg-primary/10 text-primary',
      green: 'bg-secondary-green/10 text-secondary-green',
      purple: 'bg-secondary-purple/10 text-secondary-purple',
      orange: 'bg-secondary-orange/10 text-secondary-orange',
    };
    return colors[color as keyof typeof colors] || colors.primary;
  };

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-semibold text-gray-800 mb-2">Dashboard</h2>
        <p className="text-gray-500">Monitor your audience distribution performance</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card) => {
          const Icon = card.icon;
          const isPositive = card.change > 0;
          return (
            <div key={card.title} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className={clsx('p-3 rounded-md', getColorClasses(card.color))}>
                  <Icon size={24} />
                </div>
                {card.change !== 0 && (
                  <div className={clsx(
                    'flex items-center gap-1 text-sm font-medium',
                    isPositive ? 'text-secondary-green' : 'text-secondary-red'
                  )}>
                    {isPositive ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                    {Math.abs(card.change)}%
                  </div>
                )}
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">{card.title}</p>
                <p className="text-2xl font-semibold text-gray-800">{card.value}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">Recent Audiences</h3>
          <div className="space-y-4">
            {audiences.slice(0, 5).map((audience) => (
              <div key={audience.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center flex-shrink-0">
                    <AudienceIcon audienceName={audience.name} className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{audience.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{audience.estimatedSize.toLocaleString()} users</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  {audience.platforms.map((platform) => {
                    const plat = platforms.find(p => p.id === platform);
                    return (
                      <div
                        key={platform}
                        className="inline-flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded-md"
                        title={plat?.name}
                      >
                        <PlatformLogo platform={plat?.logo || ''} className="w-4 h-4 flex-shrink-0" />
                        <span className="text-xs font-medium text-gray-600">{plat?.name.split(' ')[0]}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          <button 
            onClick={() => navigate('/audiences')}
            className="w-full mt-4 text-primary font-medium text-sm hover:text-primary-hover transition-colors"
          >
            View All Audiences →
          </button>
        </div>

        <div className="card">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">Platform Status</h3>
          <div className="space-y-4">
            {platforms.map((platform) => (
              <div 
                key={platform.id} 
                className="flex items-center justify-between py-3 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded-md transition-colors"
                onClick={() => navigate(`/platforms/${platform.id}`)}
              >
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-gray-100 rounded-md flex items-center justify-center p-2">
                    <PlatformLogo platform={platform.logo} className="w-full h-full object-contain" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{platform.name}</p>
                    {platform.connected && platform.lastSync && (
                      <p className="text-xs text-gray-500 mt-1">
                        Last sync: {new Date(platform.lastSync).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className={clsx(
                    'w-2 h-2 rounded-full',
                    platform.connected ? 'bg-secondary-green' : 'bg-secondary-red'
                  )} />
                  <span className={clsx(
                    'text-sm font-medium',
                    platform.connected ? 'text-secondary-green' : 'text-secondary-red'
                  )}>
                    {platform.connected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <button 
            onClick={() => navigate('/platforms')}
            className="w-full mt-4 text-primary font-medium text-sm hover:text-primary-hover transition-colors"
          >
            Manage Platforms →
          </button>
        </div>
      </div>
    </div>
  );
}