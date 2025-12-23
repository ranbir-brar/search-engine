"use client";

import { useState, useEffect } from "react";
import { Search, Server, AlertCircle, ListFilter } from "lucide-react";

interface SearchResult {
  id: string;
  title: string;
  url: string;
  content: string;
  category: string;
  score: number;
}

const API_URL = "http://localhost:8000";

export default function SearchInterface() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [limit, setLimit] = useState<number>(10);

  // UX State
  const [hasSearched, setHasSearched] = useState(false); // Prevents premature "No results"
  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");
  const [error, setError] = useState("");

  // 1. On mount: Check Backend Health Only
  useEffect(() => {
    async function checkHealth() {
      try {
        const healthRes = await fetch(`${API_URL}/health`);
        if (healthRes.ok) {
          setServerStatus("online");
        } else {
          setServerStatus("offline");
        }
      } catch (e) {
        setServerStatus("offline");
      }
    }
    checkHealth();
  }, []);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setHasSearched(false);

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          limit: limit,
          category: null,
        }),
      });

      const data = await response.json();

      // --- DEBUGGING LOG ---
      console.log("API Response:", data);

      if (!response.ok) {
        throw new Error(data.detail || "Search failed");
      }

      // --- SAFETY CHECK ---
      if (Array.isArray(data)) {
        setResults(data);
        setHasSearched(true);
      } else {
        console.error("Expected array but got:", data);
        setResults([]); // Fallback to empty array to prevent crash
        setError("API returned invalid data format");
      }
    } catch (err: any) {
      console.error("Search Error:", err);
      setError(err.message || "Failed to fetch results");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4 space-y-8">
      {/* Header & Status */}
      <div className="flex justify-between items-center border-b border-neutral-800 pb-4">
        <h2 className="text-2xl font-bold text-white">Neural Search</h2>

        <div className="flex items-center gap-2 text-sm">
          <span className="text-neutral-400">Backend:</span>
          {serverStatus === "checking" && (
            <span className="text-yellow-500">Connecting...</span>
          )}
          {serverStatus === "online" && (
            <span className="flex items-center gap-1 text-green-500">
              <Server size={14} /> Online
            </span>
          )}
          {serverStatus === "offline" && (
            <span className="flex items-center gap-1 text-red-500">
              <AlertCircle size={14} /> Offline
            </span>
          )}
        </div>
      </div>

      {/* Search Controls */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex gap-2">
          {/* Main Input */}
          <div className="relative flex-1">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400"
              size={20}
            />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search..."
              className="w-full bg-neutral-900 border border-neutral-700 rounded-lg pl-10 pr-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
            />
          </div>

          {/* Limit Selector */}
          <div className="relative">
            <ListFilter
              className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400"
              size={16}
            />
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="h-full bg-neutral-900 border border-neutral-700 rounded-lg pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none appearance-none cursor-pointer"
            >
              <option value={5}>5 items</option>
              <option value={10}>10 items</option>
              <option value={20}>20 items</option>
              <option value={50}>50 items</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || serverStatus === "offline"}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-200 text-sm">
          {error}
        </div>
      )}

      {/* Results Grid */}
      <div className="grid gap-4">
        {results.map((result) => (
          <div
            key={result.id}
            className="bg-neutral-900/50 border border-neutral-800 p-5 rounded-xl hover:border-neutral-700 transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-mono text-blue-400 bg-blue-900/20 px-2 py-0.5 rounded">
                {result.category}
              </span>
              <span className="text-xs font-mono text-neutral-500">
                Score: {result.score.toFixed(4)}
              </span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline hover:text-blue-400"
              >
                {result.title}
              </a>
            </h3>
            <p className="text-neutral-400 text-sm leading-relaxed line-clamp-3">
              {result.content}
            </p>
          </div>
        ))}

        {/* Empty State - Only shows if we HAVE searched and found nothing */}
        {!loading && hasSearched && results.length === 0 && !error && (
          <div className="text-center py-12 text-neutral-500">
            No results found for "{query}"
          </div>
        )}
      </div>
    </div>
  );
}
