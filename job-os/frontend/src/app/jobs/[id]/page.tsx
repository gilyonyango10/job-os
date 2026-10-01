import { JobDetailPage } from "@/components/job-detail-page";
import { ApiError, jobsApi } from "@/lib/api";
import type { Job, Requirement } from "@/lib/types";

type JobPageProps = {
  params: Promise<{ id: string }>;
};

export default async function JobPage({ params }: JobPageProps) {
  const { id } = await params;
  let job: Job | undefined;
  let requirements: Requirement[] = [];
  let error: string | undefined;

  try {
    job = await jobsApi.get(id);
    requirements = await jobsApi.listRequirements(id);
  } catch (cause) {
    error =
      cause instanceof ApiError && cause.status === 404
        ? "This job was not found."
        : cause instanceof Error
          ? cause.message
          : "Could not load this job.";
  }

  return (
    <JobDetailPage job={job} requirements={requirements} error={error} />
  );
}
