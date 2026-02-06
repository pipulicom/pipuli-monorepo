import { redirect } from "../../../../src/i18n/routing";

export default function WizardIndex() {
    redirect({ href: "/create/step-1", locale: "pt" });
}
