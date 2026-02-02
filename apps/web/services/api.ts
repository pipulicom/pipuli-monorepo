
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pipuli-api-dev-553244616231.us-central1.run.app";
const PROJ_ID = process.env.NEXT_PUBLIC_PROJECT_ID || "pipuli-dev";

export interface Equipment {
    id?: string;
    name: string;
    brand: string;
    type: string;
}

export const EquipmentService = {
    async list(): Promise<Equipment[]> {
        const url = `${API_URL}/api/${PROJ_ID}/equipments`;

        try {
            const res = await fetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": "dev-key"
                }
            });

            if (!res.ok) {
                console.error(`[EquipmentService] Fetch failed: ${res.status} ${res.statusText}`);
                throw new Error("Failed to fetch");
            }
            const json = await res.json();
            return json.data;
        } catch (error) {
            console.error("[EquipmentService] Network error:", error);
            throw error;
        }
    },

    async create(data: Equipment): Promise<Equipment> {
        const url = `${API_URL}/api/${PROJ_ID}/equipments`;

        try {
            const res = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": "dev-key"
                },
                body: JSON.stringify(data)
            });

            if (!res.ok) {
                console.error(`[EquipmentService] Create failed: ${res.status}`);
                const errText = await res.text();
                throw new Error(errText || "Failed to create");
            }
            const json = await res.json();
            return json.data;
        } catch (error) {
            console.error("[EquipmentService] Network error:", error);
            throw error;
        }
    }
};
