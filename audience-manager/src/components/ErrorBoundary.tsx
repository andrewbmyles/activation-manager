import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-lg w-full">
            <div className="flex items-center gap-3 text-red-600 mb-4">
              <AlertCircle size={24} />
              <h1 className="text-xl font-semibold">Something went wrong</h1>
            </div>
            
            <div className="space-y-4">
              <p className="text-gray-600">
                An error occurred while rendering this component. This has been logged for debugging.
              </p>
              
              {process.env.NODE_ENV === 'development' && (
                <details className="bg-gray-50 p-4 rounded-md">
                  <summary className="cursor-pointer font-medium text-gray-700">
                    Error Details (Development Only)
                  </summary>
                  <pre className="mt-2 text-xs text-gray-600 overflow-auto">
                    {this.state.error && this.state.error.toString()}
                    {this.state.errorInfo && this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
              
              <button
                onClick={() => window.location.reload()}
                className="btn-primary w-full"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}