import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, Users, DollarSign, MousePointer } from 'lucide-react';
import { analyticsData, audiences, platforms } from '../data/sampleData';

export function Analytics() {
  const [selectedAudience, setSelectedAudience] = useState<string>('1');
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('7d');

  const { data: performanceData } = useQuery({
    queryKey: ['analytics', selectedAudience, dateRange],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const filteredData = analyticsData.filter(d => d.audienceId === selectedAudience);
      
      const dailyData = filteredData.map(d => ({
        date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        impressions: d.impressions,
        clicks: d.clicks,
        conversions: d.conversions,
        spend: d.spend,
        ctr: ((d.clicks / d.impressions) * 100).toFixed(2),
        conversionRate: ((d.conversions / d.clicks) * 100).toFixed(2),
      }));

      const totalImpressions = filteredData.reduce((sum, d) => sum + d.impressions, 0);
      const totalClicks = filteredData.reduce((sum, d) => sum + d.clicks, 0);
      const totalConversions = filteredData.reduce((sum, d) => sum + d.conversions, 0);
      const totalSpend = filteredData.reduce((sum, d) => sum + d.spend, 0);

      const platformData = platforms.map(platform => {
        const platformAnalytics = filteredData.filter(d => d.platformId === platform.id);
        const impressions = platformAnalytics.reduce((sum, d) => sum + d.impressions, 0);
        const spend = platformAnalytics.reduce((sum, d) => sum + d.spend, 0);
        return {
          name: platform.name,
          impressions,
          spend,
          cpm: impressions > 0 ? ((spend / impressions) * 1000).toFixed(2) : '0',
        };
      }).filter(p => p.impressions > 0);

      return {
        dailyData,
        summary: {
          totalImpressions,
          totalClicks,
          totalConversions,
          totalSpend,
          avgCtr: totalImpressions > 0 ? ((totalClicks / totalImpressions) * 100).toFixed(2) : '0',
          avgConversionRate: totalClicks > 0 ? ((totalConversions / totalClicks) * 100).toFixed(2) : '0',
          costPerConversion: totalConversions > 0 ? (totalSpend / totalConversions).toFixed(2) : '0',
        },
        platformData,
      };
    },
  });

  const summaryCards = [
    {
      title: 'Total Impressions',
      value: performanceData?.summary.totalImpressions.toLocaleString() || '0',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Click-Through Rate',
      value: `${performanceData?.summary.avgCtr || '0'}%`,
      icon: MousePointer,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Total Conversions',
      value: performanceData?.summary.totalConversions.toLocaleString() || '0',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Total Spend',
      value: `$${performanceData?.summary.totalSpend.toLocaleString() || '0'}`,
      icon: DollarSign,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
  ];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Analytics</h2>

      <div className="mb-6 flex flex-wrap gap-4">
        <select
          value={selectedAudience}
          onChange={(e) => setSelectedAudience(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {audiences.map((audience) => (
            <option key={audience.id} value={audience.id}>
              {audience.name}
            </option>
          ))}
        </select>

        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setDateRange(range)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                dateRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Last {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {summaryCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.title} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{card.title}</p>
                <div className={`${card.bgColor} p-2 rounded-lg`}>
                  <Icon className={card.color} size={20} />
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData?.dailyData || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="impressions" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="clicks" stroke="#10B981" strokeWidth={2} />
              <Line type="monotone" dataKey="conversions" stroke="#F59E0B" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData?.platformData || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="impressions" fill="#3B82F6" />
              <Bar dataKey="spend" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Spend Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={performanceData?.platformData || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: $${entry.spend}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="spend"
              >
                {(performanceData?.platformData || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b">
              <span className="text-gray-600">Average CTR</span>
              <span className="font-semibold text-gray-900">
                {performanceData?.summary.avgCtr || '0'}%
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b">
              <span className="text-gray-600">Conversion Rate</span>
              <span className="font-semibold text-gray-900">
                {performanceData?.summary.avgConversionRate || '0'}%
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b">
              <span className="text-gray-600">Cost per Conversion</span>
              <span className="font-semibold text-gray-900">
                ${performanceData?.summary.costPerConversion || '0'}
              </span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-gray-600">Total Spend</span>
              <span className="font-semibold text-gray-900">
                ${performanceData?.summary.totalSpend.toLocaleString() || '0'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}