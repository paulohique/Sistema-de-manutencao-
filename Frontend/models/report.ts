export type MaintenanceTypeFilter = "Preventiva" | "Corretiva" | "Ambas";

export type MaintenanceReportRow = {
  computer_id: number;
  computer_name: string;
  patrimonio: string | null;
  technician: string | null;
  maintenance_type: "Preventiva" | "Corretiva";
  performed_at: string; // ISO
};

export type MaintenanceReportResponse = {
  items: MaintenanceReportRow[];
  total: number;
};

export type MaintenanceReportQuery = {
  from?: string;
  to?: string;
  maintenance_type?: MaintenanceTypeFilter;
};
