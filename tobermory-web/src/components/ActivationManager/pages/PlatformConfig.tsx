import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { ArrowLeft, Save, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { platforms } from '../data/sampleData';
import { PlatformLogo } from '../PlatformLogo';

interface PlatformConfigData {
  advertiserId: string;
  seatId: string;
  apiKey: string;
  apiSecret: string;
  accessToken?: string;
  refreshToken?: string;
  customerId?: string;
  accountId?: string;
}

export function PlatformConfig() {
  const { platformId } = useParams<{ platformId: string }>();
  const navigate = useNavigate();
  const [formData, setFormData] = useState<PlatformConfigData>({
    advertiserId: '',
    seatId: '',
    apiKey: '',
    apiSecret: '',
    accessToken: '',
    refreshToken: '',
    customerId: '',
    accountId: '',
  });
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');

  const { data: platform } = useQuery({
    queryKey: ['platform', platformId],
    queryFn: () => {
      const found = platforms.find(p => p.id === platformId);
      if (!found) throw new Error('Platform not found');
      return found;
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (data: PlatformConfigData) => {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      console.log('Saving config:', data);
      return data;
    },
    onSuccess: () => {
      // In a real app, you'd show a success toast
      navigate('/platforms');
    },
  });

  const testConnection = async () => {
    setTestStatus('testing');
    try {
      // Mock connection test
      await new Promise(resolve => setTimeout(resolve, 2000));
      // Randomly succeed or fail for demo
      if (Math.random() > 0.3) {
        setTestStatus('success');
      } else {
        setTestStatus('error');
      }
    } catch {
      setTestStatus('error');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate(formData);
  };

  const handleChange = (field: keyof PlatformConfigData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  if (!platform) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Platform not found</p>
      </div>
    );
  }

  const getPlatformFields = () => {
    switch (platform.id) {
      case 'facebook':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Facebook App ID
              </label>
              <input
                type="text"
                value={formData.apiKey}
                onChange={handleChange('apiKey')}
                className="input-field"
                placeholder="Enter your Facebook App ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                App Secret
              </label>
              <input
                type="password"
                value={formData.apiSecret}
                onChange={handleChange('apiSecret')}
                className="input-field"
                placeholder="Enter your App Secret"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Access Token
              </label>
              <input
                type="password"
                value={formData.accessToken}
                onChange={handleChange('accessToken')}
                className="input-field"
                placeholder="Enter your Access Token"
              />
            </div>
          </>
        );
      case 'google':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer ID
              </label>
              <input
                type="text"
                value={formData.customerId}
                onChange={handleChange('customerId')}
                className="input-field"
                placeholder="123-456-7890"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Developer Token
              </label>
              <input
                type="password"
                value={formData.apiKey}
                onChange={handleChange('apiKey')}
                className="input-field"
                placeholder="Enter your Developer Token"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OAuth Client Secret
              </label>
              <input
                type="password"
                value={formData.apiSecret}
                onChange={handleChange('apiSecret')}
                className="input-field"
                placeholder="Enter your Client Secret"
              />
            </div>
          </>
        );
      case 'linkedin':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                LinkedIn Account ID
              </label>
              <input
                type="text"
                value={formData.accountId}
                onChange={handleChange('accountId')}
                className="input-field"
                placeholder="Enter your Account ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client ID
              </label>
              <input
                type="text"
                value={formData.apiKey}
                onChange={handleChange('apiKey')}
                className="input-field"
                placeholder="Enter your Client ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Secret
              </label>
              <input
                type="password"
                value={formData.apiSecret}
                onChange={handleChange('apiSecret')}
                className="input-field"
                placeholder="Enter your Client Secret"
              />
            </div>
          </>
        );
      case 'tiktok':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                TikTok App ID
              </label>
              <input
                type="text"
                value={formData.apiKey}
                onChange={handleChange('apiKey')}
                className="input-field"
                placeholder="Enter your App ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                App Secret
              </label>
              <input
                type="password"
                value={formData.apiSecret}
                onChange={handleChange('apiSecret')}
                className="input-field"
                placeholder="Enter your App Secret"
              />
            </div>
          </>
        );
      case 'thetradedesk':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Partner ID
              </label>
              <input
                type="text"
                value={formData.apiKey}
                onChange={handleChange('apiKey')}
                className="input-field"
                placeholder="Enter your Partner ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Authentication Token
              </label>
              <input
                type="password"
                value={formData.accessToken}
                onChange={handleChange('accessToken')}
                className="input-field"
                placeholder="Enter your Authentication Token"
              />
            </div>
          </>
        );
      case 'netflix':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Netflix Partner ID
              </label>
              <input
                type="text"
                value={formData.apiKey}
                onChange={handleChange('apiKey')}
                className="input-field"
                placeholder="Enter your Partner ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={formData.apiSecret}
                onChange={handleChange('apiSecret')}
                className="input-field"
                placeholder="Enter your API Key"
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <button
        onClick={() => navigate('/platforms')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-6 transition-colors"
      >
        <ArrowLeft size={20} />
        <span>Back to Platforms</span>
      </button>

      <div className="mb-8">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gray-100 rounded-md flex items-center justify-center">
            <PlatformLogo platform={platform.logo} className="w-12 h-12" />
          </div>
          <div>
            <h2 className="text-3xl font-semibold text-gray-800">{platform.name} Configuration</h2>
            <p className="text-gray-500 mt-1">Configure your {platform.name} integration settings</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="card">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Platform Credentials</h3>
            
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Advertiser ID
                  </label>
                  <input
                    type="text"
                    value={formData.advertiserId}
                    onChange={handleChange('advertiserId')}
                    className="input-field"
                    placeholder="Enter your Advertiser ID"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seat ID
                  </label>
                  <input
                    type="text"
                    value={formData.seatId}
                    onChange={handleChange('seatId')}
                    className="input-field"
                    placeholder="Enter your Seat ID"
                  />
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h4 className="text-lg font-medium text-gray-800 mb-4">API Configuration</h4>
                <div className="space-y-6">
                  {getPlatformFields()}
                </div>
              </div>

              <div className="flex gap-3 pt-6 border-t border-gray-200">
                <button
                  type="submit"
                  disabled={saveMutation.isPending}
                  className="btn-primary flex items-center gap-2"
                >
                  {saveMutation.isPending ? (
                    <>
                      <RefreshCw size={16} className="animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      Save Configuration
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/platforms')}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Connection Status</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status</span>
                <span className={clsx(
                  'text-sm font-medium',
                  platform.connected ? 'text-secondary-green' : 'text-secondary-red'
                )}>
                  {platform.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {platform.lastSync && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Last Sync</span>
                  <span className="text-sm text-gray-800">
                    {new Date(platform.lastSync).toLocaleString()}
                  </span>
                </div>
              )}

              <button
                onClick={testConnection}
                disabled={testStatus === 'testing'}
                className="w-full btn-secondary flex items-center justify-center gap-2 mt-4"
              >
                {testStatus === 'testing' ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    Testing Connection...
                  </>
                ) : (
                  <>
                    <RefreshCw size={16} />
                    Test Connection
                  </>
                )}
              </button>

              {testStatus === 'success' && (
                <div className="flex items-center gap-2 text-secondary-green bg-secondary-green/10 p-3 rounded-md">
                  <CheckCircle size={16} />
                  <span className="text-sm font-medium">Connection successful!</span>
                </div>
              )}

              {testStatus === 'error' && (
                <div className="flex items-center gap-2 text-secondary-red bg-secondary-red/10 p-3 rounded-md">
                  <AlertCircle size={16} />
                  <span className="text-sm font-medium">Connection failed</span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/20 rounded-md p-4">
            <h4 className="font-medium text-gray-800 mb-2">Configuration Tips</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Ensure all credentials are correct</li>
              <li>• Test connection before saving</li>
              <li>• Keep API keys secure</li>
              <li>• Update tokens regularly</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}