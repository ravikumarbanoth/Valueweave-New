"use client";
import { useEffect, useState } from "react";
import AdminShell from "@/components/admin/AdminShell";
import { createClient } from "@/lib/supabase-browser";
import {
  Megaphone, Plus, Trash2, CheckCircle, XCircle, Edit2, Save, X, AlertCircle,
} from "lucide-react";

const EMPTY_FORM = {
  title: "", message: "", link: "", link_label: "",
  priority: "normal", is_active: true, expires_at: "",
};

function PriorityBadge({ priority }) {
  const styles = {
    high:   "bg-rose-100 text-rose-700",
    normal: "bg-amber-100 text-amber-700",
    low:    "bg-stone-100 text-stone-500",
  };
  return <span className={`chip text-[10px] font-bold ${styles[priority]}`}>{priority.toUpperCase()}</span>;
}

export default function AnnouncementsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const sb = createClient();

  async function load() {
    setLoading(true);
    const { data } = await sb.from("announcements").select("*").order("created_at", { ascending: false });
    setRows(data || []);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function save() {
    setError(null);
    if (!form.title.trim() || !form.message.trim()) {
      setError("Title and message are required.");
      return;
    }
    setSaving(true);
    const payload = {
      title: form.title.trim(),
      message: form.message.trim(),
      link: form.link.trim() || null,
      link_label: form.link_label.trim() || null,
      priority: form.priority,
      is_active: form.is_active,
      expires_at: form.expires_at || null,
    };
    if (editId) {
      await sb.from("announcements").update(payload).eq("id", editId);
    } else {
      await sb.from("announcements").insert(payload);
    }
    setSaving(false);
    setShowForm(false);
    setEditId(null);
    setForm(EMPTY_FORM);
    load();
  }

  async function toggleActive(id, current) {
    await sb.from("announcements").update({ is_active: !current }).eq("id", id);
    load();
  }

  async function remove(id) {
    if (!confirm("Delete this announcement?")) return;
    await sb.from("announcements").delete().eq("id", id);
    load();
  }

  function startEdit(row) {
    setForm({
      title: row.title, message: row.message,
      link: row.link || "", link_label: row.link_label || "",
      priority: row.priority, is_active: row.is_active,
      expires_at: row.expires_at ? row.expires_at.slice(0, 16) : "",
    });
    setEditId(row.id);
    setShowForm(true);
  }

  const activeCount = rows.filter((r) => r.is_active).length;

  return (
    <AdminShell>
      <div className="p-6 max-w-4xl space-y-6">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <span className="chip bg-amber-100 text-amber-700 border border-amber-200">ANNOUNCEMENTS</span>
            <h1 className="font-display font-extrabold text-2xl text-ink mt-2 flex items-center gap-2">
              <Megaphone size={22} className="text-amber-500" />
              Site-Wide Announcements
            </h1>
            <p className="text-stone-500 text-sm mt-1">
              {activeCount > 0 ? `${activeCount} active` : "No active"} announcement{activeCount !== 1 ? "s" : ""} — displayed as a dismissible banner on all pages
            </p>
          </div>
          <button
            onClick={() => { setForm(EMPTY_FORM); setEditId(null); setShowForm(true); }}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 text-white text-[13px] font-semibold hover:bg-amber-600 transition-colors shrink-0"
          >
            <Plus size={14} /> New Announcement
          </button>
        </div>

        {/* Create / Edit Form */}
        {showForm && (
          <div className="card-base p-5 border-2 border-amber-200 space-y-4">
            <div className="flex items-center justify-between">
              <p className="font-display font-bold text-ink">{editId ? "Edit" : "Create"} Announcement</p>
              <button onClick={() => { setShowForm(false); setEditId(null); setForm(EMPTY_FORM); }} className="text-stone-400 hover:text-stone-600">
                <X size={16} />
              </button>
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 rounded-xl text-[13px] text-rose-700">
                <AlertCircle size={14} /> {error}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="label-sm">Title *</label>
                <input
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="🚀 500 Opportunities Added"
                  className="input-base w-full"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="label-sm">Message *</label>
                <textarea
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  placeholder="We just added 500 new opportunities across Telangana and Andhra Pradesh. Check them out!"
                  rows={3}
                  className="input-base w-full resize-none"
                />
              </div>
              <div>
                <label className="label-sm">Link URL (optional)</label>
                <input
                  value={form.link}
                  onChange={(e) => setForm({ ...form, link: e.target.value })}
                  placeholder="/explore"
                  className="input-base w-full"
                />
              </div>
              <div>
                <label className="label-sm">Link Label</label>
                <input
                  value={form.link_label}
                  onChange={(e) => setForm({ ...form, link_label: e.target.value })}
                  placeholder="Explore Now"
                  className="input-base w-full"
                />
              </div>
              <div>
                <label className="label-sm">Priority</label>
                <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} className="input-base w-full">
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div>
                <label className="label-sm">Expires At (optional)</label>
                <input
                  type="datetime-local"
                  value={form.expires_at}
                  onChange={(e) => setForm({ ...form, expires_at: e.target.value })}
                  className="input-base w-full"
                />
              </div>
              <div className="flex items-center gap-3">
                <input
                  id="is_active"
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  className="rounded border-stone-300 text-amber-500"
                />
                <label htmlFor="is_active" className="text-[13px] font-semibold text-stone-600">Activate immediately</label>
              </div>
            </div>

            <div className="flex gap-2 justify-end pt-2">
              <button onClick={() => { setShowForm(false); setEditId(null); }} className="btn-ghost text-sm">Cancel</button>
              <button onClick={save} disabled={saving} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500 text-white text-[13px] font-semibold hover:bg-amber-600 disabled:opacity-50">
                <Save size={13} /> {saving ? "Saving…" : "Save"}
              </button>
            </div>
          </div>
        )}

        {/* Announcements list */}
        {loading ? (
          <div className="text-sm text-stone-400 italic p-6">Loading…</div>
        ) : rows.length === 0 ? (
          <div className="card-base p-8 text-center">
            <Megaphone size={32} className="text-stone-200 mx-auto mb-3" />
            <p className="text-stone-400 font-medium">No announcements yet.</p>
            <p className="text-[12px] text-stone-300 mt-1">Create one to display a banner across the entire site.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {rows.map((row) => {
              const expired = row.expires_at && new Date(row.expires_at) < new Date();
              return (
                <div key={row.id} className={`card-base p-4 flex items-start gap-4 ${expired ? "opacity-60" : ""}`}>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <PriorityBadge priority={row.priority} />
                      {row.is_active && !expired && (
                        <span className="chip bg-green-100 text-green-700 text-[10px]">LIVE</span>
                      )}
                      {expired && (
                        <span className="chip bg-stone-100 text-stone-400 text-[10px]">EXPIRED</span>
                      )}
                      <p className="font-display font-bold text-ink text-sm">{row.title}</p>
                    </div>
                    <p className="text-[13px] text-stone-500 line-clamp-2">{row.message}</p>
                    {row.link && (
                      <p className="text-[11px] text-amber-600 mt-1">→ {row.link_label || row.link}</p>
                    )}
                    {row.expires_at && (
                      <p className="text-[10px] text-stone-300 mt-1">Expires: {new Date(row.expires_at).toLocaleString()}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => toggleActive(row.id, row.is_active)}
                      title={row.is_active ? "Deactivate" : "Activate"}
                      className={`p-1.5 rounded-lg transition-colors ${row.is_active ? "text-green-600 hover:bg-green-50" : "text-stone-400 hover:bg-stone-100"}`}
                    >
                      {row.is_active ? <CheckCircle size={16} /> : <XCircle size={16} />}
                    </button>
                    <button onClick={() => startEdit(row)} className="p-1.5 rounded-lg text-stone-400 hover:bg-stone-100 hover:text-amber-600 transition-colors">
                      <Edit2 size={16} />
                    </button>
                    <button onClick={() => remove(row.id)} className="p-1.5 rounded-lg text-stone-400 hover:bg-rose-50 hover:text-rose-500 transition-colors">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AdminShell>
  );
}
