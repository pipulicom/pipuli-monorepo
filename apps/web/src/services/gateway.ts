import { api } from "./api";

export const gatewayService = {
    /**
     * Execute a generic workflow on the backend.
     * @param projectId - The project identifier
     * @param flowName - The workflow name to execute
     * @param payload - Data to send
     */
    executeWorkflow: async <T = unknown>(
        projectId: string,
        flowName: string,
        payload: Record<string, unknown>
    ): Promise<T> => {
        return api.post<T>(`/${projectId}/${flowName}`, payload);
    },
};
