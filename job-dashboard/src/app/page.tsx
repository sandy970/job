"use client";

import { useState } from "react";
import { JobSearch } from "@/components/JobSearch";
import { JobList } from "@/components/JobList";
import { JobStats } from "@/components/JobStats";
import { UserPreferences } from "@/components/UserPreferences";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showPreferences, setShowPreferences] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handlePreferencesSaved = () => {
    setShowPreferences(false);
    setRefreshTrigger(prev => prev + 1); // Trigger refresh of job list
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Dashboard Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome to your Job Dashboard
        </h2>
        <p className="text-gray-600">
          Discover your next opportunity with AI-powered job matching
        </p>
      </div>

      {/* Stats Overview */}
      <JobStats refreshTrigger={refreshTrigger} />

      {/* Search and Controls */}
      <div className="mb-8 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex-1 max-w-2xl">
          <JobSearch onSearch={handleSearch} />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowPreferences(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Preferences
          </button>
        </div>
      </div>

      {/* User Preferences Modal */}
      {showPreferences && (
        <UserPreferences
          isOpen={showPreferences}
          onClose={() => setShowPreferences(false)}
          onSave={handlePreferencesSaved}
        />
      )}

      {/* Job Listings */}
      <JobList searchQuery={searchQuery} refreshTrigger={refreshTrigger} />
    </div>
  );
}
