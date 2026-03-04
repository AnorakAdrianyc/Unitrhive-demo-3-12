export async function requestJson(
  path: string,
  method: "GET" | "POST",
  body?: Record<string, unknown>
): Promise<unknown> {
  const response = await fetch(path, {
    method,
    headers: {
      "Content-Type": "application/json"
    },
    body: method === "POST" ? JSON.stringify(body ?? {}) : undefined
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(
      typeof payload?.detail === "string"
        ? payload.detail
        : `Request failed with ${response.status}`
    );
  }

  return payload;
}
