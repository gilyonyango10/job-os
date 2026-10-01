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
  const [extractNote, setExtractNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const locked = busy || extracting || analyzing;

  async function refreshRequirements() {
    setRequirements(await jobsApi.listRequirements(jobId));
  }

  async function handleExtract() {
    setExtracting(true);
    setError(null);
    setExtractNote(null);
    try {
      const result = await jobsApi.extractRequirements(jobId);
      setRequirements(result.requirements);
      setAnalysis(null);
      setExtractNote(
        result.created_count === 0 && result.skipped_duplicate_count > 0
          ? `No new requirements. ${result.skipped_duplicate_count} already existed and were left unchanged.`
          : `Added ${result.created_count} requirement${result.created_count === 1 ? "" : "s"} from the job description${
              result.skipped_duplicate_count
                ? ` (${result.skipped_duplicate_count} duplicate${result.skipped_duplicate_count === 1 ? "" : "s"} skipped)`
                : ""
            }. Review them before analyzing.`,
      );
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Could not extract requirements from this job description.",
      );
    } finally {
      setExtracting(false);
    }
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
    setAnalyzing(true);
    setError(null);
    try {
      setAnalysis(await jobsApi.analyze(jobId));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not analyze this job.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Requirements</CardTitle>
          <CardDescription>
            Extract structured requirements from the job description, review them,
            then run analysis. Matching stays deterministic and does not run until
            you ask for it.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="button"
              onClick={() => void handleExtract()}
              disabled={locked}
            >
              {extracting ? "Extracting requirements…" : "Extract Requirements"}
            </Button>
            {extracting ? (
              <p className="text-sm text-muted-foreground">
                Reading the job description and structuring requirements.
              </p>
            ) : null}
          </div>
          {extractNote ? (
            <p className="text-sm text-muted-foreground">{extractNote}</p>
          ) : null}
          {requirements.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No requirements yet. Extract them from the description or add them
              by hand.
            </p>
          ) : (
            <ul className="grid gap-2">
              {requirements.map((item) => (
                <li
                  key={item.id}
                  className="flex flex-wrap items-start justify-between gap-2 rounded-lg border border-border px-3 py-2"
                >
                  <div className="grid min-w-0 flex-1 gap-1">
                    <p className="text-sm font-medium">{item.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.category} · {item.importance}
                    </p>
                    {item.evidence_text ? (
                      <p className="text-xs leading-5 text-muted-foreground">
                        Evidence from job description: “{item.evidence_text}”
                      </p>
                    ) : null}
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={locked}
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
            <Button type="submit" disabled={locked} className="w-fit">
              Add requirement
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Job analysis</CardTitle>
          <CardDescription>
            After you have reviewed the extracted requirements, compare them with
            your candidate profile. This does not call the AI matcher — only the
            deterministic engine.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <Button
            type="button"
            onClick={() => void handleAnalyze()}
            disabled={locked}
            className="w-fit"
          >
            {analyzing ? "Analyzing…" : "Analyze Job"}
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
        Add or extract at least one requirement before this job can be analyzed.
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
