const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

type Headers = Record<string, string>;

interface RequestOptions extends RequestInit {
    headers?: Headers;
}

export const api = {
    get: async <T>(url: string, options: RequestOptions = {}): Promise<T> => {
        return fetcher<T>(url, {
            ...options,
            method: 'GET',
            headers: {
                'X-API-Key': API_KEY,
                ...options.headers
            }
        });
    },
    post: async <T>(url: string, data: unknown, options: RequestOptions = {}): Promise<T> => {
        return fetcher<T>(url, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY,
                ...options.headers,
            },
        });
    },
};

async function fetcher<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    let baseUrl = API_URL;
    if (!baseUrl.endsWith('/api')) {
        baseUrl = `${baseUrl}/api`;
    }
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

    const response = await fetch(url, options);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `API Error: ${response.statusText}`);
    }

    return response.json();
}
