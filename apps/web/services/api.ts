
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";
const PROJ_ID = process.env.NEXT_PUBLIC_PROJECT_ID || "pipuli-dev";
// API Key injected at build time (pulled from Secret Manager)
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

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
                    "X-API-Key": API_KEY
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
                    "X-API-Key": API_KEY
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
