"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Search,
  Sparkles,
  TrendingUp,
  Clock,
  Zap,
  ChevronDown,
  Layers,
} from "lucide-react";

function SearchContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "artificial intelligence";

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState(initialQuery);

  // Feature: Limit Results
  const [resultsLimit, setResultsLimit] = useState(10);
  const [showLimitMenu, setShowLimitMenu] = useState(false);

  // Hardcoded Dark Theme
  const theme = {
    bg: "bg-[#121212]",
    card: "bg-[#1E1E1E]/50",
    border: "border-[#333333]",
    text: "text-[#E0E0E0]",
    textMuted: "text-[#A0A0A0]",
    textFaded: "text-[#666666]",
    accent: "from-[#3392ff] to-[#046bfb]",
    hover: "hover:bg-[#2C2C2C]",
    input: "bg-[#1E1E1E] border-[#333333] focus:border-[#47a7eb]",
    glow: "shadow-[0_0_20px_rgba(71,167,235,0.1)]",
    resultHover: "hover:bg-[#1E1E1E]",
    dropdown: "bg-[#1E1E1E]",
  };

  const baseResults = [
    {
      id: "1",
      title: "Introduction to Neural Networks and Deep Learning",
      content:
        "Neural networks are computing systems inspired by biological neural networks that constitute animal brains.",
      category: "Machine Learning",
      score: 0.95,
      url: "example.com/neural-networks",
    },
    {
      id: "2",
      title: "Understanding Semantic Search Technology",
      content:
        "Semantic search is a data searching technique that aims to understand the intent and contextual meaning of search queries.",
      category: "Information Retrieval",
      score: 0.89,
      url: "example.com/semantic-search",
    },
    {
      id: "3",
      title: "Vector Databases: The Future of Search",
      content:
        "Vector databases like Qdrant enable efficient similarity search by storing and retrieving high-dimensional vectors.",
      category: "Database Technology",
      score: 0.84,
      url: "example.com/vector-db",
    },
  ];

  // Generate more data so the limit toggle actually does something
  const generateMockData = () => {
    let data = [];
    for (let i = 0; i < 20; i++) {
      data.push(...baseResults.map((r) => ({ ...r, id: `${r.id}-${i}` })));
    }
    return data;
  };

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setResults(generateMockData());
      setLoading(false);
    }, 800);
  }, [query]);

  const handleSearch = () => {
    if (searchQuery.trim()) setQuery(searchQuery);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div className={`min-h-screen ${theme.bg} ${theme.text}`}>
      {/* Header */}
      <header
        className={`sticky top-0 ${theme.card} ${theme.border} border-b backdrop-blur-xl z-50`}
      >
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-6">
            <div
              className="flex items-center gap-2 cursor-pointer group"
              onClick={() => (window.location.href = "/")}
            >
              <div
                className={`p-2 rounded-xl ${theme.card} ${theme.border} border backdrop-blur-xl`}
              >
                <Sparkles className="w-5 h-5 text-[#47a7eb] group-hover:rotate-12 transition-transform" />
              </div>
              <span
                className={`text-xl font-bold bg-gradient-to-r ${theme.accent} text-transparent bg-clip-text hidden sm:block`}
              >
                Neural Seek
              </span>
            </div>

            <div className="flex-1 max-w-2xl relative group">
              <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                <Search
                  className={`h-5 w-5 ${theme.textMuted} group-focus-within:text-[#47a7eb] transition-colors`}
                />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                className={`w-full ${theme.input} ${theme.text} backdrop-blur-xl border rounded-full py-2.5 pl-12 pr-4 outline-none focus:ring-2 focus:ring-[#47a7eb]/30 transition-all`}
                placeholder="Search..."
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-8 relative z-10">
        {/* Controls Bar */}
        <div
          className={`flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4 ${theme.textMuted} text-sm`}
        >
          <div className="flex items-center gap-6">
            <span>
              Found{" "}
              <span className={`${theme.text} font-semibold`}>
                {results.length}
              </span>{" "}
              results
            </span>
            <div className="flex items-center gap-1 text-xs">
              <Zap className="w-3 h-3" />
              <span>42ms</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Limit Toggle Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowLimitMenu(!showLimitMenu)}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-full ${theme.card} ${theme.border} border ${theme.hover} transition-all text-xs font-medium`}
              >
                <Layers className="w-3 h-3" />
                Show: {resultsLimit}
                <ChevronDown className="w-3 h-3 opacity-50" />
              </button>

              {showLimitMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowLimitMenu(false)}
                  />
                  <div
                    className={`absolute right-0 top-full mt-2 w-32 ${theme.dropdown} ${theme.border} border rounded-xl shadow-xl z-20 overflow-hidden`}
                  >
                    {[10, 25, 50].map((num) => (
                      <button
                        key={num}
                        onClick={() => {
                          setResultsLimit(num);
                          setShowLimitMenu(false);
                        }}
                        className={`w-full text-left px-4 py-2 text-xs ${
                          theme.hover
                        } ${
                          resultsLimit === num
                            ? "text-[#47a7eb] font-bold"
                            : theme.text
                        }`}
                      >
                        {num} results
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <button
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full ${theme.card} ${theme.border} border ${theme.hover} transition-all text-xs`}
            >
              <TrendingUp className="w-3 h-3" />
              Relevance
            </button>
          </div>
        </div>

        {/* Results List */}
        <div className="space-y-6">
          {loading
            ? [...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className={`${theme.card} ${theme.border} border backdrop-blur-xl rounded-2xl p-6 animate-pulse`}
                >
                  <div
                    className={`h-4 ${theme.input} w-1/4 rounded mb-3`}
                  ></div>
                  <div className={`h-6 ${theme.card} w-3/4 rounded mb-3`}></div>
                  <div className={`h-20 ${theme.input} w-full rounded`}></div>
                </div>
              ))
            : // Slice the results based on the limit
              results.slice(0, resultsLimit).map((result) => (
                <div
                  key={result.id}
                  className={`${theme.card} ${theme.border} border backdrop-blur-xl rounded-2xl p-6 ${theme.resultHover} transition-all duration-300 cursor-pointer group ${theme.glow}`}
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span
                      className={`${theme.input} ${theme.textMuted} px-3 py-1 rounded-full text-xs font-medium border ${theme.border}`}
                    >
                      {result.category}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-green-400 text-xs font-medium">
                        {(result.score * 100).toFixed(0)}% match
                      </span>
                    </div>
                  </div>

                  <h2
                    className={`text-xl font-semibold mb-2 bg-gradient-to-r ${theme.accent} text-transparent bg-clip-text group-hover:underline underline-offset-4 decoration-[#47a7eb]`}
                  >
                    {result.title}
                  </h2>

                  <p className={`${theme.textMuted} text-sm leading-relaxed`}>
                    {result.content.substring(0, 200)}...
                  </p>
                </div>
              ))}
        </div>
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#121212]" />}>
      <SearchContent />
    </Suspense>
  );
}
