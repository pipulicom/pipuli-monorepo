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

    const startTime = Date.now();

    // Lazy load the store to avoid circular deps or client-side issues
    const { useDebugStore } = await import('../store/debugStore');
    const addLog = useDebugStore.getState().addLog;
    const isDebug = process.env.NEXT_PUBLIC_DEBUG_MODE === 'true';

    if (isDebug) {
        addLog({
            type: 'request',
            method: options.method || 'GET',
            url: url,
            data: options.body ? JSON.parse(options.body as string) : undefined
        });
    }

    const response = await fetch(url, options);
    const duration = Date.now() - startTime;

    if (isDebug) {
        // Clone response to read body without consuming the stream for the app
        const clone = response.clone();
        const responseData = await clone.json().catch(() => null);

        addLog({
            type: 'response',
            method: options.method || 'GET',
            url: url,
            status: response.status,
            duration,
            data: responseData
        });
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        if (isDebug) {
            addLog({
                type: 'error',
                method: options.method || 'GET',
                url: url,
                status: response.status,
                message: errorData.message || response.statusText,
                data: errorData
            });
        }

        // Throw the full error object so the UI can handle i18n codes
        // The errorData might look like { error: "unauthorized", code: "AUTH_TOKEN", params: {} }
        const error = new Error(errorData.message || `API Error: ${response.statusText}`);
        (error as any).info = errorData;
        (error as any).code = errorData.code;
        throw error;
    }

    return response.json();
}
