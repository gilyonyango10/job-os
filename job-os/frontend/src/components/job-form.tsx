"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { jobsApi } from "@/lib/api";
import type { Job, JobCreate } from "@/lib/types";

type JobFormProps = {
  onCreated: (job: Job) => void;
};

export function JobForm({ onCreated }: JobFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setIsSubmitting(true);
    setError(null);

    const payload: JobCreate = {
      title: String(data.get("title") ?? "").trim(),
      company: String(data.get("company") ?? "").trim(),
      description: String(data.get("description") ?? "").trim(),
      source: String(data.get("source") ?? "").trim() || "manual",
      location: String(data.get("location") ?? "").trim() || null,
      source_url: String(data.get("source_url") ?? "").trim() || null,
    };

    try {
      const job = await jobsApi.create(payload);
      form.reset();
      onCreated(job);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save this job.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <Field
        id="title"
        name="title"
        label="Title"
        required
        placeholder="Backend Engineer"
      />
      <Field
        id="company"
        name="company"
        label="Company"
        required
        placeholder="Northwind Labs"
      />
      <Field
        id="location"
        name="location"
        label="Location"
        placeholder="Remote"
      />
      <div className="grid gap-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          name="description"
          required
          rows={6}
          placeholder="Paste the job description or a short summary."
        />
      </div>
      <Field
        id="source"
        name="source"
        label="Source"
        required
        defaultValue="manual"
        placeholder="manual"
      />
      <Field
        id="source_url"
        name="source_url"
        label="Source URL"
        type="url"
        placeholder="https://example.com/jobs/backend-engineer"
      />
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving…" : "Save job"}
      </Button>
    </form>
  );
}

function Field({
  id,
  name,
  label,
  placeholder,
  required,
  type = "text",
  defaultValue,
}: {
  id: string;
  name: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  type?: string;
  defaultValue?: string;
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        name={name}
        type={type}
        required={required}
        defaultValue={defaultValue}
        placeholder={placeholder}
      />
    </div>
  );
}
