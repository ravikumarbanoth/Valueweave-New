import AppNavbar from "@/components/AppNavbar";
import { FeedSkeleton } from "@/components/Skeleton";

export default function IdeasLoading() {
  return (
    <div className="min-h-screen bg-cream pb-24 md:pb-16 font-body">
      <AppNavbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="skeleton h-9 w-64 mb-3" />
        <div className="skeleton h-4 w-full max-w-xl mb-6" />
        <div className="card-base p-4 mb-5">
          <div className="skeleton h-11 w-full mb-3" />
          <div className="flex gap-2"><div className="skeleton h-8 w-24" /><div className="skeleton h-8 w-24" /><div className="skeleton h-8 w-24" /></div>
        </div>
        <FeedSkeleton count={6} />
      </main>
    </div>
  );
}
