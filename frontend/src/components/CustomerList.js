import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, ChevronDown, ExternalLink, AlertTriangle } from 'lucide-react';
import { customerAPI, aiAPI } from '../services/api';
import toast from 'react-hot-toast';

const CustomerList = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stageFilter, setStageFilter] = useState('all');
  const [churnPredictions, setChurnPredictions] = useState({});

  useEffect(() => {
    fetchCustomers();
  }, [stageFilter]);

  const fetchCustomers = async () => {
    try {
      const params = stageFilter !== 'all' ? { stage: stageFilter } : {};
      const response = await customerAPI.getCustomers(params);
      setCustomers(response.data);
      
      // Get churn predictions for customers
      const predictions = {};
      for (const customer of response.data.slice(0, 20)) { // Limit to first 20 for demo
        if (customer.Customer_Flag) {
          try {
            const churnRes = await aiAPI.predictChurn(customer.id);
            predictions[customer.id] = churnRes.data;
          } catch (error) {
            // Ignore individual prediction errors
          }
        }
      }
      setChurnPredictions(predictions);
    } catch (error) {
      toast.error('Failed to load customers');
      console.error('Customers error:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = 
      customer.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  const getStageDisplay = (customer) => {
    if (customer.Churn_Flag) return { label: 'Churned', color: 'bg-red-100 text-red-800' };
    if (customer.Customer_Flag) return { label: 'Customer', color: 'bg-green-100 text-green-800' };
    if (customer.SQL_Flag) return { label: 'SQL', color: 'bg-blue-100 text-blue-800' };
    if (customer.MQL_Flag) return { label: 'MQL', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Lead', color: 'bg-gray-100 text-gray-800' };
  };

  const getRiskLevel = (customerId) => {
    const prediction = churnPredictions[customerId];
    if (!prediction) return null;
    
    const probability = prediction.churn_probability;
    if (probability > 0.7) return { label: 'High Risk', color: 'bg-red-100 text-red-800' };
    if (probability > 0.4) return { label: 'Medium Risk', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Low Risk', color: 'bg-green-100 text-green-800' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Customer Management
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage and track customer lifecycle stages
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search customers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Stage Filter */}
          <div className="relative">
            <select
              value={stageFilter}
              onChange={(e) => setStageFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
            >
              <option value="all">All Stages</option>
              <option value="lead">Leads</option>
              <option value="mql">MQLs</option>
              <option value="sql">SQLs</option>
              <option value="customer">Customers</option>
              <option value="churned">Churned</option>
            </select>
          </div>

          {/* Results Count */}
          <div className="flex items-center text-sm text-gray-500">
            Showing {filteredCustomers.length} of {customers.length} customers
          </div>
        </div>
      </div>

      {/* Customer Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredCustomers.map((customer) => {
            const stage = getStageDisplay(customer);
            const risk = getRiskLevel(customer.id);
            
            return (
              <li key={customer.id}>
                <Link
                  to={`/customers/${customer.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <span className="text-sm font-medium text-gray-700">
                            {customer.first_name?.[0]}{customer.last_name?.[0]}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">
                            {customer.first_name} {customer.last_name}
                          </div>
                          {risk && (
                            <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${risk.color}`}>
                              <AlertTriangle className="w-3 h-3 mr-1" />
                              {risk.label}
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500">
                          {customer.email}
                        </div>
                        <div className="flex items-center mt-1">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${stage.color}`}>
                            {stage.label}
                          </span>
                          {customer.Industry && (
                            <span className="ml-2 text-xs text-gray-500">
                              {customer.Industry}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {customer.ACV_USD && (
                        <div className="text-sm text-gray-900 font-medium">
                          ${customer.ACV_USD.toLocaleString()}
                        </div>
                      )}
                      <ExternalLink className="h-5 w-5 text-gray-400" />
                    </div>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {filteredCustomers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-sm text-gray-500">No customers found matching your criteria</div>
        </div>
      )}
    </div>
  );
};

export default CustomerList;