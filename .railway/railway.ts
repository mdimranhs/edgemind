import { defineRailway, preserve, project, service } from "railway/iac";

export default defineRailway(() => {
  const api = service("edgemind", {
    healthcheck: "/health",
    healthcheckTimeout: 300,
    env: {
      LLM_PROVIDER: "hf_api",
      HF_MODEL: "Qwen/Qwen3.8-27B",
      HF_TOKEN: preserve(),
      DEBUG: "false",
      WEB_SEARCH_ENABLED: "true",
      RAG_LOCAL_FILES_ONLY: "true",
    },
  });

  return project("edgemind", {
    resources: [api],
  });
});
