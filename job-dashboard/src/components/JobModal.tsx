"use client";

import { X, ExternalLink, MapPin, DollarSign, Star, Sparkles, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

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

interface JobModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

export function JobModal({ job, isOpen, onClose }: JobModalProps) {
  if (!isOpen) return null;

  const handleAnalyze = async () => {
    try {
      const response = await fetch(`http://localhost:8000/jobs/${job.id}/analyze`, {
        method: "POST",
      });
      if (response.ok) {
        // Refresh job data
        window.location.reload();
      }
    } catch (error) {
      console.error("Error analyzing job:", error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{job.title}</h2>
              <p className="text-xl text-blue-600 font-medium">{job.company}</p>
              
              <div className="flex items-center gap-4 mt-3 text-gray-600">
                {job.location && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    <span>{job.location}</span>
                  </div>
                )}
                {job.salary_range && (
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-4 w-4" />
                    <span>{job.salary_range}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>
                    {job.posted_date
                      ? formatDistanceToNow(new Date(job.posted_date), { addSuffix: true })
                      : formatDistanceToNow(new Date(job.scraped_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Match Score */}
          {job.match_score && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800">Match Score</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-2xl font-bold text-green-800">
                  {Math.round(job.match_score * 100)}%
                </div>
                <div className="text-sm text-green-700">
                  This job matches your preferences and skills
                </div>
              </div>
            </div>
          )}

          {/* AI Summary */}
          {job.ai_summary && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-blue-800">AI Summary</span>
              </div>
              <p className="text-blue-700">{job.ai_summary}</p>
            </div>
          )}

          {/* Requirements */}
          {job.requirements && job.requirements.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Requirements</h3>
              <div className="flex flex-wrap gap-2">
                {job.requirements.map((req, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                  >
                    {req}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Job Description */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Job Description</h3>
            <div className="prose prose-gray max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">{job.description}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ExternalLink className="h-4 w-4" />
              View Original Job
            </a>
            
            {!job.ai_summary && (
              <button
                onClick={handleAnalyze}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Sparkles className="h-4 w-4" />
                Generate AI Analysis
              </button>
            )}
          </div>

          {/* Metadata */}
          <div className="text-sm text-gray-500 pt-4 border-t">
            <p>Source: {job.source}</p>
            <p>Scraped: {new Date(job.scraped_at).toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
}