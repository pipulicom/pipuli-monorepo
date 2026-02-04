
"use client";

import { useEffect, useState } from "react";
import { Equipment, EquipmentService } from "../../services/api";

export default function EquipmentsPage() {
    const [equipments, setEquipments] = useState<Equipment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Form state
    const [formData, setFormData] = useState({ name: "", brand: "", type: "" });

    const fetchEquipments = async () => {
        try {
            setLoading(true);
            const data = await EquipmentService.list();
            setEquipments(data);
            setError("");
        } catch (err) {
            setError("Failed to load equipments. Is the backend running?");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEquipments();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || !formData.brand || !formData.type) {
            alert("Please fill all fields");
            return;
        }

        try {
            await EquipmentService.create(formData);
            setFormData({ name: "", brand: "", type: "" });
            fetchEquipments(); // Reload list
        } catch (err) {
            alert("Failed to create equipment");
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold mb-8 text-blue-400">Pipuli Equipments Prototype</h1>

                {/* FORM */}
                <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8 border border-gray-700">
                    <h2 className="text-xl font-semibold mb-4">Add New Equipment</h2>
                    <form onSubmit={handleSubmit} className="flex gap-4 items-end flex-wrap">
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Name</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                                placeholder="e.g. Drill"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Brand</label>
                            <input
                                type="text"
                                value={formData.brand}
                                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                                className="bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                                placeholder="e.g. DeWalt"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Type</label>
                            <input
                                type="text"
                                value={formData.type}
                                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                className="bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                                placeholder="e.g. Power Tool"
                            />
                        </div>
                        <button
                            type="submit"
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors"
                        >
                            Add
                        </button>
                    </form>
                </div>

                {/* LIST */}
                <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
                    <h2 className="text-xl font-semibold p-6 border-b border-gray-700">Equipment List</h2>

                    {loading ? (
                        <div className="p-6 text-center text-gray-400">Loading...</div>
                    ) : error ? (
                        <div className="p-6 text-center text-red-400">{error}</div>
                    ) : equipments.length === 0 ? (
                        <div className="p-6 text-center text-gray-400">No equipments found. Add one!</div>
                    ) : (
                        <table className="w-full text-left">
                            <thead>
                                <tr className="bg-gray-750 text-gray-400 border-b border-gray-700">
                                    <th className="p-4">Name</th>
                                    <th className="p-4">Brand</th>
                                    <th className="p-4">Type</th>
                                    <th className="p-4">ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {equipments.map((item) => (
                                    <tr key={item.id} className="border-b border-gray-700 hover:bg-gray-750 transition-colors">
                                        <td className="p-4 font-medium text-white">{item.name}</td>
                                        <td className="p-4 text-gray-300">{item.brand}</td>
                                        <td className="p-4 text-gray-300">
                                            <span className="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded-full">
                                                {item.type}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-500 text-sm font-mono">{item.id}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
            {/* DEBUG PROBE */}
            <div className="fixed bottom-0 left-0 right-0 bg-black text-xs text-green-400 p-1 text-center font-mono opacity-80">
                DEBUG PROBE: API_URL=[{process.env.NEXT_PUBLIC_API_URL}] PROJ_ID=[{process.env.NEXT_PUBLIC_PROJECT_ID}]
            </div>
        </div>
    );
}
