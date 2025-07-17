"use client";

import { useState } from "react";
import { Search, MapPin, Loader2 } from "lucide-react";

interface JobSearchProps {
  onSearch: (query: string) => void;
}

export function JobSearch({ onSearch }: JobSearchProps) {
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Trigger job scraping
    try {
      const response = await fetch("http://localhost:8000/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keywords: query,
          location: location || undefined,
          max_jobs: 50,
        }),
      });
      
      if (response.ok) {
        onSearch(query);
      }
    } catch (error) {
      console.error("Error triggering scrape:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchFilter = () => {
    onSearch(query);
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search jobs (e.g., React Developer, Python, Machine Learning)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-48 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={!query || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Scraping Jobs...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                Scrape New Jobs
              </>
            )}
          </button>
          
          <button
            type="button"
            onClick={handleSearchFilter}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Filter Current Jobs
          </button>
        </div>
      </form>
      
      {isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-blue-800">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Scraping jobs from multiple sources... This may take a moment.</span>
          </div>
        </div>
      )}
    </div>
  );
}