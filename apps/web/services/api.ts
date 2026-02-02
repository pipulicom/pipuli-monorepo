
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
        const res = await fetch(`${API_URL}/api/${PROJ_ID}/equipments`, {
            method: "POST", // Gateway uses POST for body args usually, but our workflow handles GET method in body or via POST?
            // Wait, my handler uses `request.method` injected into body.
            // If I send a GET request to Gateway, `request.method` is GET.
            // But Gateway `process_request` allows GET.
            // "If request.method == POST: body = await request.json()"
            // "Merge Query Parameters into body"
            // So if I send GET, body is query params.
            // The workflow checks `data.get("_method")`.
            // `router.py` injects `_method`.
            // So if I send GET, `_method` is GET.

            headers: {
                "Content-Type": "application/json",
                "X-API-Key": "dev-key" // Mock Key for local, or handle auth
            }
        });

        if (!res.ok) throw new Error("Failed to fetch");
        const json = await res.json();
        return json.data;
    },

    async create(data: Equipment): Promise<Equipment> {
        const res = await fetch(`${API_URL}/api/${PROJ_ID}/equipments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": "dev-key"
            },
            body: JSON.stringify(data)
        });

        if (!res.ok) throw new Error("Failed to create");
        const json = await res.json();
        return json.data;
    }
};
