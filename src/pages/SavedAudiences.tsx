import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Archive, Eye, RefreshCw, Download, Users, TrendingUp, Target } from 'lucide-react';
import { getAudienceIcon, getAudienceIconColor } from '../utils/audienceUtils';

export function SavedAudiences() {
  const [audiences, setAudiences] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAudiences();
  }, []);

  const fetchAudiences = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/audiences?user_id=demo_user');
      const data = await response.json();
      
      if (data.success) {
        setAudiences(data.audiences);
      } else {
        // Use mock data for demo purposes
        const mockAudiences = [
          {
            audience_id: 'demo-gaming-audience',
            name: 'Gaming Enthusiasts Q4',
            enhanced_name: 'Gaming-Enthusiast Gen Z Males',
            description: 'Find males aged 18-24 interested in gaming',
            natural_language_criteria: 'Males between ages 18-24 who are interested in video games',
            audience_size: 67842,
            original_query: 'gaming enthusiasts',
            insights: [
              'Focused audience of 68K+ targeted users',
              'Digital-native generation',
              'High engagement with gaming content'
            ],
            segments: [{segment_id: 'seg_1', name: 'Console Gamers', size: 34521}],
            created_at: new Date().toISOString()
          },
          {
            audience_id: 'demo-fashion-audience',
            name: 'Fashion Forward Millennials',
            enhanced_name: 'Fashion-Forward Millennial Women',
            description: 'Fashion-conscious millennial women with high disposable income',
            natural_language_criteria: 'Females between ages 25-40 who are interested in fashion and have high disposable income',
            audience_size: 54321,
            original_query: 'fashion-forward millennial women',
            insights: [
              'High purchasing power demographic',
              'Active on social media',
              'Brand conscious consumers'
            ],
            segments: [{segment_id: 'seg_2', name: 'Luxury Shoppers', size: 27160}],
            created_at: new Date(Date.now() - 86400000).toISOString() // Yesterday
          }
        ];
        setAudiences(mockAudiences);
      }
    } catch (error) {
      console.error('Error fetching audiences:', error);
      // Use mock data on error too
      const mockAudiences = [
        {
          audience_id: 'demo-gaming-audience',
          name: 'Gaming Enthusiasts Q4',
          enhanced_name: 'Gaming-Enthusiast Gen Z Males',
          description: 'Find males aged 18-24 interested in gaming',
          natural_language_criteria: 'Males between ages 18-24 who are interested in video games',
          audience_size: 67842,
          original_query: 'gaming enthusiasts',
          insights: [
            'Focused audience of 68K+ targeted users',
            'Digital-native generation',
            'High engagement with gaming content'
          ],
          segments: [{segment_id: 'seg_1', name: 'Console Gamers', size: 34521}],
          created_at: new Date().toISOString()
        },
        {
          audience_id: 'demo-fashion-audience',
          name: 'Fashion Forward Millennials',
          enhanced_name: 'Fashion-Forward Millennial Women',
          description: 'Fashion-conscious millennial women with high disposable income',
          natural_language_criteria: 'Females between ages 25-40 who are interested in fashion and have high disposable income',
          audience_size: 54321,
          original_query: 'fashion-forward millennial women',
          insights: [
            'High purchasing power demographic',
            'Active on social media',
            'Brand conscious consumers'
          ],
          segments: [{segment_id: 'seg_2', name: 'Luxury Shoppers', size: 27160}],
          created_at: new Date(Date.now() - 86400000).toISOString() // Yesterday
        }
      ];
      setAudiences(mockAudiences);
    } finally {
      setLoading(false);
    }
  };

  const handleViewAudience = (audienceId: string) => {
    // Navigate to audience detail view
    navigate(`/audiences/${audienceId}`);
  };

  const handleArchiveAudience = async (audienceId: string) => {
    if (!window.confirm('Are you sure you want to archive this audience?')) return;

    try {
      const response = await fetch(`/api/audiences/${audienceId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user',
          status: 'archived'
        })
      });

      if (response.ok) {
        fetchAudiences(); // Refresh list
      }
    } catch (error) {
      console.error('Error archiving audience:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-gray-500" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Saved Audiences</h1>
        <button
          onClick={() => navigate('/audiences')}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Create New Audience
        </button>
      </div>

      {audiences.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600">No saved audiences yet.</p>
          <p className="text-sm text-gray-500 mt-2">
            Create your first audience using the Natural Language Audience Builder.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {audiences.map(audience => {
            const Icon = getAudienceIcon(audience.original_query || audience.description || '');
            const iconColor = getAudienceIconColor(audience.original_query || audience.description || '');
            const displaySize = audience.audience_size || audience.total_audience_size || 0;
            
            return (
              <div key={audience.audience_id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden">
                {/* Card Header with Icon */}
                <div className="relative p-6 pb-0">
                  <div className="flex items-start justify-between mb-4">
                    <div 
                      className="w-16 h-16 rounded-full flex items-center justify-center shadow-md"
                      style={{ backgroundColor: `${iconColor}20` }}
                    >
                      <Icon size={32} style={{ color: iconColor }} />
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleViewAudience(audience.audience_id)}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                        title="View Details"
                      >
                        <Eye size={16} className="text-gray-600" />
                      </button>
                      <button
                        onClick={() => handleArchiveAudience(audience.audience_id)}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                        title="Archive"
                      >
                        <Archive size={16} className="text-gray-600" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Audience Name */}
                  <h3 className="text-xl font-bold text-gray-800 mb-2">
                    {audience.enhanced_name || audience.name}
                  </h3>
                  
                  {/* Audience Size */}
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={20} className="text-green-500" />
                    <span className="text-2xl font-semibold text-gray-700">
                      {displaySize.toLocaleString()}
                    </span>
                    <span className="text-gray-500">people</span>
                  </div>
                </div>
                
                {/* Card Body */}
                <div className="px-6 pb-6">
                  {/* Natural Language Criteria */}
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-1">Audience Criteria:</p>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      {audience.natural_language_criteria || audience.description || 'Custom audience based on selected criteria'}
                    </p>
                  </div>
                  
                  {/* Insights */}
                  {audience.insights && audience.insights.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-1">Key Insights:</p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {audience.insights.slice(0, 2).map((insight: string, index: number) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-1">•</span>
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Metadata */}
                  <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
                    <span className="flex items-center gap-1">
                      <Target size={12} />
                      {audience.segments?.length || 0} segments
                    </span>
                    <span>Created {new Date(audience.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                {/* Card Footer - Action Button */}
                <div className="px-6 pb-4">
                  <button
                    onClick={() => navigate(`/distribution?audience=${audience.audience_id}`)}
                    className="w-full py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-200 flex items-center justify-center gap-2 text-sm font-medium"
                  >
                    <Download size={16} />
                    Activate Audience
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}