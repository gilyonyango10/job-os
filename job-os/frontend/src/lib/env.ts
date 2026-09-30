export function getApiUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:48217";
  return url.replace(/\/$/, "");
}
