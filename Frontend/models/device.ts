export type MaintenanceStatus = "Em Dia" | "Atrasada" | "Pendente";

export type DeviceRow = {
  id: string;
  device_name: string;
  maintenance_status: MaintenanceStatus;
  last_maintenance_date: string | null;
  next_maintenance_date: string | null;
};

export type DevicesQuery = {
  tab: "dispositivos" | "preventiva" | "corretiva";
  q: string;
  page: number;
  pageSize: number;
};

export type DevicesPage = {
  items: DeviceRow[];
  page: number;
  pageSize: number;
  total: number;
};

// Tipos para o detalhe do dispositivo (visualizar)
export type DeviceComponent = {
  type: string;
  name: string;
  manufacturer?: string;
  model?: string;
  serial?: string;
  [key: string]: any;
};

export type DeviceNote = {
  id: string;
  date: string;
  author: string;
  content: string;
};

export type DeviceDetail = {
  id: string;
  name: string;
  serial?: string;
  location?: string;
  department?: string;
  status?: string;
  components: DeviceComponent[];
  notes: DeviceNote[];
  maintenance_history: Array<{
    id: string;
    type: "Preventiva" | "Corretiva";
    date: string;
    description: string;
    technician?: string;
  }>;
};
