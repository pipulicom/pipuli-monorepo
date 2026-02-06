import { useTranslations } from 'next-intl';
import { Link } from '../../../../src/i18n/routing';

export default function EquipmentsLanding() {
    const t = useTranslations('Equipments');

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] bg-background text-foreground">
            <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center space-y-4 text-center">
                    <div className="space-y-2">
                        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                            {t('title')}
                        </h1>
                        <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                            {t('description')}
                        </p>
                    </div>
                    <div className="space-x-4">
                        <Link
                            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-black text-white"
                            href="/equipments/manage"
                        >
                            {t('getStarted')}
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
