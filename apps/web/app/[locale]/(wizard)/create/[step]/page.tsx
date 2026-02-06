import { useTranslations } from 'next-intl';

type Params = Promise<{ step: string }>;

export default async function StepPage(props: { params: Params }) {
    // Note: In Next.js 15+ params is a promise, but in client components/hooks usage might differ. 
    // However, useTranslations works in server components too.
    // We need to unwrap params correctly or use it as is if compatible.
    // The previous code awaited generic params props.
    // Actually, `useTranslations` in Server Components works directly. 
    // But this is a component that *might* be server rendered.
    // Let's keep the async signature and use 'use' from React or await params if needed.
    // Wait, useTranslations hook is generally for client components or standard server usage.
    // Let's stick to the existing structure but add the hook call.
    // IMPORTANT: Next.js App Router Server Components can use `getTranslations` (async) or `useTranslations` (sync, if context provided).
    // Given the previous setup used `NextIntlClientProvider` in layout, `useTranslations` should work if this is a Client Component OR if we are okay with it.
    // BUT checking the file, it has `export default async function`. `useTranslations` hook *might* complain in async server component if not configured right?
    // Actually, for Server Components, we often use `getTranslations`.
    // Let's try `useTranslations` first as it's common in this setup, but if it fails we might need `getTranslations` + async.
    // Wait, `app/[locale]/layout.tsx` has `NextIntlClientProvider`.
    // If this page is a Server Component (it is async), `useTranslations` might work if the strings are static? 
    // The docs say: "You can use useTranslations in Server Components too." -> Yes.

    // BUT we need to handle the `params` promise if we are accessing `step`.
    // Let's grab `t` first.

    // Changing to sync component might be cleaner if we don't do other async work, but it accepts `params` as promise.
    // Let's keep it async and use `getTranslations`? Or unwrapping params properly.
    // Actually, since this is simple text replacement, I will change to:

    // "import { useTranslations } from 'next-intl';"

    // But `useTranslations` requires the component to call it synchronously.
    // If the component is async, we should use `const t = await getTranslations('Wizard');`.

    // Let's modify to use `getTranslations` because the component is `async`.

    // REVISED PLAN: Use `getTranslations` from `next-intl/server`.

    const { step } = await props.params;
    const { getTranslations } = await import('next-intl/server');
    const t = await getTranslations('Wizard');

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold tracking-tight">{t('step')}: {step}</h1>
            <p className="text-muted-foreground">
                {t('description')} <span className="font-mono text-primary">{step}</span>.
            </p>

            <div className="p-4 border border-dashed rounded bg-slate-50">
                <p className="text-sm text-gray-500 mb-2">{t('placeholder')}</p>
            </div>

            <div className="flex justify-end pt-4">
                <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800">
                    {t('next')}
                </button>
            </div>
        </div>
    );
}
