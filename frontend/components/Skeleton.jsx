export function CardSkeleton() {
  return (
    <div className="card-base p-5 flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <div className="skeleton h-5 w-24" />
        <div className="skeleton h-4 w-16" />
      </div>
      <div className="skeleton h-5 w-3/4" />
      <div className="skeleton h-4 w-full" />
      <div className="skeleton h-4 w-5/6" />
      <div className="flex gap-1.5">
        <div className="skeleton h-5 w-12" />
        <div className="skeleton h-5 w-16" />
        <div className="skeleton h-5 w-10" />
      </div>
      <div className="flex items-center gap-2 pt-3 border-t border-stone-100">
        <div className="skeleton h-7 w-7 !rounded-full" />
        <div className="skeleton h-4 w-20" />
      </div>
    </div>
  );
}

export function FeedSkeleton({ count = 6 }) {
  return (
    <div data-testid="feed-skeleton" className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => <CardSkeleton key={i} />)}
    </div>
  );
}
