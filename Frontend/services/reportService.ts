import { type MaintenanceReportQuery, type MaintenanceReportResponse } from "@/models/report";

import { serverAuthHeaders } from "@/lib/auth-server";
import { getPyApiBaseUrl } from "@/lib/py-api";

export async function getMaintenanceReport(
  query: MaintenanceReportQuery
): Promise<MaintenanceReportResponse | null> {
  let py: string;
  try {
    py = getPyApiBaseUrl();
  } catch {
    return null;
  }

  try {
    const url = new URL(`${py}/api/reports/maintenance`);
    if (query.from) url.searchParams.set("from", query.from);
    if (query.to) url.searchParams.set("to", query.to);
    if (query.maintenance_type && query.maintenance_type !== "Ambas") {
      url.searchParams.set("maintenance_type", query.maintenance_type);
    }

    const res = await fetch(url.toString(), { cache: "no-store", headers: serverAuthHeaders() });
    if (!res.ok) return null;
    const data = await res.json();
    return {
      total: Number(data.total ?? 0),
      items: Array.isArray(data.items)
        ? data.items.map((it: any) => ({
            computer_id: Number(it.computer_id),
            computer_name: String(it.computer_name ?? ""),
            patrimonio: it.patrimonio != null ? String(it.patrimonio) : null,
            technician: it.technician != null ? String(it.technician) : null,
            maintenance_type: it.maintenance_type === "Corretiva" ? "Corretiva" : "Preventiva",
            performed_at: String(it.performed_at),
          }))
        : [],
    };
  } catch {
    return null;
  }
}
