import React, { useState } from 'react';
import { Check, X, AlertCircle } from 'lucide-react';

interface TestItem {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'pass' | 'fail';
  notes?: string;
}

export function TestChecklist() {
  const [tests, setTests] = useState<TestItem[]>([
    {
      id: '1',
      name: 'Navigation',
      description: 'All sidebar navigation links work correctly',
      status: 'pending'
    },
    {
      id: '2',
      name: 'Platform Logos',
      description: 'All platform logos render (Meta, Google, LinkedIn, TikTok, Netflix, Trade Desk)',
      status: 'pending'
    },
    {
      id: '3',
      name: 'User Profile',
      description: 'Andrew Myles name and headshot display correctly',
      status: 'pending'
    },
    {
      id: '4',
      name: 'Dashboard Links',
      description: 'Platform cards and footer links are clickable',
      status: 'pending'
    },
    {
      id: '5',
      name: 'Audience Builder',
      description: 'Variable selector works with search and categories',
      status: 'pending'
    },
    {
      id: '6',
      name: 'Platform Config',
      description: 'Gear icon navigates to configuration page',
      status: 'pending'
    },
    {
      id: '7',
      name: 'Distribution Center',
      description: 'Can select audiences and platforms',
      status: 'pending'
    },
    {
      id: '8',
      name: 'Analytics Charts',
      description: 'Recharts render without errors',
      status: 'pending'
    },
    {
      id: '9',
      name: 'Responsive Design',
      description: 'Layout works on different screen sizes',
      status: 'pending'
    },
    {
      id: '10',
      name: 'Form Validation',
      description: 'Forms show proper validation messages',
      status: 'pending'
    }
  ]);

  const updateTest = (id: string, status: 'pass' | 'fail', notes?: string) => {
    setTests(tests.map(test => 
      test.id === id ? { ...test, status, notes } : test
    ));
  };

  const allPassed = tests.every(test => test.status === 'pass');
  const failedCount = tests.filter(test => test.status === 'fail').length;

  return (
    <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-md z-50">
      <h3 className="font-semibold text-gray-800 mb-3">Demo Test Checklist</h3>
      
      <div className="space-y-2 max-h-96 overflow-y-auto mb-3">
        {tests.map(test => (
          <div key={test.id} className="flex items-start gap-3">
            <div className="flex gap-1 mt-1">
              <button
                onClick={() => updateTest(test.id, 'pass')}
                className={`p-1 rounded ${test.status === 'pass' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}
              >
                <Check size={16} />
              </button>
              <button
                onClick={() => updateTest(test.id, 'fail', 'Issue found')}
                className={`p-1 rounded ${test.status === 'fail' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-400'}`}
              >
                <X size={16} />
              </button>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700">{test.name}</p>
              <p className="text-xs text-gray-500">{test.description}</p>
              {test.notes && (
                <p className="text-xs text-red-600 mt-1">{test.notes}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t pt-3">
        {allPassed ? (
          <div className="flex items-center gap-2 text-green-600">
            <Check size={20} />
            <span className="font-medium">All tests passed! Ready to build.</span>
          </div>
        ) : failedCount > 0 ? (
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle size={20} />
            <span className="font-medium">{failedCount} test(s) failed</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-gray-500">
            <AlertCircle size={20} />
            <span className="font-medium">Complete all tests</span>
          </div>
        )}
      </div>
    </div>
  );
}