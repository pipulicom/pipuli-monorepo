import { redirect } from "next/navigation";

export default function WizardIndex() {
    redirect("/create/step-1");
}
