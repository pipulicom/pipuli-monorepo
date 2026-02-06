export default function EquipmentsLanding() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] bg-background text-foreground">
            <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center space-y-4 text-center">
                    <div className="space-y-2">
                        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                            Manage Your Equipments
                        </h1>
                        <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                            Track, organize, and manage your inventory with our simple and powerful tool.
                        </p>
                    </div>
                    <div className="space-x-4">
                        <a
                            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-black text-white"
                            href="/equipments/manage"
                        >
                            Get Started
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}
