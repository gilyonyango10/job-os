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

const EMPTY_FORM = {
  title: "",
  company: "",
  location: "",
  description: "",
  source: "manual",
  source_url: "",
};

export function JobForm({ onCreated }: JobFormProps) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function updateField(field: keyof typeof EMPTY_FORM, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const payload: JobCreate = {
      title: form.title.trim(),
      company: form.company.trim(),
      description: form.description.trim(),
      source: form.source.trim() || "manual",
      location: form.location.trim() || null,
      source_url: form.source_url.trim() || null,
    };

    try {
      const job = await jobsApi.create(payload);
      setForm(EMPTY_FORM);
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
        label="Title"
        value={form.title}
        onChange={(value) => updateField("title", value)}
        required
        placeholder="Backend Engineer"
      />
      <Field
        id="company"
        label="Company"
        value={form.company}
        onChange={(value) => updateField("company", value)}
        required
        placeholder="Northwind Labs"
      />
      <Field
        id="location"
        label="Location"
        value={form.location}
        onChange={(value) => updateField("location", value)}
        placeholder="Remote"
      />
      <div className="grid gap-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          required
          rows={6}
          value={form.description}
          onChange={(event) => updateField("description", event.target.value)}
          placeholder="Paste the job description or a short summary."
        />
      </div>
      <Field
        id="source"
        label="Source"
        value={form.source}
        onChange={(value) => updateField("source", value)}
        required
        placeholder="manual"
      />
      <Field
        id="source_url"
        label="Source URL"
        type="url"
        value={form.source_url}
        onChange={(value) => updateField("source_url", value)}
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
  label,
  value,
  onChange,
  placeholder,
  required,
  type = "text",
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  type?: string;
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type={type}
        required={required}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}
