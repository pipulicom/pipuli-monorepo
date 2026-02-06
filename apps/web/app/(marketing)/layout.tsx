import Link from "next/link";

export default function MarketingLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen flex-col">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container flex h-14 items-center">
                    <div className="mr-4 flex">
                        <Link className="mr-6 flex items-center space-x-2" href="/">
                            <span className="hidden font-bold sm:inline-block">
                                BrandName
                            </span>
                        </Link>
                        <nav className="flex items-center space-x-6 text-sm font-medium">
                            <Link href="/create" className="transition-colors hover:text-foreground/80 text-foreground/60">Create</Link>
                            <Link href="#" className="transition-colors hover:text-foreground/80 text-foreground/60">About</Link>
                        </nav>
                    </div>
                </div>
            </header>
            <main className="flex-1">{children}</main>
            <footer className="py-6 md:px-8 md:py-0">
                <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
                    <p className="text-balance text-center text-sm leading-loose text-muted-foreground md:text-left">
                        Built by Pipuli.
                    </p>
                </div>
            </footer>
        </div>
    );
}
