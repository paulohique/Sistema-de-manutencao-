"use client";

import { useMemo } from "react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { type MaintenanceReportRow, type MaintenanceTypeFilter } from "@/models/report";

function fmtDate(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

export function ReportClient({
  rows,
  total,
  filters,
}: {
  rows: MaintenanceReportRow[];
  total: number;
  filters: { from: string; to: string; maintenance_type: MaintenanceTypeFilter };
}) {
  const subtitle = useMemo(() => {
    const parts: string[] = [];
    if (filters.maintenance_type) parts.push(`Tipo: ${filters.maintenance_type}`);
    if (filters.from) parts.push(`De: ${filters.from}`);
    if (filters.to) parts.push(`Até: ${filters.to}`);
    return parts.join(" | ");
  }, [filters]);

  const onDownloadPdf = () => {
    const doc = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
    doc.setFontSize(14);
    doc.text("Relatório de Manutenções", 40, 40);
    doc.setFontSize(10);
    if (subtitle) doc.text(subtitle, 40, 58);

    const body = rows.map((r) => [
      r.computer_name,
      r.patrimonio ?? "—",
      r.technician ?? "—",
      r.maintenance_type,
      fmtDate(r.performed_at),
    ]);

    autoTable(doc, {
      startY: 75,
      head: [["Computador", "Patrimônio", "Técnico", "Tipo", "Data"]],
      body,
      styles: { fontSize: 9, cellPadding: 4 },
      headStyles: { fillColor: [17, 24, 39] },
      theme: "grid",
    });

    const fileName = `relatorio-manutencoes-${filters.maintenance_type || "todas"}.pdf`;
    doc.save(fileName);
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-lg">
      <div className="border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white p-6">
        <h3 className="text-lg font-bold text-gray-900">Relatório</h3>
        <p className="mt-1 text-sm text-gray-600">
          Filtre por tipo e período. Exporta em PDF com computador, técnico, tipo e data.
        </p>

        <form className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-4" action="/" method="get">
          <input type="hidden" name="tab" value="relatorio" />

          <div>
            <label className="text-xs text-gray-600">Tipo</label>
            <select
              name="maintenance_type"
              defaultValue={filters.maintenance_type}
              className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="Ambas">Ambas</option>
              <option value="Preventiva">Preventiva</option>
              <option value="Corretiva">Corretiva</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-gray-600">De</label>
            <Input className="mt-1" type="date" name="from" defaultValue={filters.from} />
          </div>

          <div>
            <label className="text-xs text-gray-600">Até</label>
            <Input className="mt-1" type="date" name="to" defaultValue={filters.to} />
          </div>

          <div className="flex items-end gap-2">
            <Button variant="primary" type="submit" className="w-full">Gerar</Button>
            <Button variant="outline" type="button" onClick={onDownloadPdf} disabled={rows.length === 0}>
              Salvar PDF
            </Button>
          </div>
        </form>
      </div>

      <div className="p-6">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-muted-foreground">Total de registros: {total}</p>
        </div>

        <div className="mt-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Computador</TableHead>
                <TableHead>Patrimônio</TableHead>
                <TableHead>Técnico</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Data</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((r, idx) => (
                <TableRow key={`${r.computer_id}-${r.performed_at}-${idx}`}>
                  <TableCell className="font-semibold">{r.computer_name}</TableCell>
                  <TableCell>{r.patrimonio ?? "—"}</TableCell>
                  <TableCell>{r.technician ?? "—"}</TableCell>
                  <TableCell>{r.maintenance_type}</TableCell>
                  <TableCell>{fmtDate(r.performed_at)}</TableCell>
                </TableRow>
              ))}

              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-12 text-gray-500">
                    Nenhum registro encontrado para esse filtro.
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
