import { ProfilePage } from "@/components/profile-page";
import { profileApi } from "@/lib/api";
import type { Candidate } from "@/lib/types";

export default async function ProfileRoute() {
  let initialProfile: Candidate | null = null;
  let initialError: string | null = null;

  try {
    initialProfile = await profileApi.get();
  } catch (cause) {
    initialError =
      cause instanceof Error ? cause.message : "Could not load your profile.";
  }

  return (
    <ProfilePage initialProfile={initialProfile} initialError={initialError} />
  );
}
