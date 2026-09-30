"use client";

import { FormEvent, ReactNode, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export type ProfileField = {
  name: string;
  label: string;
  required?: boolean;
  type?: string;
  placeholder?: string;
  textarea?: boolean;
};

type ProfileSectionProps<T extends { id: string }> = {
  title: string;
  description: string;
  emptyText: string;
  addLabel: string;
  idPrefix: string;
  items: T[];
  fields: ProfileField[];
  valuesFor: (item: T) => Record<string, string>;
  renderSummary: (item: T) => ReactNode;
  onCreate: (form: FormData) => Promise<void>;
  onUpdate: (id: string, form: FormData) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
};

export function ProfileSection<T extends { id: string }>({
  title,
  description,
  emptyText,
  addLabel,
  idPrefix,
  items,
  fields,
  valuesFor,
  renderSummary,
  onCreate,
  onUpdate,
  onDelete,
}: ProfileSectionProps<T>) {
  const [adding, setAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(true);
    setError(null);
    try {
      await onCreate(new FormData(form));
      form.reset();
      setAdding(false);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save this entry.");
    } finally {
      setBusy(false);
    }
  }

  async function handleUpdate(id: string, event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onUpdate(id, new FormData(event.currentTarget));
      setEditingId(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not update this entry.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("Remove this entry from your profile?")) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onDelete(id);
      setEditingId(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not delete this entry.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="grid gap-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-medium">{title}</h2>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={busy || adding}
          onClick={() => {
            setAdding(true);
            setEditingId(null);
          }}
        >
          {addLabel}
        </Button>
      </div>
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
      {items.length === 0 && !adding ? (
        <p className="text-sm text-muted-foreground">{emptyText}</p>
      ) : (
        <ul className="grid gap-3">
          {items.map((item) => (
            <li key={item.id} className="rounded-xl border border-border p-4">
              {editingId === item.id ? (
                <EntryForm
                  idPrefix={`${idPrefix}-${item.id}`}
                  fields={fields}
                  defaultValues={valuesFor(item)}
                  busy={busy}
                  submitLabel="Save changes"
                  onSubmit={(event) => void handleUpdate(item.id, event)}
                  onCancel={() => setEditingId(null)}
                />
              ) : (
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">{renderSummary(item)}</div>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      disabled={busy}
                      onClick={() => {
                        setEditingId(item.id);
                        setAdding(false);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      disabled={busy}
                      onClick={() => void handleDelete(item.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
      {adding ? (
        <div className="rounded-xl border border-border p-4">
          <EntryForm
            idPrefix={`${idPrefix}-new`}
            fields={fields}
            busy={busy}
            submitLabel="Save"
            onSubmit={(event) => void handleCreate(event)}
            onCancel={() => setAdding(false)}
          />
        </div>
      ) : null}
    </section>
  );
}

function EntryForm({
  idPrefix,
  fields,
  defaultValues,
  busy,
  submitLabel,
  onSubmit,
  onCancel,
}: {
  idPrefix: string;
  fields: ProfileField[];
  defaultValues?: Record<string, string>;
  busy: boolean;
  submitLabel: string;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
}) {
  return (
    <form onSubmit={onSubmit} className="grid gap-3">
      {fields.map((field) => (
        <div key={field.name} className="grid gap-2">
          <Label htmlFor={`${idPrefix}-${field.name}`}>{field.label}</Label>
          {field.textarea ? (
            <Textarea
              id={`${idPrefix}-${field.name}`}
              name={field.name}
              required={field.required}
              rows={4}
              placeholder={field.placeholder}
              defaultValue={defaultValues?.[field.name] ?? ""}
            />
          ) : (
            <Input
              id={`${idPrefix}-${field.name}`}
              name={field.name}
              type={field.type ?? "text"}
              required={field.required}
              placeholder={field.placeholder}
              defaultValue={defaultValues?.[field.name] ?? ""}
            />
          )}
        </div>
      ))}
      <div className="flex gap-2">
        <Button type="submit" disabled={busy}>
          {busy ? "Saving…" : submitLabel}
        </Button>
        <Button type="button" variant="ghost" disabled={busy} onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
