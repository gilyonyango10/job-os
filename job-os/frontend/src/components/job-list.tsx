import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import type { Job } from "@/lib/types";

type JobListProps = {
  jobs: Job[];
  isLoading: boolean;
  error: string | null;
};

export function JobList({ jobs, isLoading, error }: JobListProps) {
  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading jobs…</p>;
  }

  if (error) {
    return (
      <p className="text-sm text-destructive" role="alert">
        {error}
      </p>
    );
  }

  if (jobs.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No jobs yet. Add a role to start moving it toward an interview.
      </p>
    );
  }

  return (
    <ul className="grid gap-3">
      {jobs.map((job) => (
        <li key={job.id}>
          <Link
            href={`/jobs/${job.id}`}
            className="block rounded-xl border border-border bg-card p-4 transition-colors hover:bg-muted/50"
          >
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="font-medium">{job.title}</p>
                <p className="text-sm text-muted-foreground">
                  {job.company}
                  {job.location ? ` · ${job.location}` : ""}
                </p>
              </div>
              <Badge variant="secondary">{formatStatus(job.status)}</Badge>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

function formatStatus(status: string): string {
  return status.replaceAll("_", " ");
}
