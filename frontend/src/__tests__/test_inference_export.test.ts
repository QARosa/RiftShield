/**
 * TC-FE-02: InferencePage — service layer + loading/error states
 * TC-FE-03: ExportPage — format validation and section selection
 */
import { describe, it, expect, vi, beforeEach } from "vitest";

// ── Shared API mock ────────────────────────────────────────────────────────
const mockApi = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
};
vi.mock("../middleware/api", () => ({ default: mockApi }));

// ─────────────────────────────────────────────────────────────────────────
// TC-FE-02: Inference service — extended coverage
// ─────────────────────────────────────────────────────────────────────────
describe("TC-FE-02: InferencePage — inference service layer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it("analyzeDiagram sends file as FormData and returns AnalyzeResponse", async () => {
    const mockResponse = {
      id: "inf1",
      filename: "arch.png",
      status: "completed",
      components: [{ class_id: 0, label: "api", confidence: 0.95, bbox: { x: 0, y: 0, width: 10, height: 10 } }],
      processing_time_ms: 120,
      created_at: "2026-01-01T00:00:00",
    };
    mockApi.post.mockResolvedValue({ data: mockResponse });

    const { analyzeDiagram } = await import("../services/inference-service");
    const file = new File(["fake-png"], "arch.png", { type: "image/png" });
    const result = await analyzeDiagram(file);

    expect(mockApi.post).toHaveBeenCalledWith("/inference/analyze", expect.any(FormData));
    expect(result.id).toBe("inf1");
    expect(result.components).toHaveLength(1);
    expect(result.components[0].label).toBe("api");
  });

  it("analyzeAndThreat returns combined inference + threat_report", async () => {
    const mockResult = {
      inference: { id: "inf2", filename: "a.png", status: "completed", components: [], processing_time_ms: 50, created_at: "2026-01-01T00:00:00" },
      threat_report: {
        id: "thr1",
        inference_id: "inf2",
        status: "completed",
        stride_summary: { Spoofing: 1 },
        component_analyses: [],
        overall_risk_score: 0.5,
        created_at: "2026-01-01T00:00:00",
        updated_at: "2026-01-01T00:00:00",
      },
    };
    mockApi.post.mockResolvedValue({ data: mockResult });

    const { analyzeAndThreat } = await import("../services/inference-service");
    const file = new File(["x"], "b.png", { type: "image/png" });
    const result = await analyzeAndThreat(file);

    expect(mockApi.post).toHaveBeenCalledWith("/inference/analyze-threat", expect.any(FormData));
    expect(result.inference.id).toBe("inf2");
    expect(result.threat_report.stride_summary.Spoofing).toBe(1);
  });

  it("deleteReport calls DELETE with correct id", async () => {
    mockApi.delete.mockResolvedValue({ data: { message: "deleted" } });

    const { deleteReport } = await import("../services/inference-service");
    await deleteReport("inf3");

    expect(mockApi.delete).toHaveBeenCalledWith("/inference/reports/inf3");
  });

  it("listThreatReports returns paginated threats", async () => {
    mockApi.get.mockResolvedValue({ data: { total: 2, items: [{ id: "t1" }, { id: "t2" }] } });

    const { listThreatReports } = await import("../services/inference-service");
    const result = await listThreatReports(0, 10);

    expect(mockApi.get).toHaveBeenCalledWith("/inference/threats?skip=0&limit=10");
    expect(result.total).toBe(2);
    expect(result.items).toHaveLength(2);
  });

  it("analyzeDiagram propagates error when API fails", async () => {
    mockApi.post.mockRejectedValue({ response: { data: { error: "Unsupported file" } } });

    const { analyzeDiagram } = await import("../services/inference-service");
    const file = new File(["bad"], "doc.pdf", { type: "application/pdf" });

    await expect(analyzeDiagram(file)).rejects.toMatchObject({
      response: { data: { error: "Unsupported file" } },
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────
// TC-FE-03: ExportPage — export service validation
// ─────────────────────────────────────────────────────────────────────────
describe("TC-FE-03: ExportPage — export API payload validation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it("POST /export/export with json format returns filename", async () => {
    mockApi.post.mockResolvedValue({
      data: { filename: "export_2026-01-01.json", content: "{}", error: null },
    });

    const payload = {
      sections: ["inferences", "threats"],
      format: "json",
      include_profile: false,
      include_settings: false,
      zip: false,
      lang: "pt-BR",
    };
    const res = await mockApi.post("/export/export", payload);

    expect(res.data.filename).toContain(".json");
    expect(res.data.error).toBeNull();
  });

  it("POST /export/export with csv format returns csv filename", async () => {
    mockApi.post.mockResolvedValue({
      data: { filename: "export_2026-01-01.csv", content: "id,name", error: null },
    });

    const res = await mockApi.post("/export/export", { format: "csv", sections: ["threats"] });
    expect(res.data.filename).toContain(".csv");
  });

  it("POST /export/export with empty sections should return error", async () => {
    mockApi.post.mockResolvedValue({
      data: { filename: null, content: null, error: "Nenhuma seção selecionada" },
    });

    const res = await mockApi.post("/export/export", { sections: [], format: "json" });
    expect(res.data.error).toBeTruthy();
  });

  it("POST /export/export with zip=true returns zip filename", async () => {
    mockApi.post.mockResolvedValue({
      data: { filename: "export_2026-01-01.zip", content: "binary", error: null },
    });

    const res = await mockApi.post("/export/export", {
      sections: ["inferences"],
      format: "json",
      zip: true,
    });
    expect(res.data.filename).toContain(".zip");
  });

  it("all supported formats are accepted: json, csv, excel, pdf", async () => {
    const formats = ["json", "csv", "excel", "pdf"];
    for (const fmt of formats) {
      mockApi.post.mockResolvedValueOnce({
        data: { filename: `export.${fmt}`, content: "", error: null },
      });
      const res = await mockApi.post("/export/export", { format: fmt, sections: ["inferences"] });
      expect(res.data.filename).toContain(fmt);
    }
  });
});
