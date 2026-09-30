"use client";

import { FormEvent, useState } from "react";

import { ProfileSection } from "@/components/profile-section";
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
import { Textarea } from "@/components/ui/textarea";
import { profileApi } from "@/lib/api";
import type {
  Candidate,
  CertificationWrite,
  EducationWrite,
  ExperienceWrite,
  ProjectWrite,
  SkillWrite,
} from "@/lib/types";

type ProfilePageProps = {
  initialProfile: Candidate | null;
  initialError: string | null;
};

export function ProfilePage({ initialProfile, initialError }: ProfilePageProps) {
  const [profile, setProfile] = useState<Candidate | null>(initialProfile);
  const [error, setError] = useState<string | null>(initialError);
  const [infoError, setInfoError] = useState<string | null>(null);
  const [savingInfo, setSavingInfo] = useState(false);

  async function reload() {
    const next = await profileApi.get();
    setProfile(next);
    setError(null);
  }

  async function handleInfoSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setSavingInfo(true);
    setInfoError(null);
    try {
      const next = await profileApi.update({
        full_name: read(data, "full_name"),
        email: optional(data, "email"),
        location: optional(data, "location"),
        professional_summary: optional(data, "professional_summary"),
      });
      setProfile(next);
    } catch (cause) {
      setInfoError(
        cause instanceof Error ? cause.message : "Could not save your profile.",
      );
    } finally {
      setSavingInfo(false);
    }
  }

  if (error || !profile) {
    return (
      <div className="mx-auto w-full max-w-5xl px-4 py-8 md:py-12">
        <p className="text-sm text-destructive" role="alert">
          {error ?? "Could not load your profile."}
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto grid w-full max-w-5xl gap-6 px-4 py-8 md:py-12">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Candidate profile</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          This structured profile is the source of truth for later matching, gap
          analysis, and application materials.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Basic information</CardTitle>
          <CardDescription>
            Keep this current so later job matching has a reliable starting point.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleInfoSubmit} className="grid gap-4">
            <div className="grid gap-4 md:grid-cols-2">
              <FormField
                id="full_name"
                name="full_name"
                label="Full name"
                defaultValue={profile.full_name}
                placeholder="Ada Okonkwo"
              />
              <FormField
                id="email"
                name="email"
                label="Email"
                type="email"
                defaultValue={profile.email ?? ""}
                placeholder="ada@example.com"
              />
            </div>
            <FormField
              id="location"
              name="location"
              label="Location"
              defaultValue={profile.location ?? ""}
              placeholder="Nairobi"
            />
            <div className="grid gap-2">
              <Label htmlFor="professional_summary">Professional summary</Label>
              <Textarea
                id="professional_summary"
                name="professional_summary"
                rows={5}
                defaultValue={profile.professional_summary ?? ""}
                placeholder="What you do, the problems you solve, and the roles you are targeting."
              />
            </div>
            {infoError ? (
              <p className="text-sm text-destructive" role="alert">
                {infoError}
              </p>
            ) : null}
            <Button type="submit" disabled={savingInfo} className="w-fit">
              {savingInfo ? "Saving…" : "Save profile"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Evidence</CardTitle>
          <CardDescription>
            Education, work, skills, projects, and certifications that later
            matching can use as evidence.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-10">
          <ProfileSection
            title="Education"
            description="Degrees, courses, and formal study."
            emptyText="No education added yet."
            addLabel="Add education"
            idPrefix="education"
            items={profile.education}
            fields={[
              {
                name: "institution",
                label: "Institution",
                required: true,
                placeholder: "University of Nairobi",
              },
              { name: "degree", label: "Degree", placeholder: "BSc" },
              {
                name: "field_of_study",
                label: "Field of study",
                placeholder: "Computer Science",
              },
              { name: "start_date", label: "Start date", type: "date" },
              { name: "end_date", label: "End date", type: "date" },
            ]}
            valuesFor={(item) => ({
              institution: item.institution,
              degree: item.degree ?? "",
              field_of_study: item.field_of_study ?? "",
              start_date: item.start_date ?? "",
              end_date: item.end_date ?? "",
            })}
            renderSummary={(item) => (
              <>
                <p className="font-medium">{item.institution}</p>
                <p className="text-sm text-muted-foreground">
                  {[item.degree, item.field_of_study].filter(Boolean).join(" · ") ||
                    "Education"}
                  {formatRange(item.start_date, item.end_date)}
                </p>
              </>
            )}
            onCreate={async (form) => {
              await profileApi.addEducation(toEducation(form));
              await reload();
            }}
            onUpdate={async (id, form) => {
              await profileApi.updateEducation(id, toEducation(form));
              await reload();
            }}
            onDelete={async (id) => {
              await profileApi.deleteEducation(id);
              await reload();
            }}
          />

          <ProfileSection
            title="Experience"
            description="Roles you can point to as evidence."
            emptyText="No experience added yet."
            addLabel="Add experience"
            idPrefix="experience"
            items={profile.experience}
            fields={[
              {
                name: "company",
                label: "Company",
                required: true,
                placeholder: "Northwind Labs",
              },
              {
                name: "title",
                label: "Title",
                required: true,
                placeholder: "Backend Engineer",
              },
              { name: "start_date", label: "Start date", type: "date" },
              { name: "end_date", label: "End date", type: "date" },
              {
                name: "description",
                label: "Description",
                textarea: true,
                placeholder: "What you owned and the outcomes you produced.",
              },
            ]}
            valuesFor={(item) => ({
              company: item.company,
              title: item.title,
              start_date: item.start_date ?? "",
              end_date: item.end_date ?? "",
              description: item.description ?? "",
            })}
            renderSummary={(item) => (
              <>
                <p className="font-medium">
                  {item.title} · {item.company}
                </p>
                <p className="text-sm text-muted-foreground">
                  {formatRange(item.start_date, item.end_date, "") ||
                    "Current or unspecified dates"}
                </p>
                {item.description ? (
                  <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">
                    {item.description}
                  </p>
                ) : null}
              </>
            )}
            onCreate={async (form) => {
              await profileApi.addExperience(toExperience(form));
              await reload();
            }}
            onUpdate={async (id, form) => {
              await profileApi.updateExperience(id, toExperience(form));
              await reload();
            }}
            onDelete={async (id) => {
              await profileApi.deleteExperience(id);
              await reload();
            }}
          />

          <ProfileSection
            title="Skills"
            description="Named capabilities, grouped when useful."
            emptyText="No skills added yet."
            addLabel="Add skill"
            idPrefix="skill"
            items={profile.skills}
            fields={[
              {
                name: "name",
                label: "Skill",
                required: true,
                placeholder: "Python",
              },
              {
                name: "category",
                label: "Category",
                placeholder: "technical",
              },
            ]}
            valuesFor={(item) => ({
              name: item.name,
              category: item.category ?? "",
            })}
            renderSummary={(item) => (
              <>
                <p className="font-medium">{item.name}</p>
                <p className="text-sm text-muted-foreground">
                  {item.category || "Uncategorized"}
                </p>
              </>
            )}
            onCreate={async (form) => {
              await profileApi.addSkill(toSkill(form));
              await reload();
            }}
            onUpdate={async (id, form) => {
              await profileApi.updateSkill(id, toSkill(form));
              await reload();
            }}
            onDelete={async (id) => {
              await profileApi.deleteSkill(id);
              await reload();
            }}
          />

          <ProfileSection
            title="Projects"
            description="Work you can show, including personal projects."
            emptyText="No projects added yet."
            addLabel="Add project"
            idPrefix="project"
            items={profile.projects}
            fields={[
              {
                name: "name",
                label: "Project",
                required: true,
                placeholder: "Job OS",
              },
              {
                name: "description",
                label: "Description",
                textarea: true,
                placeholder: "What you built and why it is credible evidence.",
              },
              {
                name: "technologies",
                label: "Technologies",
                placeholder: "Python, FastAPI, React",
              },
            ]}
            valuesFor={(item) => ({
              name: item.name,
              description: item.description ?? "",
              technologies: item.technologies ?? "",
            })}
            renderSummary={(item) => (
              <>
                <p className="font-medium">{item.name}</p>
                {item.technologies ? (
                  <p className="text-sm text-muted-foreground">{item.technologies}</p>
                ) : null}
                {item.description ? (
                  <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">
                    {item.description}
                  </p>
                ) : null}
              </>
            )}
            onCreate={async (form) => {
              await profileApi.addProject(toProject(form));
              await reload();
            }}
            onUpdate={async (id, form) => {
              await profileApi.updateProject(id, toProject(form));
              await reload();
            }}
            onDelete={async (id) => {
              await profileApi.deleteProject(id);
              await reload();
            }}
          />

          <ProfileSection
            title="Certifications"
            description="Credentials that can support a requirement."
            emptyText="No certifications added yet."
            addLabel="Add certification"
            idPrefix="certification"
            items={profile.certifications}
            fields={[
              {
                name: "name",
                label: "Certification",
                required: true,
                placeholder: "AWS Certified Developer",
              },
              { name: "issuer", label: "Issuer", placeholder: "Amazon" },
              { name: "date", label: "Date", type: "date" },
            ]}
            valuesFor={(item) => ({
              name: item.name,
              issuer: item.issuer ?? "",
              date: item.date ?? "",
            })}
            renderSummary={(item) => (
              <>
                <p className="font-medium">{item.name}</p>
                <p className="text-sm text-muted-foreground">
                  {[item.issuer, item.date].filter(Boolean).join(" · ") ||
                    "Certification"}
                </p>
              </>
            )}
            onCreate={async (form) => {
              await profileApi.addCertification(toCertification(form));
              await reload();
            }}
            onUpdate={async (id, form) => {
              await profileApi.updateCertification(id, toCertification(form));
              await reload();
            }}
            onDelete={async (id) => {
              await profileApi.deleteCertification(id);
              await reload();
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}

function FormField({
  id,
  name,
  label,
  defaultValue,
  placeholder,
  type = "text",
}: {
  id: string;
  name: string;
  label: string;
  defaultValue: string;
  placeholder?: string;
  type?: string;
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        name={name}
        type={type}
        defaultValue={defaultValue}
        placeholder={placeholder}
      />
    </div>
  );
}

function read(data: FormData, name: string): string {
  return String(data.get(name) ?? "").trim();
}

function optional(data: FormData, name: string): string | null {
  return read(data, name) || null;
}

function toEducation(data: FormData): EducationWrite {
  return {
    institution: read(data, "institution"),
    degree: optional(data, "degree"),
    field_of_study: optional(data, "field_of_study"),
    start_date: optional(data, "start_date"),
    end_date: optional(data, "end_date"),
  };
}

function toExperience(data: FormData): ExperienceWrite {
  return {
    company: read(data, "company"),
    title: read(data, "title"),
    start_date: optional(data, "start_date"),
    end_date: optional(data, "end_date"),
    description: optional(data, "description"),
  };
}

function toSkill(data: FormData): SkillWrite {
  return {
    name: read(data, "name"),
    category: optional(data, "category"),
  };
}

function toProject(data: FormData): ProjectWrite {
  return {
    name: read(data, "name"),
    description: optional(data, "description"),
    technologies: optional(data, "technologies"),
  };
}

function toCertification(data: FormData): CertificationWrite {
  return {
    name: read(data, "name"),
    issuer: optional(data, "issuer"),
    date: optional(data, "date"),
  };
}

function formatRange(
  start: string | null,
  end: string | null,
  prefix = " · ",
): string {
  if (!start && !end) {
    return "";
  }
  return `${prefix}${start ?? "Unknown"} – ${end ?? "present"}`;
}
