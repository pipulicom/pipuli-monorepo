// import { gatewayService } from "./gateway"; // Unused
import { api } from "./api";

// Assuming equipments is a workflow in project 'pipuli-asset-mngmt' or similar
// But the legacy code used `${API_URL}/api/${PROJ_ID}/equipments` which looks like a direct route or a workflow routed via gateway.
// Given the gateway router in `apps/api/gateway/router.py` maps `/{project_id}/{flow_name}`, 
// the legacy code `${API_URL}/api/${PROJ_ID}/equipments` maps to project=`${PROJ_ID}` and flow=`equipments`.
// So we can use gatewayService.executeWorkflow.

const PROJ_ID = process.env.NEXT_PUBLIC_PROJECT_ID || "pipuli-dev";

export interface Equipment {
    id?: string;
    name: string;
    brand: string;
    type: string;
}

export const EquipmentService = {
    list: async (): Promise<Equipment[]> => {
        // GET request to gateway is supported if body has no data, 
        // but api.ts fetcher handles the method.
        // GatewayService.executeWorkflow uses api.post by default.
        // We might need a GET method in GatewayService or just use api.get directly for this REST-like mapping.

        // However, the new gateway logic expects POST usually for workflows, 
        // but the router supports GET.
        // Let's use api.get directly to minimize friction, using the exact same path math logic.

        // URL: /api/{PROJ_ID}/equipments
        // Our api.ts adds /api prefix if we configured API_URL to include /api? 
        // In api.ts: `const API_URL = ... || "http://.../api";` 
        // And `url = ... ${API_URL}${endpoint}`
        // So endpoint should be `/${PROJ_ID}/equipments`.

        const response = await api.get<{ data: Equipment[] }>(`/${PROJ_ID}/equipments`);
        return response.data;
    },

    create: async (data: Equipment): Promise<Equipment> => {
        const response = await api.post<{ data: Equipment }>(`/${PROJ_ID}/equipments`, data);
        return response.data;
    }
};
