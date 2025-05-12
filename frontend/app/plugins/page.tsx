'use client';

import { useState, useEffect } from 'react';
import { FaPlus, FaEdit, FaTrash, FaPuzzlePiece, FaArrowLeft } from 'react-icons/fa';
import Link from 'next/link';

type Parameter = {
  name: string;
  description: string;
  required: boolean;
  type: string;
};

type Plugin = {
  id: number;
  name: string;
  description: string;
  api_endpoint: string;
  api_key_required: boolean;
  parameters: Parameter[];
  created_at: string;
  updated_at: string | null;
};

type PluginFormData = {
  name: string;
  description: string;
  api_endpoint: string;
  api_key_required: boolean;
  parameters: Parameter[];
};

const emptyFormData: PluginFormData = {
  name: '',
  description: '',
  api_endpoint: '',
  api_key_required: false,
  parameters: [],
};

const emptyParameter: Parameter = {
  name: '',
  description: '',
  required: false,
  type: 'string',
};

export default function PluginsPage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [formData, setFormData] = useState<PluginFormData>(emptyFormData);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch plugins on component mount
  useEffect(() => {
    fetchPlugins();
  }, []);

  const fetchPlugins = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/plugins`);
      if (!response.ok) {
        throw new Error('Failed to fetch plugins');
      }
      const data = await response.json();
      setPlugins(data);
    } catch (error) {
      console.error('Error fetching plugins:', error);
      setError('Failed to load plugins. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData({ ...formData, [name]: checked });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleParameterChange = (index: number, field: keyof Parameter, value: string | boolean) => {
    const updatedParameters = [...formData.parameters];
    updatedParameters[index] = { 
      ...updatedParameters[index], 
      [field]: value 
    };
    setFormData({ ...formData, parameters: updatedParameters });
  };

  const addParameter = () => {
    setFormData({
      ...formData,
      parameters: [...formData.parameters, { ...emptyParameter }],
    });
  };

  const removeParameter = (index: number) => {
    const updatedParameters = [...formData.parameters];
    updatedParameters.splice(index, 1);
    setFormData({ ...formData, parameters: updatedParameters });
  };

  const resetForm = () => {
    setFormData(emptyFormData);
    setEditingId(null);
    setIsFormVisible(false);
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      const url = editingId 
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/plugins/${editingId}` 
        : `${process.env.NEXT_PUBLIC_API_URL}/api/plugins`;
      
      const method = editingId ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save plugin');
      }

      // Refresh plugins list
      await fetchPlugins();
      
      setSuccess(editingId ? 'Plugin updated successfully!' : 'Plugin created successfully!');
      resetForm();
    } catch (error: any) {
      console.error('Error saving plugin:', error);
      setError(error.message || 'Failed to save plugin. Please try again.');
    }
  };

  const handleEdit = (plugin: Plugin) => {
    setFormData({
      name: plugin.name,
      description: plugin.description,
      api_endpoint: plugin.api_endpoint,
      api_key_required: plugin.api_key_required,
      parameters: plugin.parameters,
    });
    setEditingId(plugin.id);
    setIsFormVisible(true);
    setError(null);
    setSuccess(null);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this plugin?')) {
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/plugins/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete plugin');
      }

      // Refresh plugins list
      await fetchPlugins();
      setSuccess('Plugin deleted successfully!');
    } catch (error) {
      console.error('Error deleting plugin:', error);
      setError('Failed to delete plugin. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-primary-600 text-white p-4">
        <div className="container mx-auto">
          <div className="flex justify-between items-center">
            <Link href="/" className="text-xl font-bold flex items-center">
              <FaPuzzlePiece className="mr-2" /> Cybersecurity AI Assistant Plugins
            </Link>
            <Link href="/chat" className="flex items-center text-white hover:text-primary-200">
              <FaArrowLeft className="mr-1" /> Back to Chat
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto py-8 px-4">
        {/* Notification Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        {/* Plugins List */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Available Plugins</h2>
            <button
              onClick={() => {
                resetForm();
                setIsFormVisible(true);
              }}
              className="bg-primary-600 text-white px-4 py-2 rounded flex items-center hover:bg-primary-700"
            >
              <FaPlus className="mr-2" /> Add New Plugin
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4">Loading plugins...</p>
            </div>
          ) : plugins.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
              <FaPuzzlePiece className="text-5xl mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-semibold mb-2">No Plugins Available</h3>
              <p className="text-gray-500 mb-4">
                Create your first plugin to extend the capabilities of your cybersecurity assistant.
              </p>
              <button
                onClick={() => {
                  resetForm();
                  setIsFormVisible(true);
                }}
                className="bg-primary-600 text-white px-4 py-2 rounded flex items-center hover:bg-primary-700 mx-auto"
              >
                <FaPlus className="mr-2" /> Add New Plugin
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {plugins.map((plugin) => (
                <div
                  key={plugin.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow p-4"
                >
                  <div className="flex justify-between items-start">
                    <h3 className="text-xl font-semibold">{plugin.name}</h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(plugin)}
                        className="text-blue-600 hover:text-blue-800"
                        title="Edit"
                      >
                        <FaEdit />
                      </button>
                      <button
                        onClick={() => handleDelete(plugin.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Delete"
                      >
                        <FaTrash />
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 mt-2">{plugin.description}</p>
                  <div className="mt-3 text-sm text-gray-500">
                    <div>API Endpoint: {plugin.api_endpoint}</div>
                    <div>API Key Required: {plugin.api_key_required ? 'Yes' : 'No'}</div>
                    <div>Parameters: {plugin.parameters.length}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Plugin Form */}
        {isFormVisible && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-2xl font-semibold mb-4">
              {editingId ? 'Edit Plugin' : 'Create New Plugin'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-gray-700 dark:text-gray-300 mb-2">
                  Plugin Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 dark:text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                  rows={3}
                  required
                ></textarea>
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 dark:text-gray-300 mb-2">
                  API Endpoint
                </label>
                <input
                  type="text"
                  name="api_endpoint"
                  value={formData.api_endpoint}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="flex items-center text-gray-700 dark:text-gray-300">
                  <input
                    type="checkbox"
                    name="api_key_required"
                    checked={formData.api_key_required}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  API Key Required
                </label>
              </div>

              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-gray-700 dark:text-gray-300">
                    Parameters
                  </label>
                  <button
                    type="button"
                    onClick={addParameter}
                    className="text-primary-600 hover:text-primary-800 flex items-center"
                  >
                    <FaPlus className="mr-1" /> Add Parameter
                  </button>
                </div>

                {formData.parameters.length === 0 ? (
                  <div className="text-gray-500 italic">No parameters defined</div>
                ) : (
                  <div className="space-y-4">
                    {formData.parameters.map((param, index) => (
                      <div key={index} className="border border-gray-300 dark:border-gray-600 p-3 rounded">
                        <div className="flex justify-between mb-2">
                          <h4 className="font-medium">Parameter #{index + 1}</h4>
                          <button
                            type="button"
                            onClick={() => removeParameter(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <FaTrash />
                          </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <div>
                            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                              Name
                            </label>
                            <input
                              type="text"
                              value={param.name}
                              onChange={(e) => handleParameterChange(index, 'name', e.target.value)}
                              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                              required
                            />
                          </div>

                          <div>
                            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                              Type
                            </label>
                            <select
                              value={param.type}
                              onChange={(e) => handleParameterChange(index, 'type', e.target.value)}
                              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                            >
                              <option value="string">String</option>
                              <option value="number">Number</option>
                              <option value="boolean">Boolean</option>
                              <option value="array">Array</option>
                              <option value="object">Object</option>
                            </select>
                          </div>

                          <div className="md:col-span-2">
                            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                              Description
                            </label>
                            <input
                              type="text"
                              value={param.description}
                              onChange={(e) => handleParameterChange(index, 'description', e.target.value)}
                              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                              required
                            />
                          </div>

                          <div className="md:col-span-2">
                            <label className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                              <input
                                type="checkbox"
                                checked={param.required}
                                onChange={(e) => handleParameterChange(index, 'required', e.target.checked)}
                                className="mr-2"
                              />
                              Required Parameter
                            </label>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                >
                  {editingId ? 'Update Plugin' : 'Create Plugin'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
