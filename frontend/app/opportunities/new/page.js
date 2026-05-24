import { Suspense } from "react";
import OpportunityFormClient from "./OpportunityFormClient";

export const dynamic = "force-dynamic";

export default function PostOpportunityPage() {
  return (
    <Suspense fallback={<OpportunityFormFallback />}>
      <OpportunityFormClient />
    </Suspense>
  );
}

function OpportunityFormFallback() {
  return (
    <div className="min-h-screen bg-cream pb-20 md:pb-0">
      <main className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="font-display font-extrabold text-3xl tracking-tight mb-1">Post an opportunity</h1>
        <p className="text-muted text-sm mb-6">Share what you're building or looking for. The community can connect with you.</p>
        <div className="card-base p-6 flex flex-col gap-4">
          <div className="skeleton h-11 w-full" />
          <div className="skeleton h-28 w-full" />
          <div className="grid grid-cols-2 gap-3">
            <div className="skeleton h-11 w-full" />
            <div className="skeleton h-11 w-full" />
          </div>
          <div className="skeleton h-11 w-full" />
          <div className="grid grid-cols-2 gap-3">
            <div className="skeleton h-11 w-full" />
            <div className="skeleton h-11 w-full" />
          </div>
          <div className="skeleton h-12 w-full !rounded-full" />
        </div>
      </main>
    </div>
  );
}
