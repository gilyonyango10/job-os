"use client";

import { useCallback, useEffect, useState } from "react";

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

export function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = useCallback(async (options?: { silent?: boolean }) => {
    if (!options?.silent) {
      setIsLoading(true);
    }
    setError(null);
    try {
      setJobs(await jobsApi.list());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load jobs.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadJobs();
  }, [loadJobs]);

  function handleCreated() {
    void loadJobs({ silent: true });
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
          <JobForm onCreated={handleCreated} />
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
          <JobList jobs={jobs} isLoading={isLoading} error={error} />
        </CardContent>
      </Card>
    </div>
  );
}
