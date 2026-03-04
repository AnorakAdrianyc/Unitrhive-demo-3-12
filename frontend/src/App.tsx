import { useMemo, useState } from "react";
import { apiGroups, callEndpoint } from "./lib/api";
import type { ApiEndpoint } from "./types";

function EndpointCard({
  endpoint,
  onRun,
  running
}: {
  endpoint: ApiEndpoint;
  onRun: (payloadText: string) => void;
  running: boolean;
}) {
  const initialBody = useMemo(
    () => JSON.stringify(endpoint.sampleBody ?? {}, null, 2),
    [endpoint.sampleBody]
  );
  const [payloadText, setPayloadText] = useState<string>(initialBody);

  return (
    <div className="rounded-xl border border-blue-100 bg-white p-4 shadow-card">
      <div className="mb-2 flex items-center justify-between gap-3">
        <h4 className="text-sm font-semibold text-slate-800">{endpoint.label}</h4>
        <span
          className={`rounded-full px-2 py-1 text-xs font-semibold ${
            endpoint.method === "GET"
              ? "bg-blue-100 text-blue-700"
              : "bg-indigo-100 text-indigo-700"
          }`}
        >
          {endpoint.method}
        </span>
      </div>

      <p className="rounded-md bg-slate-50 px-3 py-2 text-xs text-slate-700">
        {endpoint.path}
      </p>

      {endpoint.method === "POST" ? (
        <textarea
          className="mt-3 h-36 w-full rounded-md border border-blue-100 bg-white p-2 font-mono text-xs"
          value={payloadText}
          onChange={(event) => setPayloadText(event.target.value)}
        />
      ) : null}

      <button
        className="mt-3 w-full rounded-md bg-uni-primary px-3 py-2 text-sm font-semibold text-white transition hover:bg-uni-accent disabled:cursor-not-allowed disabled:opacity-60"
        onClick={() => onRun(payloadText)}
        disabled={running}
      >
        {running ? "Running..." : "Run endpoint"}
      </button>
    </div>
  );
}

export default function App() {
  const [activeGroup, setActiveGroup] = useState<string>(apiGroups[0].key);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [status, setStatus] = useState<string>("Ready");
  const [responseJson, setResponseJson] = useState<string>("{}");

  const group = apiGroups.find((item) => item.key === activeGroup) ?? apiGroups[0];

  async function runEndpoint(endpoint: ApiEndpoint, payloadText: string): Promise<void> {
    setIsRunning(true);
    setStatus(`Calling ${endpoint.path} ...`);
    try {
      const body =
        endpoint.method === "POST" && payloadText.trim()
          ? (JSON.parse(payloadText) as Record<string, unknown>)
          : undefined;

      const result = await callEndpoint(endpoint.method, endpoint.path, body);
      setResponseJson(JSON.stringify(result, null, 2));
      setStatus(`Success: ${endpoint.path}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setStatus(`Error: ${message}`);
      setResponseJson(JSON.stringify({ error: message }, null, 2));
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <main className="min-h-screen bg-uni-neutral">
      <div className="mx-auto grid max-w-7xl gap-5 px-4 py-5 lg:grid-cols-[300px_1fr_1fr]">
        <section className="rounded-2xl bg-white p-4 shadow-card">
          <h1 className="text-2xl font-bold text-uni-primary">UniThrive Demo</h1>
          <p className="mt-2 text-sm text-slate-600">
            Full-stack frontend modules linked to each backend router file.
          </p>
          <div className="mt-4 space-y-2">
            {apiGroups.map((item) => (
              <button
                key={item.key}
                className={`w-full rounded-lg px-3 py-2 text-left text-sm font-medium transition ${
                  activeGroup === item.key
                    ? "bg-uni-primary text-white"
                    : "bg-uni-neutral text-slate-700 hover:bg-blue-100"
                }`}
                onClick={() => setActiveGroup(item.key)}
              >
                {item.title}
              </button>
            ))}
          </div>
          <p className="mt-4 rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
            Color palette: #1e3a8a, #3b82f6, #60a5fa, #ffffff, #f3f4f6
          </p>
        </section>

        <section className="rounded-2xl bg-white p-4 shadow-card">
          <h2 className="text-xl font-semibold text-uni-primary">{group.title}</h2>
          <p className="mt-1 text-sm text-slate-600">{group.description}</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {group.endpoints.map((endpoint) => (
              <EndpointCard
                key={`${endpoint.method}-${endpoint.path}`}
                endpoint={endpoint}
                running={isRunning}
                onRun={(payloadText) => runEndpoint(endpoint, payloadText)}
              />
            ))}
          </div>
        </section>

        <section className="rounded-2xl bg-white p-4 shadow-card">
          <h3 className="text-lg font-semibold text-uni-primary">Live API Response</h3>
          <p
            className={`mt-2 rounded-md px-3 py-2 text-sm ${
              status.startsWith("Error")
                ? "bg-red-50 text-red-700"
                : "bg-green-50 text-green-700"
            }`}
          >
            {status}
          </p>
          <pre className="mt-3 max-h-[78vh] overflow-auto rounded-lg bg-slate-900 p-3 text-xs text-slate-100">
            {responseJson}
          </pre>
        </section>
      </div>
    </main>
  );
}
