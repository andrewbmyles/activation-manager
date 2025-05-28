import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, Settings, Link, Unlink, CheckCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';
import { Platform } from '../types';
import { platforms as samplePlatforms } from '../data/sampleData';
import { PlatformLogo } from '../components/PlatformLogo';

export function PlatformManagement() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);

  const { data: platforms = [], isLoading } = useQuery({
    queryKey: ['platforms'],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return samplePlatforms;
    },
  });

  const connectPlatform = useMutation({
    mutationFn: async (platformId: string) => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return platformId;
    },
    onSuccess: (platformId) => {
      queryClient.setQueryData(['platforms'], (old: Platform[]) =>
        old.map(p => p.id === platformId ? { ...p, connected: true, lastSync: new Date() } : p)
      );
      setConnectingPlatform(null);
    },
  });

  const disconnectPlatform = useMutation({
    mutationFn: async (platformId: string) => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return platformId;
    },
    onSuccess: (platformId) => {
      queryClient.setQueryData(['platforms'], (old: Platform[]) =>
        old.map(p => p.id === platformId ? { ...p, connected: false, lastSync: undefined } : p)
      );
    },
  });

  const syncPlatform = useMutation({
    mutationFn: async (platformId: string) => {
      await new Promise(resolve => setTimeout(resolve, 3000));
      return platformId;
    },
    onSuccess: (platformId) => {
      queryClient.setQueryData(['platforms'], (old: Platform[]) =>
        old.map(p => p.id === platformId ? { ...p, lastSync: new Date() } : p)
      );
    },
  });

  const handleConnect = (platformId: string) => {
    setConnectingPlatform(platformId);
    connectPlatform.mutate(platformId);
  };

  const getPlatformInstructions = (platformId: string) => {
    const instructions: Record<string, string[]> = {
      facebook: [
        'Navigate to Facebook Business Manager',
        'Go to Business Settings > System Users',
        'Create new system user or select existing',
        'Generate access token with ads_management permission',
        'Copy the token and paste below',
      ],
      google: [
        'Visit Google Ads API Center',
        'Create or select a project',
        'Enable Google Ads API',
        'Create OAuth 2.0 credentials',
        'Complete authentication flow',
      ],
      linkedin: [
        'Access LinkedIn Campaign Manager',
        'Navigate to Account Assets > API Access',
        'Create new application',
        'Request Marketing Developer Platform access',
        'Configure OAuth 2.0 settings',
      ],
      tiktok: [
        'Open TikTok Ads Manager',
        'Go to Assets > Events > Web Events',
        'Create new app or select existing',
        'Generate access token',
        'Configure webhook endpoints',
      ],
    };
    return instructions[platformId] || [];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading platforms...</div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Platform Management</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {platforms.map((platform) => (
          <div key={platform.id} className="bg-white rounded-lg shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-gray-100 rounded-md flex items-center justify-center">
                    <PlatformLogo platform={platform.logo} className="w-10 h-10" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{platform.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {platform.connected ? (
                        <>
                          <CheckCircle className="text-green-500" size={16} />
                          <span className="text-sm text-green-600">Connected</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="text-gray-400" size={16} />
                          <span className="text-sm text-gray-500">Not Connected</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/platforms/${platform.id}`);
                  }}
                  className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
                >
                  <Settings size={20} />
                </button>
              </div>

              {platform.connected ? (
                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Last Sync</p>
                    <p className="font-medium text-gray-900">
                      {platform.lastSync ? new Date(platform.lastSync).toLocaleString() : 'Never'}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => syncPlatform.mutate(platform.id)}
                      disabled={syncPlatform.isPending && syncPlatform.variables === platform.id}
                      className={clsx(
                        'flex-1 flex items-center justify-center gap-2 py-2 rounded-lg font-medium transition-colors',
                        syncPlatform.isPending && syncPlatform.variables === platform.id
                          ? 'bg-gray-100 text-gray-500'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      )}
                    >
                      <RefreshCw
                        size={16}
                        className={clsx(
                          syncPlatform.isPending && syncPlatform.variables === platform.id && 'animate-spin'
                        )}
                      />
                      {syncPlatform.isPending && syncPlatform.variables === platform.id
                        ? 'Syncing...'
                        : 'Sync Now'}
                    </button>
                    <button
                      onClick={() => disconnectPlatform.mutate(platform.id)}
                      disabled={disconnectPlatform.isPending && disconnectPlatform.variables === platform.id}
                      className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-2"
                    >
                      <Unlink size={16} />
                      Disconnect
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  {connectingPlatform === platform.id ? (
                    <div className="space-y-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Connection Instructions</h4>
                        <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                          {getPlatformInstructions(platform.id).map((instruction, index) => (
                            <li key={index}>{instruction}</li>
                          ))}
                        </ol>
                      </div>

                      <div className="space-y-3">
                        <input
                          type="text"
                          placeholder="Enter API Key or Access Token"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="flex gap-3">
                          <button
                            disabled={connectPlatform.isPending}
                            className={clsx(
                              'flex-1 py-2 rounded-lg font-medium transition-colors',
                              connectPlatform.isPending
                                ? 'bg-gray-300 text-gray-500'
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                            )}
                          >
                            {connectPlatform.isPending ? 'Connecting...' : 'Complete Connection'}
                          </button>
                          <button
                            onClick={() => setConnectingPlatform(null)}
                            disabled={connectPlatform.isPending}
                            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleConnect(platform.id)}
                      className="w-full flex items-center justify-center gap-2 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
                    >
                      <Link size={16} />
                      Connect Platform
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-yellow-900 mb-2">Platform Limits & Best Practices</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• Facebook: Maximum 200,000 users per custom audience</li>
          <li>• Google: Minimum 1,000 users for Customer Match</li>
          <li>• LinkedIn: Minimum 300 matched members for targeting</li>
          <li>• TikTok: Maximum file size of 50MB for uploads</li>
        </ul>
      </div>
    </div>
  );
}