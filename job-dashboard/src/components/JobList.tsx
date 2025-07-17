"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { JobCard } from "./JobCard";
import { JobModal } from "./JobModal";
import { Loader2 } from "lucide-react";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  description: string;
  requirements?: string[];
  url: string;
  source: string;
  posted_date?: string;
  scraped_at: string;
  ai_summary?: string;
  match_score?: number;
}

interface JobListProps {
  searchQuery: string;
  refreshTrigger: number;
}

export function JobList({ searchQuery, refreshTrigger }: JobListProps) {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);

  const { data: jobs = [], isLoading, error, refetch } = useQuery({
    queryKey: ["jobs"],
    queryFn: async (): Promise<Job[]> => {
      try {
        const response = await fetch("http://localhost:8000/jobs");
        if (!response.ok) {
          throw new Error("Failed to fetch jobs");
        }
        return response.json();
      } catch (error) {
        console.error("Error fetching jobs:", error);
        // Return mock data for demo
        return getMockJobs();
      }
    },
    refetchInterval: 30000, // Refetch every 30 seconds for real-time updates
  });

  // Trigger refetch when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger > 0) {
      refetch();
    }
  }, [refreshTrigger, refetch]);

  // Filter jobs based on search query
  useEffect(() => {
    if (!searchQuery) {
      setFilteredJobs(jobs);
    } else {
      const filtered = jobs.filter(
        (job) =>
          job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
          job.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          job.requirements?.some((req) =>
            req.toLowerCase().includes(searchQuery.toLowerCase())
          )
      );
      setFilteredJobs(filtered);
    }
  }, [jobs, searchQuery]);

  const handleJobClick = (job: Job) => {
    setSelectedJob(job);
  };

  const handleCloseModal = () => {
    setSelectedJob(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center gap-2 text-gray-600">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading jobs...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Error loading jobs</p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (filteredJobs.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">
          {searchQuery
            ? `No jobs found for "${searchQuery}"`
            : "No jobs available"}
        </p>
        <p className="text-sm text-gray-500">
          Try searching for different keywords or scrape new jobs above
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          {filteredJobs.length} Job{filteredJobs.length !== 1 ? "s" : ""} Found
          {searchQuery && ` for "${searchQuery}"`}
        </h3>
        <div className="text-sm text-gray-500">
          Updated {new Date().toLocaleTimeString()}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredJobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onClick={() => handleJobClick(job)}
          />
        ))}
      </div>

      {selectedJob && (
        <JobModal
          job={selectedJob}
          isOpen={!!selectedJob}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}

// Mock data for demo purposes
function getMockJobs(): Job[] {
  return [
    {
      id: "1",
      title: "Senior Software Engineer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      salary_range: "$120,000 - $180,000",
      description: "We are looking for a senior software engineer to join our team...",
      requirements: ["Python", "React", "PostgreSQL", "AWS"],
      url: "https://example.com/job/1",
      source: "demo",
      scraped_at: new Date().toISOString(),
      ai_summary: "Senior role with leadership responsibilities, focus on full-stack development",
      match_score: 0.85,
    },
    {
      id: "2",
      title: "Frontend Developer",
      company: "StartupXYZ",
      location: "Remote",
      salary_range: "$80,000 - $120,000",
      description: "Join our innovative startup as a frontend developer...",
      requirements: ["React", "TypeScript", "CSS", "Next.js"],
      url: "https://example.com/job/2",
      source: "demo",
      scraped_at: new Date().toISOString(),
      ai_summary: "Remote frontend position with modern tech stack",
      match_score: 0.72,
    },
    {
      id: "3",
      title: "Data Scientist",
      company: "AI Solutions Ltd",
      location: "New York, NY",
      salary_range: "$100,000 - $150,000",
      description: "We're seeking a data scientist to analyze large datasets...",
      requirements: ["Python", "Machine Learning", "SQL", "TensorFlow"],
      url: "https://example.com/job/3",
      source: "demo",
      scraped_at: new Date().toISOString(),
      ai_summary: "Data science role with ML focus, hybrid work environment",
      match_score: 0.68,
    },
  ];
}