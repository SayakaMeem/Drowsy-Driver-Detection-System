'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Settings() {
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendAndLoadModels();
  }, []);

  const checkBackendAndLoadModels = async () => {
    setLoading(true);
    setError('');
    
    try {
      // First check if backend is running
      const healthResponse = await fetch('http://localhost:5000/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (healthResponse.ok) {
        setBackendStatus('connected');
        await loadAvailableModels();
      } else {
        setBackendStatus('error');
        setError('Backend server is not responding properly');
      }
    } catch (error) {
      console.error('Backend connection error:', error);
      setBackendStatus('error');
      setError('Cannot connect to backend server. Please ensure the Python backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableModels = async () => {
    try {
      const response = await fetch('http://localhost:5000/models');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setModels(data.models || []);
      setCurrentModel(data.current_model);
      
      if (data.models && data.models.length === 0) {
        setError('No models found in backend directory. Please add .keras or .h5 model files to the backend folder.');
      }
    } catch (error) {
      console.error('Error loading models:', error);
      setError('Error loading models: ' + error.message);
    }
  };

  const changeModel = async (modelPath) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/load-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_path: modelPath })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setCurrentModel(modelPath);
        setError(''); // Clear any previous errors
        // Show success message temporarily
        setTimeout(() => {
          setError('');
        }, 3000);
      } else {
        setError('Error changing model: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      setError('Error changing model: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const retryConnection = () => {
    checkBackendAndLoadModels();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header with Back button and Settings title */}
      <div className="flex items-center justify-between mb-8">
        <Link 
          href="/" 
          className="inline-flex items-center px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </Link>
        
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        
        {/* Empty div to maintain spacing */}
        <div className="w-32"></div>
      </div>
      
      {/* Backend Status */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Backend Status</h2>
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            backendStatus === 'connected' ? 'bg-green-500' : 
            backendStatus === 'checking' ? 'bg-yellow-500' : 'bg-red-500'
          }`}></div>
          <span className="text-gray-700">
            {backendStatus === 'connected' ? 'Connected to Python Backend' :
             backendStatus === 'checking' ? 'Checking connection...' : 'Backend not available'}
          </span>
          {backendStatus === 'error' && (
            <button
              onClick={retryConnection}
              className="ml-4 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
            >
              Retry
            </button>
          )}
        </div>
      </div>
      
      {/* Model Selection Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Model Selection</h2>
        
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading models...</p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        {!loading && !error && models.length > 0 && (
          <div className="space-y-3">
            {models.map((model, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-800">{model.name}</h3>
                  <p className="text-sm text-gray-500">
                    Size: {formatFileSize(model.size)} | Path: {model.path}
                  </p>
                  {currentModel === model.path && (
                    <span className="inline-block mt-1 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                      Currently Active
                    </span>
                  )}
                </div>
                <button
                  onClick={() => changeModel(model.path)}
                  disabled={loading || currentModel === model.path}
                  className={`px-4 py-2 rounded-lg text-sm font-medium ${
                    currentModel === model.path
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {loading ? 'Loading...' : currentModel === model.path ? 'Active' : 'Select'}
                </button>
              </div>
            ))}
          </div>
        )}
        
        {!loading && !error && models.length === 0 && (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-2 text-gray-500">No models found in backend directory</p>
            <p className="text-sm text-gray-400">Please add .keras or .h5 model files to the backend folder</p>
          </div>
        )}
      </div>
      
      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-blue-800 mb-2">How to Start the Backend</h3>
        <div className="text-blue-700 text-sm space-y-1">
          <p>1. Open a terminal in your project directory</p>
          <p>2. Run: <code className="bg-blue-100 px-1 rounded">python start_backend.py</code></p>
          <p>3. Or run: <code className="bg-blue-100 px-1 rounded">python backend/ml_server.py</code></p>
          <p>4. The backend should start on <code className="bg-blue-100 px-1 rounded">http://localhost:5000</code></p>
        </div>
      </div>
    </div>
  );
} 