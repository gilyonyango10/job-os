"use client";

import { useState } from "react";

import { JobForm } from "@/components/job-form";
import { JobList } from "@/components/job-list";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { jobsApi } from "@/lib/api";
import type { Job } from "@/lib/types";

type JobsPageProps = {
  initialJobs: Job[];
  initialError: string | null;
};

export function JobsPage({ initialJobs, initialError }: JobsPageProps) {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [error, setError] = useState<string | null>(initialError);

  async function refreshJobs() {
    try {
      setJobs(await jobsApi.list());
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load jobs.");
    }
  }

  return (
    <div className="mx-auto grid w-full max-w-5xl gap-6 px-4 py-8 md:grid-cols-[minmax(0,22rem)_1fr] md:py-12">
      <Card>
        <CardHeader>
          <CardTitle>Add a job</CardTitle>
          <CardDescription>
            Capture a role so you can qualify it before spending time on an
            application.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <JobForm
            onCreated={(job) => {
              setJobs((current) => [
                job,
                ...current.filter((item) => item.id !== job.id),
              ]);
              void refreshJobs();
            }}
          />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Jobs</CardTitle>
          <CardDescription>
            {jobs.length === 0
              ? "Saved opportunities will appear here."
              : `${jobs.length} saved ${jobs.length === 1 ? "opportunity" : "opportunities"}.`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <JobList jobs={jobs} isLoading={false} error={error} />
        </CardContent>
      </Card>
    </div>
  );
}
