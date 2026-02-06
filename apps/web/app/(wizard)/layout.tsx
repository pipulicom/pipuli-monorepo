export default function WizardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen flex-col bg-slate-50">
            <header className="border-b bg-white">
                <div className="container flex h-16 items-center justify-between py-4">
                    <div className="font-bold">Creation Wizard</div>
                    {/* Progress Bar Placeholder */}
                    <div className="text-sm text-gray-500">Step 1 of 3</div>
                </div>
            </header>
            <main className="flex-1 container py-8">
                <div className="mx-auto max-w-2xl bg-white p-8 rounded-lg shadow-sm border">
                    {children}
                </div>
            </main>
        </div>
    );
}
