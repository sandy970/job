"use client";

import { useState } from "react";
import { X, Plus } from "lucide-react";

interface UserPreferencesProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
}

export function UserPreferences({ isOpen, onClose, onSave }: UserPreferencesProps) {
  const [skills, setSkills] = useState<string[]>(["React", "Python", "JavaScript"]);
  const [locations, setLocations] = useState<string[]>(["Remote", "San Francisco", "New York"]);
  const [salaryMin, setSalaryMin] = useState<number>(80000);
  const [jobTypes, setJobTypes] = useState<string[]>(["Software Engineer", "Frontend Developer"]);
  const [newSkill, setNewSkill] = useState("");
  const [newLocation, setNewLocation] = useState("");
  const [newJobType, setNewJobType] = useState("");

  if (!isOpen) return null;

  const handleSave = async () => {
    try {
      const preferences = {
        skills,
        preferred_locations: locations,
        salary_min: salaryMin,
        job_types: jobTypes,
      };

      const response = await fetch("http://localhost:8000/user/preferences", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(preferences),
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error("Error saving preferences:", error);
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill("");
    }
  };

  const removeSkill = (skill: string) => {
    setSkills(skills.filter(s => s !== skill));
  };

  const addLocation = () => {
    if (newLocation.trim() && !locations.includes(newLocation.trim())) {
      setLocations([...locations, newLocation.trim()]);
      setNewLocation("");
    }
  };

  const removeLocation = (location: string) => {
    setLocations(locations.filter(l => l !== location));
  };

  const addJobType = () => {
    if (newJobType.trim() && !jobTypes.includes(newJobType.trim())) {
      setJobTypes([...jobTypes, newJobType.trim()]);
      setNewJobType("");
    }
  };

  const removeJobType = (jobType: string) => {
    setJobTypes(jobTypes.filter(jt => jt !== jobType));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Job Preferences</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <p className="text-gray-600 mt-2">
            Set your preferences to get better job matches
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Skills & Technologies
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {skills.map((skill) => (
                <div
                  key={skill}
                  className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  <span>{skill}</span>
                  <button
                    onClick={() => removeSkill(skill)}
                    className="hover:bg-blue-200 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addSkill()}
                placeholder="Add a skill (e.g., React, Python)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={addSkill}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-1"
              >
                <Plus className="h-4 w-4" />
                Add
              </button>
            </div>
          </div>

          {/* Preferred Locations */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Preferred Locations
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {locations.map((location) => (
                <div
                  key={location}
                  className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                >
                  <span>{location}</span>
                  <button
                    onClick={() => removeLocation(location)}
                    className="hover:bg-green-200 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addLocation()}
                placeholder="Add a location (e.g., Remote, San Francisco)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={addLocation}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-1"
              >
                <Plus className="h-4 w-4" />
                Add
              </button>
            </div>
          </div>

          {/* Minimum Salary */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Minimum Salary (USD)
            </label>
            <input
              type="number"
              value={salaryMin}
              onChange={(e) => setSalaryMin(Number(e.target.value))}
              placeholder="80000"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Job Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Job Types & Roles
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {jobTypes.map((jobType) => (
                <div
                  key={jobType}
                  className="flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                >
                  <span>{jobType}</span>
                  <button
                    onClick={() => removeJobType(jobType)}
                    className="hover:bg-purple-200 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newJobType}
                onChange={(e) => setNewJobType(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addJobType()}
                placeholder="Add a job type (e.g., Software Engineer)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={addJobType}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-1"
              >
                <Plus className="h-4 w-4" />
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t p-6">
          <div className="flex gap-3 justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Save Preferences
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}