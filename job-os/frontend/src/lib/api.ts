import { getApiUrl } from "@/lib/env";
import type {
  Candidate,
  CandidateUpdate,
  Certification,
  CertificationWrite,
  Education,
  EducationWrite,
  Experience,
  ExperienceWrite,
  Job,
  JobCreate,
  Project,
  ProjectWrite,
  Skill,
  SkillWrite,
} from "@/lib/types";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${getApiUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    throw new ApiError(
      "Could not reach the Job OS API. Confirm the backend is running.",
      0,
    );
  }

  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof body.detail === "string"
    ) {
      return body.detail;
    }
  } catch {
    // Fall through to the status-based message.
  }
  return `Request failed (${response.status})`;
}

export const jobsApi = {
  list(): Promise<Job[]> {
    return request<Job[]>("/jobs");
  },
  get(jobId: string): Promise<Job> {
    return request<Job>(`/jobs/${jobId}`);
  },
  create(payload: JobCreate): Promise<Job> {
    return request<Job>("/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};

export const profileApi = {
  get(): Promise<Candidate> {
    return request<Candidate>("/profile");
  },
  update(payload: CandidateUpdate): Promise<Candidate> {
    return request<Candidate>("/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  addEducation(payload: EducationWrite): Promise<Education> {
    return request<Education>("/profile/education", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  updateEducation(id: string, payload: EducationWrite): Promise<Education> {
    return request<Education>(`/profile/education/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  deleteEducation(id: string): Promise<void> {
    return request<void>(`/profile/education/${id}`, { method: "DELETE" });
  },
  addExperience(payload: ExperienceWrite): Promise<Experience> {
    return request<Experience>("/profile/experience", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  updateExperience(id: string, payload: ExperienceWrite): Promise<Experience> {
    return request<Experience>(`/profile/experience/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  deleteExperience(id: string): Promise<void> {
    return request<void>(`/profile/experience/${id}`, { method: "DELETE" });
  },
  addSkill(payload: SkillWrite): Promise<Skill> {
    return request<Skill>("/profile/skills", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  updateSkill(id: string, payload: SkillWrite): Promise<Skill> {
    return request<Skill>(`/profile/skills/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  deleteSkill(id: string): Promise<void> {
    return request<void>(`/profile/skills/${id}`, { method: "DELETE" });
  },
  addProject(payload: ProjectWrite): Promise<Project> {
    return request<Project>("/profile/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  updateProject(id: string, payload: ProjectWrite): Promise<Project> {
    return request<Project>(`/profile/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  deleteProject(id: string): Promise<void> {
    return request<void>(`/profile/projects/${id}`, { method: "DELETE" });
  },
  addCertification(payload: CertificationWrite): Promise<Certification> {
    return request<Certification>("/profile/certifications", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  updateCertification(
    id: string,
    payload: CertificationWrite,
  ): Promise<Certification> {
    return request<Certification>(`/profile/certifications/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  deleteCertification(id: string): Promise<void> {
    return request<void>(`/profile/certifications/${id}`, { method: "DELETE" });
  },
};

