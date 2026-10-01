"use client";

import { FormEvent, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { jobsApi } from "@/lib/api";
import type {
  JobAnalysis,
  Requirement,
  RequirementCategory,
  RequirementImportance,
  RequirementMatch,
} from "@/lib/types";

type JobIntelligenceProps = {
  jobId: string;
  initialRequirements: Requirement[];
};

export function JobIntelligence({
  jobId,
  initialRequirements,
}: JobIntelligenceProps) {
  const [requirements, setRequirements] = useState(initialRequirements);
  const [analysis, setAnalysis] = useState<JobAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function refreshRequirements() {
    setRequirements(await jobsApi.listRequirements(jobId));
  }

  async function handleAddRequirement(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy(true);
    setError(null);
    try {
      await jobsApi.addRequirement(jobId, {
        name: String(data.get("name") ?? "").trim(),
        category: String(data.get("category") ?? "skill") as RequirementCategory,
        importance: String(
          data.get("importance") ?? "required",
        ) as RequirementImportance,
        description: String(data.get("description") ?? "").trim() || null,
      });
      form.reset();
      await refreshRequirements();
      setAnalysis(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save the requirement.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(requirementId: string) {
    setBusy(true);
    setError(null);
    try {
      await jobsApi.deleteRequirement(jobId, requirementId);
      await refreshRequirements();
      setAnalysis(null);
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Could not delete the requirement.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleAnalyze() {
    setBusy(true);
    setError(null);
    try {
      setAnalysis(await jobsApi.analyze(jobId));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not analyze this job.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Requirements</CardTitle>
          <CardDescription>
            Capture what this job needs so it can be compared with your profile.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          {requirements.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No requirements yet. Add the skills and experience the role asks for.
            </p>
          ) : (
            <ul className="grid gap-2">
              {requirements.map((item) => (
                <li
                  key={item.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2"
                >
                  <div>
                    <p className="text-sm font-medium">{item.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.category} · {item.importance}
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={busy}
                    onClick={() => void handleDelete(item.id)}
                  >
                    Remove
                  </Button>
                </li>
              ))}
            </ul>
          )}
          <form onSubmit={handleAddRequirement} className="grid gap-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="requirement-name">Requirement</Label>
                <Input
                  id="requirement-name"
                  name="name"
                  required
                  placeholder="Python"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="requirement-category">Category</Label>
                <select
                  id="requirement-category"
                  name="category"
                  defaultValue="skill"
                  className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm"
                >
                  <option value="skill">skill</option>
                  <option value="technology">technology</option>
                  <option value="experience">experience</option>
                  <option value="education">education</option>
                  <option value="responsibility">responsibility</option>
                  <option value="certification">certification</option>
                  <option value="other">other</option>
                </select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="requirement-importance">Importance</Label>
                <select
                  id="requirement-importance"
                  name="importance"
                  defaultValue="required"
                  className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm"
                >
                  <option value="required">required</option>
                  <option value="preferred">preferred</option>
                </select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="requirement-description">Description</Label>
                <Input
                  id="requirement-description"
                  name="description"
                  placeholder="Optional detail"
                />
              </div>
            </div>
            <Button type="submit" disabled={busy} className="w-fit">
              Add requirement
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Job analysis</CardTitle>
          <CardDescription>
            Compare these requirements with your candidate profile. No score yet —
            just the evidence, transfers, and gaps.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <Button
            type="button"
            onClick={() => void handleAnalyze()}
            disabled={busy}
            className="w-fit"
          >
            {busy ? "Analyzing…" : "Analyze Job"}
          </Button>
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
          {analysis ? <AnalysisResults analysis={analysis} /> : null}
        </CardContent>
      </Card>
    </div>
  );
}

function AnalysisResults({ analysis }: { analysis: JobAnalysis }) {
  if (analysis.requirements.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Add at least one requirement before this job can be analyzed.
      </p>
    );
  }

  return (
    <div className="grid gap-4">
      <MatchGroup
        title="Strong Evidence"
        empty="No direct evidence yet."
        items={analysis.strong_evidence}
        tone="strong"
      />
      <MatchGroup
        title="Transferable"
        empty="No transferable evidence."
        items={analysis.transferable}
        tone="transferable"
      />
      <MatchGroup title="Gaps" empty="No gaps." items={analysis.gaps} tone="gap" />
      <MatchGroup
        title="Required Gaps"
        empty="No required gaps."
        items={analysis.required_gaps}
        tone="gap"
      />
      <MatchGroup
        title="Preferred Gaps"
        empty="No preferred gaps."
        items={analysis.preferred_gaps}
        tone="gap"
      />
    </div>
  );
}

function MatchGroup({
  title,
  empty,
  items,
  tone,
}: {
  title: string;
  empty: string;
  items: RequirementMatch[];
  tone: "strong" | "transferable" | "gap";
}) {
  const toneClass = {
    strong: "border-l-4 border-l-emerald-600",
    transferable: "border-l-4 border-l-amber-500",
    gap: "border-l-4 border-l-destructive",
  }[tone];

  return (
    <section className={`grid gap-2 rounded-lg border border-border p-3 ${toneClass}`}>
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-medium">{title}</h3>
        <Badge variant={tone === "gap" ? "destructive" : "secondary"}>{items.length}</Badge>
      </div>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground">{empty}</p>
      ) : (
        <ul className="grid gap-2">
          {items.map((item) => (
            <li key={item.requirement_id}>
              <p className="text-sm font-medium">{item.requirement_name}</p>
              {item.evidence.length > 0 ? (
                <ul className="mt-1 list-disc pl-5 text-xs text-muted-foreground">
                  {item.evidence.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
