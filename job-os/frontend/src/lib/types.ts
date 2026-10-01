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

export type RequirementCategory =
  | "skill"
  | "technology"
  | "experience"
  | "education"
  | "responsibility"
  | "certification"
  | "other";

export type RequirementImportance = "required" | "preferred";

export type Requirement = {
  id: string;
  job_id: string;
  name: string;
  category: RequirementCategory;
  importance: RequirementImportance;
  description: string | null;
  evidence_text: string | null;
};

export type RequirementWrite = {
  name: string;
  category?: RequirementCategory;
  importance?: RequirementImportance;
  description?: string | null;
  evidence_text?: string | null;
};

export type ExtractRequirementsResponse = {
  requirements: Requirement[];
  created_count: number;
  skipped_duplicate_count: number;
};

export type MatchClassification = "STRONG_EVIDENCE" | "TRANSFERABLE" | "GAP";

export type RequirementMatch = {
  job_id: string;
  requirement_id: string;
  requirement_name: string;
  category: RequirementCategory;
  importance: RequirementImportance;
  classification: MatchClassification;
  evidence: string[];
};

export type JobAnalysis = {
  job: Job;
  requirements: Requirement[];
  strong_evidence: RequirementMatch[];
  transferable: RequirementMatch[];
  gaps: RequirementMatch[];
  required_gaps: RequirementMatch[];
  preferred_gaps: RequirementMatch[];
};

export type Candidate = {
  id: string;
  full_name: string;
  email: string | null;
  location: string | null;
  professional_summary: string | null;
  education: Education[];
  experience: Experience[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
};

export type CandidateUpdate = {
  full_name: string;
  email?: string | null;
  location?: string | null;
  professional_summary?: string | null;
};

export type Education = {
  id: string;
  candidate_id: string;
  institution: string;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
};

export type EducationWrite = {
  institution: string;
  degree?: string | null;
  field_of_study?: string | null;
  start_date?: string | null;
  end_date?: string | null;
};

export type Experience = {
  id: string;
  candidate_id: string;
  company: string;
  title: string;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
};

export type ExperienceWrite = {
  company: string;
  title: string;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
};

export type Skill = {
  id: string;
  candidate_id: string;
  name: string;
  category: string | null;
};

export type SkillWrite = {
  name: string;
  category?: string | null;
};

export type Project = {
  id: string;
  candidate_id: string;
  name: string;
  description: string | null;
  technologies: string | null;
};

export type ProjectWrite = {
  name: string;
  description?: string | null;
  technologies?: string | null;
};

export type Certification = {
  id: string;
  candidate_id: string;
  name: string;
  issuer: string | null;
  date: string | null;
};

export type CertificationWrite = {
  name: string;
  issuer?: string | null;
  date?: string | null;
};

