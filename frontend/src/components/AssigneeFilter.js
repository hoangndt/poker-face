import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, Users } from 'lucide-react';
import { Listbox } from '@headlessui/react';

const AssigneeFilter = ({ assignees, selectedAssignees, onSelectionChange }) => {

  // Generate avatar from initials
  const generateAvatar = (name) => {
    if (!name) return '';
    const initials = name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .join('')
      .slice(0, 2);
    return initials;
  };

  // Generate consistent color for each person
  const getAvatarColor = (name) => {
    if (!name) return 'bg-gray-500';
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-yellow-500',
      'bg-red-500',
      'bg-teal-500',
      'bg-orange-500',
      'bg-cyan-500'
    ];
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  const handleAssigneeToggle = (assignee) => {
    const isSelected = selectedAssignees.some(selected => selected.id === assignee.id);
    let newSelection;
    
    if (isSelected) {
      newSelection = selectedAssignees.filter(selected => selected.id !== assignee.id);
    } else {
      newSelection = [...selectedAssignees, assignee];
    }
    
    onSelectionChange(newSelection);
  };

  const handleRemoveAssignee = (assigneeToRemove) => {
    const newSelection = selectedAssignees.filter(assignee => assignee.id !== assigneeToRemove.id);
    onSelectionChange(newSelection);
  };

  const clearAllSelections = () => {
    onSelectionChange([]);
  };

  return (
    <Listbox value={selectedAssignees} onChange={onSelectionChange} multiple>
      <div className="relative">
        {/* Filter Button and Selected Pills Container */}
        <div className="flex items-center flex-wrap gap-2">
          {/* Filter Button */}
          <Listbox.Button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ui-open:ring-2 ui-open:ring-blue-500">
            <Users className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-700">
              {selectedAssignees.length === 0
                ? 'Filter by Assignee'
                : `${selectedAssignees.length} selected`
              }
            </span>
            <ChevronDown className="h-4 w-4 text-gray-500 transition-transform ui-open:rotate-180" />
          </Listbox.Button>

          {/* Selected Assignees Pills - Inline */}
          {selectedAssignees.length > 0 && (
            <>
              {selectedAssignees.map(assignee => (
                <div
                  key={assignee.id}
                  className="flex items-center space-x-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                >
                  <div className={`w-5 h-5 rounded-full ${getAvatarColor(assignee.name)} flex items-center justify-center text-white text-xs font-medium`}>
                    {generateAvatar(assignee.name)}
                  </div>
                  <span>{assignee.name}</span>
                  <button
                    onClick={() => handleRemoveAssignee(assignee)}
                    className="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
              {selectedAssignees.length > 1 && (
                <button
                  onClick={clearAllSelections}
                  className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 hover:bg-gray-100 rounded transition-colors"
                >
                  Clear all
                </button>
              )}
            </>
          )}
        </div>

        {/* Dropdown Menu */}
        <Listbox.Options className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-64 max-w-[400px] focus:outline-none">
          <div className="sticky top-0 bg-white text-xs font-medium text-gray-500 px-3 py-2 border-b border-gray-100 rounded-t-lg z-10">
            Select Assignees
          </div>

          {assignees.length === 0 ? (
            <div className="px-3 py-4 text-sm text-gray-500 text-center">
              No assignees found
            </div>
          ) : (
            <div className="max-h-64 overflow-y-auto py-1">
              {assignees.map(assignee => {
                const isSelected = selectedAssignees.some(selected => selected.id === assignee.id);
                return (
                  <Listbox.Option
                    key={assignee.id}
                    value={assignee}
                    className={({ active }) => `
                      w-full flex items-center space-x-3 px-3 py-2 text-left cursor-pointer transition-colors
                      ${active ? 'bg-gray-50' : ''}
                      ${isSelected ? 'bg-blue-50 text-blue-900' : 'text-gray-700'}
                    `}
                  >
                    {({ selected }) => (
                      <>
                        {/* Avatar */}
                        <div className={`w-8 h-8 rounded-full ${getAvatarColor(assignee.name)} flex items-center justify-center text-white text-sm font-medium flex-shrink-0`}>
                          {generateAvatar(assignee.name)}
                        </div>

                        {/* Name and Role */}
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm truncate">
                            {assignee.name}
                          </div>
                          {assignee.role && (
                            <div className="text-xs text-gray-500 truncate">
                              {assignee.role.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                            </div>
                          )}
                        </div>

                        {/* Checkbox */}
                        <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                          isSelected
                            ? 'bg-blue-500 border-blue-500'
                            : 'border-gray-300'
                        }`}>
                          {isSelected && (
                            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                      </>
                    )}
                  </Listbox.Option>
                );
              })}
            </div>
          )}
        </Listbox.Options>
      </div>
    </Listbox>
  );
};

export default AssigneeFilter;
