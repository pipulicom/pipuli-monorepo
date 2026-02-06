type Params = Promise<{ step: string }>;

export default async function StepPage(props: { params: Params }) {
    const params = await props.params;
    const step = params.step;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold tracking-tight">Step: {step}</h1>
            <p className="text-muted-foreground">
                This is a generic placeholder for step: <span className="font-mono text-primary">{step}</span>.
            </p>

            <div className="p-4 border border-dashed rounded bg-slate-50">
                <p className="text-sm text-gray-500 mb-2">Form Component will be loaded here based on the step.</p>
            </div>

            <div className="flex justify-end pt-4">
                <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800">
                    Next
                </button>
            </div>
        </div>
    );
}
