"use client";

import { useQuery } from "@tanstack/react-query";
import { Briefcase, TrendingUp, MapPin, Star } from "lucide-react";

interface JobStatsProps {
  refreshTrigger: number;
}

export function JobStats({ refreshTrigger }: JobStatsProps) {
  const { data: jobs = [] } = useQuery({
    queryKey: ["jobs", refreshTrigger],
    queryFn: async () => {
      try {
        const response = await fetch("http://localhost:8000/jobs");
        if (!response.ok) throw new Error("Failed to fetch");
        return response.json();
      } catch {
        return getMockJobs();
      }
    },
  });

  const totalJobs = jobs.length;
  const remoteJobs = jobs.filter((job: { location?: string }) => 
    job.location?.toLowerCase().includes("remote")
  ).length;
  const highMatchJobs = jobs.filter((job: { match_score?: number }) => 
    job.match_score && job.match_score >= 0.8
  ).length;
  const recentJobs = jobs.filter((job: { scraped_at: string }) => {
    const scraped = new Date(job.scraped_at);
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return scraped > yesterday;
  }).length;

  const stats = [
    {
      name: "Total Jobs",
      value: totalJobs.toLocaleString(),
      icon: Briefcase,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      name: "New Today",
      value: recentJobs.toLocaleString(),
      icon: TrendingUp,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      name: "Remote Jobs",
      value: remoteJobs.toLocaleString(),
      icon: MapPin,
      color: "text-purple-600",
      bgColor: "bg-purple-100",
    },
    {
      name: "High Match",
      value: highMatchJobs.toLocaleString(),
      icon: Star,
      color: "text-yellow-600",
      bgColor: "bg-yellow-100",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div key={stat.name} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <Icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function getMockJobs() {
  return [
    {
      id: "1",
      location: "San Francisco, CA",
      match_score: 0.85,
      scraped_at: new Date().toISOString(),
    },
    {
      id: "2",
      location: "Remote",
      match_score: 0.72,
      scraped_at: new Date().toISOString(),
    },
    {
      id: "3",
      location: "New York, NY",
      match_score: 0.68,
      scraped_at: new Date(Date.now() - 86400000).toISOString(),
    },
  ];
}