"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ApiError, jobsApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Job } from "@/lib/types";

type JobDetailPageProps = {
  jobId: string;
};

export function JobDetailPage({ jobId }: JobDetailPageProps) {
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadJob() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await jobsApi.get(jobId);
        if (!cancelled) {
          setJob(result);
        }
      } catch (cause) {
        if (!cancelled) {
          setJob(null);
          if (cause instanceof ApiError && cause.status === 404) {
            setError("This job was not found.");
          } else {
            setError(
              cause instanceof Error ? cause.message : "Could not load this job.",
            );
          }
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadJob();
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  return (
    <div className="mx-auto grid w-full max-w-3xl gap-4 px-4 py-8 md:py-12">
      <Link
        href="/"
        className={cn(buttonVariants({ variant: "ghost" }), "w-fit px-0")}
      >
        Back to jobs
      </Link>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading job…</p>
      ) : error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : job ? (
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <CardTitle className="text-2xl">{job.title}</CardTitle>
                <CardDescription>
                  {job.company}
                  {job.location ? ` · ${job.location}` : ""}
                </CardDescription>
              </div>
              <Badge variant="secondary">{job.status.replaceAll("_", " ")}</Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-6">
            <Detail label="Source" value={job.source} />
            <Detail
              label="Source URL"
              value={job.source_url}
              href={job.source_url}
            />
            <Detail
              label="Added"
              value={new Date(job.created_at).toLocaleString()}
            />
            <div className="grid gap-2">
              <h2 className="text-sm font-medium">Description</h2>
              <p className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
                {job.description}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function Detail({
  label,
  value,
  href,
}: {
  label: string;
  value: string | null;
  href?: string | null;
}) {
  return (
    <div className="grid gap-1">
      <h2 className="text-sm font-medium">{label}</h2>
      {href && value ? (
        <a
          href={href}
          className="break-all text-sm text-primary underline-offset-4 hover:underline"
          target="_blank"
          rel="noreferrer"
        >
          {value}
        </a>
      ) : (
        <p className="text-sm text-muted-foreground">{value || "Not provided"}</p>
      )}
    </div>
  );
}
