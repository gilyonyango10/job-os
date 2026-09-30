import { JobsPage } from "@/components/jobs-page";
import { jobsApi } from "@/lib/api";
import type { Job } from "@/lib/types";

export default async function Home() {
  let initialJobs: Job[] = [];
  let initialError: string | null = null;

  try {
    initialJobs = await jobsApi.list();
  } catch (cause) {
    initialError =
      cause instanceof Error ? cause.message : "Could not load jobs.";
  }

  return <JobsPage initialJobs={initialJobs} initialError={initialError} />;
}
