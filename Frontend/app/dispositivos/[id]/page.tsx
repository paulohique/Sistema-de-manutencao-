import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function DeviceDetailPage({ params }: Props) {
  const { id } = await params;

  // TODO: Buscar detalhes do dispositivo do backend
  // const device = await getDeviceDetail(id);
  // Por enquanto mostra estrutura vazia aguardando implementação do backend

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Button asChild variant="outline" size="sm">
              <Link href="/">
                <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Voltar
              </Link>
            </Button>
            <h2 className="text-2xl font-bold text-gray-900">Detalhes do Dispositivo</h2>
          </div>
          <p className="mt-2 text-sm text-gray-600">ID: {id}</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white shadow-lg">
        <div className="border-b border-gray-200 p-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Nome</p>
              <p className="mt-1 text-sm font-medium text-gray-900">—</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Serial</p>
              <p className="mt-1 text-sm font-medium text-gray-900">—</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Localização</p>
              <p className="mt-1 text-sm font-medium text-gray-900">—</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Status</p>
              <Badge variant="neutral" className="mt-1">Aguardando Backend</Badge>
            </div>
          </div>
        </div>

        <div className="p-6">
          <Tabs defaultValue="components" className="w-full">
            <TabsList className="mb-6">
              <TabsTrigger value="components">Componentes</TabsTrigger>
              <TabsTrigger value="notes">Notas</TabsTrigger>
              <TabsTrigger value="maintenance">Histórico de Manutenção</TabsTrigger>
            </TabsList>

            <TabsContent value="components" className="space-y-4">
              <div className="rounded-lg border border-gray-200 p-8 text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <h3 className="mt-4 text-sm font-semibold text-gray-900">Componentes do Dispositivo</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Os componentes (CPU, RAM, HD, etc.) serão carregados do GLPI via backend.
                </p>
                <p className="mt-1 text-xs text-gray-400">
                  Endpoint: <code className="rounded bg-gray-100 px-2 py-1">GET /api/devices/{id}/components</code>
                </p>
              </div>
            </TabsContent>

            <TabsContent value="notes" className="space-y-4">
              <div className="flex justify-end">
                <Button variant="primary">
                  <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Adicionar Nota
                </Button>
              </div>
              <div className="rounded-lg border border-gray-200 p-8 text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <h3 className="mt-4 text-sm font-semibold text-gray-900">Notas do Dispositivo</h3>
                <p className="mt-2 text-sm text-gray-500">
                  Aqui você poderá adicionar e visualizar notas sobre este dispositivo.
                </p>
                <p className="mt-1 text-xs text-gray-400">
                  Endpoints: <code className="rounded bg-gray-100 px-2 py-1">GET/POST /api/devices/{id}/notes</code>
                </p>
              </div>
            </TabsContent>

            <TabsContent value="maintenance" className="space-y-4">
              <div className="rounded-lg border border-gray-200 p-8 text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <h3 className="mt-4 text-sm font-semibold text-gray-900">Histórico de Manutenção</h3>
                <p className="mt-2 text-sm text-gray-500">
                  O histórico completo de manutenções (preventivas e corretivas) será carregado do backend.
                </p>
                <p className="mt-1 text-xs text-gray-400">
                  Endpoint: <code className="rounded bg-gray-100 px-2 py-1">GET /api/devices/{id}/maintenance</code>
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <div className="flex gap-3">
          <svg className="h-5 w-5 flex-shrink-0 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-blue-900">Backend Necessário</h4>
            <p className="mt-1 text-sm text-blue-700">
              Esta página está pronta para consumir os dados do backend. Implemente os seguintes endpoints:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-blue-600">
              <li>• <code className="font-mono">GET /api/devices/{id}</code> - Detalhes do dispositivo do GLPI</li>
              <li>• <code className="font-mono">GET /api/devices/{id}/components</code> - Componentes de hardware</li>
              <li>• <code className="font-mono">GET /api/devices/{id}/notes</code> - Listar notas</li>
              <li>• <code className="font-mono">POST /api/devices/{id}/notes</code> - Adicionar nota</li>
              <li>• <code className="font-mono">GET /api/devices/{id}/maintenance</code> - Histórico de manutenção</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
