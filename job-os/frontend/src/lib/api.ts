import { getApiUrl } from "@/lib/env";
import type { Job, JobCreate } from "@/lib/types";

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
