import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, CheckCircle, Clock, AlertCircle, Download, ChevronRight, Info } from 'lucide-react';
import { clsx } from 'clsx';
import { audiences, platforms, distributions as sampleDistributions } from '../data/sampleData';
import { Distribution } from '../types';
import { PlatformLogo } from '../PlatformLogo';

export function DistributionCenter() {
  const queryClient = useQueryClient();
  const [selectedAudiences, setSelectedAudiences] = useState<string[]>([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [isDistributing, setIsDistributing] = useState(false);

  const { data: distributions = [] } = useQuery({
    queryKey: ['distributions'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return sampleDistributions;
    },
  });

  const connectedPlatforms = platforms.filter(p => p.connected);

  const distributeAudiences = useMutation({
    mutationFn: async (data: { audiences: string[]; platforms: string[] }) => {
      const newDistributions: Distribution[] = [];
      for (const audienceId of data.audiences) {
        for (const platformId of data.platforms) {
          await new Promise(resolve => setTimeout(resolve, 1000));
          newDistributions.push({
            id: Date.now().toString() + Math.random(),
            audienceId,
            platformId,
            status: 'in_progress',
            startedAt: new Date(),
            recordsProcessed: 0,
          });
        }
      }
      return newDistributions;
    },
    onSuccess: (newDistributions) => {
      queryClient.setQueryData(['distributions'], (old: Distribution[]) => [...newDistributions, ...old]);
      setSelectedAudiences([]);
      setSelectedPlatforms([]);
      setIsDistributing(false);
      
      newDistributions.forEach((dist) => {
        setTimeout(() => {
          queryClient.setQueryData(['distributions'], (old: Distribution[]) =>
            old.map(d => d.id === dist.id
              ? {
                  ...d,
                  status: 'completed',
                  completedAt: new Date(),
                  recordsProcessed: audiences.find(a => a.id === dist.audienceId)?.estimatedSize || 0,
                }
              : d
            )
          );
        }, 5000 + Math.random() * 5000);
      });
    },
  });

  const handleDistribute = () => {
    if (selectedAudiences.length > 0 && selectedPlatforms.length > 0) {
      setIsDistributing(true);
      distributeAudiences.mutate({
        audiences: selectedAudiences,
        platforms: selectedPlatforms,
      });
    }
  };

  const toggleAudience = (audienceId: string) => {
    setSelectedAudiences(prev =>
      prev.includes(audienceId)
        ? prev.filter(id => id !== audienceId)
        : [...prev, audienceId]
    );
  };

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const getStatusIcon = (status: Distribution['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-secondary-green" size={20} />;
      case 'in_progress':
        return <Clock className="text-primary animate-pulse" size={20} />;
      case 'failed':
        return <AlertCircle className="text-secondary-red" size={20} />;
      default:
        return null;
    }
  };

  const getStatusText = (status: Distribution['status']) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      case 'failed':
        return 'Failed';
      default:
        return 'Pending';
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-semibold text-gray-800 mb-2">Distribution Center</h2>
        <p className="text-gray-500">Distribute audiences to your connected ad platforms</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Select Audiences</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {audiences.map((audience) => (
                <label
                  key={audience.id}
                  className={clsx(
                    'flex items-center justify-between p-4 rounded-md border cursor-pointer transition-all duration-200',
                    selectedAudiences.includes(audience.id)
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:bg-gray-50'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={selectedAudiences.includes(audience.id)}
                      onChange={() => toggleAudience(audience.id)}
                      className="w-4 h-4 text-primary rounded focus:ring-primary"
                    />
                    <div>
                      <p className="font-medium text-gray-800">{audience.name}</p>
                      <p className="text-sm text-gray-500">
                        {audience.estimatedSize.toLocaleString()} users
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="text-gray-400" size={20} />
                </label>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Select Platforms</h3>
            <div className="grid grid-cols-2 gap-4">
              {connectedPlatforms.map((platform) => (
                <label
                  key={platform.id}
                  className={clsx(
                    'flex items-center gap-3 p-4 rounded-md border cursor-pointer transition-all duration-200',
                    selectedPlatforms.includes(platform.id)
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:bg-gray-50'
                  )}
                >
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes(platform.id)}
                    onChange={() => togglePlatform(platform.id)}
                    className="w-4 h-4 text-primary rounded focus:ring-primary"
                  />
                  <PlatformLogo platform={platform.logo} className="w-6 h-6" />
                  <span className="font-medium text-gray-800">{platform.name}</span>
                </label>
              ))}
            </div>
            {connectedPlatforms.length === 0 && (
              <div className="text-center py-8">
                <Info className="text-gray-400 w-12 h-12 mx-auto mb-3" />
                <p className="text-gray-500">No connected platforms</p>
                <p className="text-sm text-gray-400 mt-1">Please connect platforms first</p>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Distribution Summary</h3>
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-md">
                <p className="text-sm text-gray-600">Selected Audiences</p>
                <p className="text-2xl font-semibold text-gray-800">{selectedAudiences.length}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-md">
                <p className="text-sm text-gray-600">Selected Platforms</p>
                <p className="text-2xl font-semibold text-gray-800">{selectedPlatforms.length}</p>
              </div>
              <div className="p-4 bg-primary/10 rounded-md">
                <p className="text-sm text-primary">Total Distributions</p>
                <p className="text-2xl font-semibold text-primary">
                  {selectedAudiences.length * selectedPlatforms.length}
                </p>
              </div>
              <button
                onClick={handleDistribute}
                disabled={selectedAudiences.length === 0 || selectedPlatforms.length === 0 || isDistributing}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Send size={20} />
                {isDistributing ? 'Distributing...' : 'Start Distribution'}
              </button>
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/20 rounded-md p-4">
            <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
              <Info size={16} className="text-primary" />
              Distribution Tips
            </h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Batch similar audiences for efficiency</li>
              <li>• Check platform limits before distributing</li>
              <li>• Monitor progress for large audiences</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="border-b border-gray-200 pb-4 mb-6">
          <h3 className="text-xl font-semibold text-gray-800">Distribution History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table-base">
            <thead>
              <tr>
                <th className="table-header px-6 py-4 text-left">Audience</th>
                <th className="table-header px-6 py-4 text-left">Platform</th>
                <th className="table-header px-6 py-4 text-left">Status</th>
                <th className="table-header px-6 py-4 text-left">Records</th>
                <th className="table-header px-6 py-4 text-left">Started</th>
                <th className="table-header px-6 py-4 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {distributions.map((distribution) => {
                const audience = audiences.find(a => a.id === distribution.audienceId);
                const platform = platforms.find(p => p.id === distribution.platformId);
                
                return (
                  <tr key={distribution.id} className="table-row">
                    <td className="px-6 py-4 text-sm font-medium text-gray-800">
                      {audience?.name}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {platform && <PlatformLogo platform={platform.logo} className="w-5 h-5" />}
                        <span className="text-sm text-gray-600">{platform?.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(distribution.status)}
                        <span className={clsx(
                          'text-sm font-medium',
                          distribution.status === 'completed' && 'text-secondary-green',
                          distribution.status === 'in_progress' && 'text-primary',
                          distribution.status === 'failed' && 'text-secondary-red'
                        )}>
                          {getStatusText(distribution.status)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {distribution.recordsProcessed?.toLocaleString() || '—'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(distribution.startedAt).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-primary hover:text-primary-hover transition-colors">
                        <Download size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}