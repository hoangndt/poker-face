import React, { useState, useEffect, useMemo } from 'react';
import {
  Search,
  Filter,
  Users,
  Mail,
  Phone,
  Building,
  DollarSign,
  Calendar,
  User,
  ChevronUp,
  ChevronDown,
  Eye,
  Edit,
  Trash2,
  Plus,
  Target,
  Lightbulb
} from 'lucide-react';
import { sprintAPI } from '../services/api';
import toast from 'react-hot-toast';

const STATUS_COLORS = {
  lead: 'bg-gray-100 text-gray-800',
  qualified_solution: 'bg-blue-100 text-blue-800',
  qualified_delivery: 'bg-yellow-100 text-yellow-800',
  qualified_cso: 'bg-purple-100 text-purple-800',
  deal: 'bg-green-100 text-green-800',
  project: 'bg-emerald-100 text-emerald-800'
};

const STATUS_LABELS = {
  lead: 'Lead',
  qualified_solution: 'Qualified Solution',
  qualified_delivery: 'Qualified Delivery',
  qualified_cso: 'CSO Review',
  deal: 'Deal',
  project: 'Project'
};

const SOURCE_COLORS = {
  'SEO': 'bg-purple-50 text-purple-700',
  'Networking Event': 'bg-blue-50 text-blue-700',
  'Summit Event': 'bg-indigo-50 text-indigo-700',
  'Cold Outreach': 'bg-orange-50 text-orange-700',
  'Referral': 'bg-green-50 text-green-700',
  'Social Media': 'bg-pink-50 text-pink-700',
  'Website Form': 'bg-cyan-50 text-cyan-700',
  'Trade Show': 'bg-yellow-50 text-yellow-700',
  'Partner Referral': 'bg-emerald-50 text-emerald-700',
  'Content Marketing': 'bg-violet-50 text-violet-700'
};

const SOLUTION_COLORS = {
  'Enterprise Software': 'bg-blue-50 text-blue-700',
  'Cloud Infrastructure': 'bg-sky-50 text-sky-700',
  'Data Analytics': 'bg-purple-50 text-purple-700',
  'CRM Solutions': 'bg-green-50 text-green-700',
  'Marketing Automation': 'bg-pink-50 text-pink-700',
  'Cybersecurity': 'bg-red-50 text-red-700',
  'AI/ML Platform': 'bg-indigo-50 text-indigo-700',
  'E-commerce Platform': 'bg-orange-50 text-orange-700',
  'Business Intelligence': 'bg-violet-50 text-violet-700',
  'Integration Services': 'bg-teal-50 text-teal-700'
};

const Contacts = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [companyFilter, setCompanyFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [solutionFilter, setSolutionFilter] = useState('');
  const [sortField, setSortField] = useState('full_name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [summary, setSummary] = useState(null);
  const [editingNote, setEditingNote] = useState(null);
  const [noteValues, setNoteValues] = useState({});
  const [savingNote, setSavingNote] = useState(null);

  useEffect(() => {
    fetchContacts();
    fetchSummary();
  }, []);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const response = await sprintAPI.getContacts();
      setContacts(response.data);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      toast.error('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await sprintAPI.getContactsSummary();
      setSummary(response.data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const handleNoteEdit = (contactId, currentNote) => {
    setEditingNote(contactId);
    setNoteValues({ ...noteValues, [contactId]: currentNote || '' });
  };

  const handleNoteSave = async (contactId) => {
    try {
      setSavingNote(contactId);
      const noteValue = noteValues[contactId]?.trim() || '';
      await sprintAPI.updateContact(contactId, { note: noteValue });

      // Update local state
      setContacts(contacts.map(contact =>
        contact.id === contactId
          ? { ...contact, note: noteValue }
          : contact
      ));

      setEditingNote(null);
      setNoteValues({ ...noteValues, [contactId]: '' });
      toast.success('Note updated successfully');
    } catch (error) {
      console.error('Error updating note:', error);
      toast.error('Failed to update note');
    } finally {
      setSavingNote(null);
    }
  };

  const handleNoteCancel = (contactId) => {
    setEditingNote(null);
    setNoteValues({ ...noteValues, [contactId]: '' });
  };

  const filteredAndSortedContacts = useMemo(() => {
    let filtered = contacts.filter(contact => {
      const matchesSearch = !searchTerm ||
        contact.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.position?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.lead_source?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.solution_interest?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = !statusFilter || contact.status === statusFilter;
      const matchesCompany = !companyFilter ||
        contact.company_name?.toLowerCase().includes(companyFilter.toLowerCase());
      const matchesSource = !sourceFilter || contact.lead_source === sourceFilter;
      const matchesSolution = !solutionFilter || contact.solution_interest === solutionFilter;

      return matchesSearch && matchesStatus && matchesCompany && matchesSource && matchesSolution;
    });

    // Sort contacts
    filtered.sort((a, b) => {
      let aValue = a[sortField] || '';
      let bValue = b[sortField] || '';
      
      // Handle numeric fields
      if (sortField === 'estimated_revenue' || sortField === 'gmv') {
        aValue = parseFloat(aValue) || 0;
        bValue = parseFloat(bValue) || 0;
      }
      
      // Handle date fields
      if (sortField === 'estimated_close_date') {
        aValue = new Date(aValue || 0);
        bValue = new Date(bValue || 0);
      }
      
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      if (sortDirection === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [contacts, searchTerm, statusFilter, companyFilter, sourceFilter, solutionFilter, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const SortableHeader = ({ field, children, className = "" }) => (
    <th 
      className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 ${className}`}
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field && (
          sortDirection === 'asc' ? 
            <ChevronUp className="h-4 w-4" /> : 
            <ChevronDown className="h-4 w-4" />
        )}
      </div>
    </th>
  );

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contacts Management</h1>
          <p className="text-gray-600">Manage and track all your business contacts</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>New Contact</span>
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Contacts</p>
                <p className="text-2xl font-bold text-gray-900">{summary.total_contacts}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Est. Revenue</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.total_estimated_revenue)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <Building className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg. GMV</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.average_gmv)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Deals</p>
                <p className="text-2xl font-bold text-gray-900">{summary.status_distribution?.deal || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="relative lg:col-span-2">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search contacts..."
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            {Object.entries(STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
          >
            <option value="">All Sources</option>
            <option value="SEO">SEO</option>
            <option value="Networking Event">Networking Event</option>
            <option value="Summit Event">Summit Event</option>
            <option value="Cold Outreach">Cold Outreach</option>
            <option value="Referral">Referral</option>
            <option value="Social Media">Social Media</option>
            <option value="Website Form">Website Form</option>
            <option value="Trade Show">Trade Show</option>
            <option value="Partner Referral">Partner Referral</option>
            <option value="Content Marketing">Content Marketing</option>
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            value={solutionFilter}
            onChange={(e) => setSolutionFilter(e.target.value)}
          >
            <option value="">All Solutions</option>
            <option value="Enterprise Software">Enterprise Software</option>
            <option value="Cloud Infrastructure">Cloud Infrastructure</option>
            <option value="Data Analytics">Data Analytics</option>
            <option value="CRM Solutions">CRM Solutions</option>
            <option value="Marketing Automation">Marketing Automation</option>
            <option value="Cybersecurity">Cybersecurity</option>
            <option value="AI/ML Platform">AI/ML Platform</option>
            <option value="E-commerce Platform">E-commerce Platform</option>
            <option value="Business Intelligence">Business Intelligence</option>
            <option value="Integration Services">Integration Services</option>
          </select>
          <div className="flex items-center text-sm text-gray-600">
            <Filter className="h-4 w-4 mr-2" />
            {filteredAndSortedContacts.length} of {contacts.length} contacts
          </div>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-white shadow border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 table-fixed">
            <thead className="bg-gray-50">
              <tr>
                <SortableHeader field="full_name">Full Name</SortableHeader>
                <SortableHeader field="position">Position</SortableHeader>
                <SortableHeader field="company_name">Company</SortableHeader>
                <SortableHeader field="gmv">GMV</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact Info
                </th>
                <SortableHeader field="lead_source">Lead Source</SortableHeader>
                <SortableHeader field="solution_interest">Solution Interest</SortableHeader>
                <SortableHeader field="status">Status</SortableHeader>
                <SortableHeader field="estimated_revenue">Est Revenue</SortableHeader>
                <SortableHeader field="estimated_close_date">Est Close Date</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Team
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAndSortedContacts.map((contact) => (
                <tr key={contact.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <User className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{contact.full_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contact.position || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contact.company_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(contact.gmv)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="space-y-1">
                      {contact.email && (
                        <div className="flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          <span className="truncate max-w-32">{contact.email}</span>
                        </div>
                      )}
                      {contact.phone_number && (
                        <div className="flex items-center">
                          <Phone className="h-3 w-3 mr-1" />
                          <span>{contact.phone_number}</span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contact.lead_source && (
                      <div className="flex items-center">
                        <Target className="h-4 w-4 mr-2 text-blue-500" />
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${SOURCE_COLORS[contact.lead_source] || 'bg-gray-50 text-gray-700'}`}>
                          {contact.lead_source}
                        </span>
                      </div>
                    )}
                    {!contact.lead_source && <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {contact.solution_interest && (
                      <div className="flex items-center">
                        <Lightbulb className="h-4 w-4 mr-2 text-green-500" />
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${SOLUTION_COLORS[contact.solution_interest] || 'bg-gray-50 text-gray-700'}`}>
                          {contact.solution_interest}
                        </span>
                      </div>
                    )}
                    {!contact.solution_interest && <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${STATUS_COLORS[contact.status] || 'bg-gray-100 text-gray-800'}`}>
                      {STATUS_LABELS[contact.status] || contact.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(contact.estimated_revenue)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(contact.estimated_close_date)}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-900" style={{ maxWidth: '300px', minWidth: '200px' }}>
                    {editingNote === contact.id ? (
                      <div className="space-y-2">
                        <textarea
                          value={noteValues[contact.id] || ''}
                          onChange={(e) => setNoteValues({ ...noteValues, [contact.id]: e.target.value })}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && e.ctrlKey) {
                              handleNoteSave(contact.id);
                            } else if (e.key === 'Escape') {
                              handleNoteCancel(contact.id);
                            }
                          }}
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                          rows="3"
                          placeholder="Add a note... (Ctrl+Enter to save, Esc to cancel)"
                          autoFocus
                        />
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleNoteSave(contact.id)}
                            disabled={savingNote === contact.id}
                            className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {savingNote === contact.id ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            onClick={() => handleNoteCancel(contact.id)}
                            className="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div
                        className="cursor-pointer hover:bg-gray-50 p-2 rounded min-h-[2rem] border border-transparent hover:border-gray-200"
                        onClick={() => handleNoteEdit(contact.id, contact.note)}
                      >
                        {contact.note ? (
                          <span className="text-gray-900">{contact.note}</span>
                        ) : (
                          <span className="text-gray-400 italic">Click to add note...</span>
                        )}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="space-y-1">
                      <div>Owner: {contact.contact_owner?.name || '-'}</div>
                      <div>Designer: {contact.solution_designer?.name || '-'}</div>
                      <div>Team: {contact.delivery_team_assigned || '-'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="text-green-600 hover:text-green-900">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredAndSortedContacts.length === 0 && (
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || statusFilter || companyFilter || sourceFilter || solutionFilter
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by creating your first contact.'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Contacts;
