export type HttpMethod = "GET" | "POST";

export type ApiEndpoint = {
  label: string;
  method: HttpMethod;
  path: string;
  sampleBody?: Record<string, unknown>;
};

export type ApiGroup = {
  key: string;
  title: string;
  description: string;
  endpoints: ApiEndpoint[];
};
