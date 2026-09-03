/**
 * Core API Client for ReturnSentinel AI Backend
 * Centralizes base URL configuration, request options, JSON serialization, and typed error handling.
 */

export class ApiClientError extends Error {
  status: number;
  statusText: string;
  data?: any;

  constructor(message: string, status: number, statusText: string, data?: any) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.statusText = statusText;
    this.data = data;
  }
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${API_BASE_URL}${normalizedPath}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }
  if (options.body && typeof options.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err: any) {
    throw new ApiClientError(
      `Network connection failure: unable to reach ReturnSentinel API at ${url}. ${err.message || ""}`,
      0,
      "NetworkError"
    );
  }

  if (!response.ok) {
    let errorData: any = null;
    let errorMessage = `API request failed with status ${response.status} (${response.statusText})`;
    try {
      errorData = await response.json();
      if (errorData?.detail) {
        errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      try {
        errorMessage = await response.text();
      } catch {
        // use default error message
      }
    }

    throw new ApiClientError(
      errorMessage,
      response.status,
      response.statusText,
      errorData
    );
  }

  // Parse JSON response
  try {
    return (await response.json()) as T;
  } catch (err: any) {
    throw new ApiClientError(
      `Failed to parse JSON response from server: ${err.message || ""}`,
      response.status,
      response.statusText
    );
  }
}
