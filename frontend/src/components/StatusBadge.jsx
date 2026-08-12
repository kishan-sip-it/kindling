// The lead pipeline as a spark → fire metaphor — memorable stage names
// for the UI, while the underlying LeadStatus enum stays plain and
// functional (new/contacted/qualified/won/lost) for data integrity and
// straightforward querying/filtering.
const STAGE_LABELS = {
  new: "Spark",
  contacted: "Warming",
  qualified: "Catching",
  won: "Ablaze",
  lost: "Ash",
};

const STYLES = {
  new: "bg-sky-50 text-sky-700 border-sky-200",
  contacted: "bg-amber-50 text-amber-700 border-amber-200",
  qualified: "bg-orange-50 text-orange-700 border-orange-200",
  won: "bg-emerald-50 text-emerald-700 border-emerald-200",
  lost: "bg-stone-100 text-stone-500 border-stone-200",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`inline-flex rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide ${STYLES[status] || STYLES.new}`}>
      {STAGE_LABELS[status] || status}
    </span>
  );
}
