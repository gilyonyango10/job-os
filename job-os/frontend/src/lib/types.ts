export type JobStatus =
  | "DISCOVERED"
  | "QUALIFIED"
  | "PREPARING"
  | "READY"
  | "APPLIED"
  | "FOLLOW_UP"
  | "INTERVIEW"
  | "OUTCOME";

export type Job = {
  id: string;
  title: string;
  company: string;
  location: string | null;
  description: string;
  source: string;
  source_url: string | null;
  status: JobStatus;
  created_at: string;
};

export type JobCreate = {
  title: string;
  company: string;
  location?: string | null;
  description: string;
  source?: string;
  source_url?: string | null;
};
