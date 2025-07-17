"use client";

import { MapPin, DollarSign, Clock, Star, Sparkles } from "lucide-react";
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

interface JobCardProps {
  job: Job;
  onClick: () => void;
}

export function JobCard({ job, onClick }: JobCardProps) {
  const getMatchScoreColor = (score?: number) => {
    if (!score) return "bg-gray-100 text-gray-600";
    if (score >= 0.8) return "bg-green-100 text-green-800";
    if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const getMatchScoreText = (score?: number) => {
    if (!score) return "No match data";
    if (score >= 0.8) return "Excellent match";
    if (score >= 0.6) return "Good match";
    return "Partial match";
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
            {job.title}
          </h3>
          <p className="text-blue-600 font-medium">{job.company}</p>
        </div>
        {job.match_score && (
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.match_score)}`}>
            <div className="flex items-center gap-1">
              <Star className="h-3 w-3" />
              {Math.round(job.match_score * 100)}%
            </div>
          </div>
        )}
      </div>

      {/* Location and Salary */}
      <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
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
      </div>

      {/* AI Summary */}
      {job.ai_summary && (
        <div className="mb-3 p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-1 mb-1">
            <Sparkles className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">AI Summary</span>
          </div>
          <p className="text-sm text-blue-700 line-clamp-2">{job.ai_summary}</p>
        </div>
      )}

      {/* Requirements */}
      {job.requirements && job.requirements.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {job.requirements.slice(0, 4).map((req, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
              >
                {req}
              </span>
            ))}
            {job.requirements.length > 4 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                +{job.requirements.length - 4} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>
            {job.posted_date
              ? formatDistanceToNow(new Date(job.posted_date), { addSuffix: true })
              : formatDistanceToNow(new Date(job.scraped_at), { addSuffix: true })}
          </span>
        </div>
        <span className="capitalize text-xs px-2 py-1 bg-gray-100 rounded">
          {job.source}
        </span>
      </div>

      {/* Match Score Text */}
      {job.match_score && (
        <div className="mt-2 text-xs text-gray-600">
          {getMatchScoreText(job.match_score)}
        </div>
      )}
    </div>
  );
}