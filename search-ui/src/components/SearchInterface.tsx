"use client";

import { useState, useEffect } from "react";
import {
  Search,
  AlertCircle,
  Loader2,
  ExternalLink,
  FileText,
  BookOpen,
  GraduationCap,
  ClipboardList,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";

interface SearchResult {
  id: string;
  title: string;
  url: string;
  content?: string;
  source: string;
  resource_type: string;
  authors: string[];
  score?: number;
  summary_preview?: string;
}

const API_URL = "http://localhost:8000";

const TYPE_STYLES: Record<string, { color: string; icon: React.ElementType }> =
  {
    "Lecture Slides": {
      color: "bg-orange-500/20 text-orange-600 border-orange-500/30",
      icon: BookOpen,
    },
    "Course Notes": {
      color: "bg-green-500/20 text-green-600 border-green-500/30",
      icon: GraduationCap,
    },
    Syllabus: {
      color: "bg-purple-500/20 text-purple-600 border-purple-500/30",
      icon: ClipboardList,
    },
    Exam: {
      color: "bg-red-500/20 text-red-600 border-red-500/30",
      icon: FileText,
    },
    "Problem Set": {
      color: "bg-amber-500/20 text-amber-600 border-amber-500/30",
      icon: ClipboardList,
    },
    Solutions: {
      color: "bg-teal-500/20 text-teal-600 border-teal-500/30",
      icon: FileText,
    },
  };

export default function SearchInterface() {
  // View state
  const [view, setView] = useState<"home" | "results">("home");

  // Search state
  const [query, setQuery] = useState("");
  const [searchedQuery, setSearchedQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [limit, setLimit] = useState<string>("10");
  const [resourceType, setResourceType] = useState<string>("All");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestion, setSuggestion] = useState<string | null>(null);

  // Server state
  const [serverStatus, setServerStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");

  useEffect(() => {
    async function checkHealth() {
      try {
        const healthRes = await fetch(`${API_URL}/health`);
        if (healthRes.ok) {
          setServerStatus("online");
        } else {
          setServerStatus("offline");
        }
      } catch {
        setServerStatus("offline");
      }
    }
    checkHealth();
  }, []);

  // Simple spell check
  const getSpellingSuggestion = (term: string): string | null => {
    const corrections: Record<string, string> = {
      algoritm: "algorithm",
      algorythm: "algorithm",
      machin: "machine",
      machien: "machine",
      learing: "learning",
      learnign: "learning",
      neaural: "neural",
      nueral: "neural",
      netwrok: "network",
      programing: "programming",
      optimzation: "optimization",
      artifical: "artificial",
      inteligence: "intelligence",
      structre: "structure",
      databse: "database",
      compuer: "computer",
      linera: "linear",
      algebre: "algebra",
    };

    const words = term.toLowerCase().split(/\s+/);
    let hasSuggestion = false;
    const correctedWords = words.map((word) => {
      if (corrections[word]) {
        hasSuggestion = true;
        return corrections[word];
      }
      return word;
    });

    return hasSuggestion ? correctedWords.join(" ") : null;
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setSuggestion(null);
    setSearchedQuery(query.trim());
    setView("results");

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          limit: parseInt(limit),
          resource_type: resourceType === "All" ? null : resourceType,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Search failed");
      }

      if (Array.isArray(data)) {
        setResults(data);
        if (data.length === 0) {
          const spellingSuggestion = getSpellingSuggestion(query);
          if (spellingSuggestion) {
            setSuggestion(spellingSuggestion);
          }
        }
      } else {
        setResults([]);
        setError("API returned invalid data format");
      }
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to fetch results";
      setError(errorMessage);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = () => {
    if (suggestion) {
      setQuery(suggestion);
      setTimeout(() => {
        const form = document.querySelector("form");
        if (form) form.requestSubmit();
      }, 0);
    }
  };

  const goHome = () => {
    setView("home");
    setQuery("");
    setSearchedQuery("");
    setResults([]);
    setError("");
    setSuggestion(null);
  };

  const getTypeStyle = (type: string) => {
    return TYPE_STYLES[type] || TYPE_STYLES.Paper;
  };

  // Home Page - Clean and minimal
  if (view === "home") {
    return (
      <div className="w-full min-h-screen bg-background flex flex-col">
        {/* Centered Content */}
        <div className="flex-1 flex flex-col items-center justify-center px-4 -mt-16">
          <div className="w-full max-w-2xl space-y-8">
            {/* Atlas Branding */}
            <div className="mb-4">
              <h1
                style={{
                  fontFamily: 'Circular, "Segoe UI", sans-serif',
                  fontSize: "72px",
                  fontWeight: 400,
                  letterSpacing: "-2px",
                  color: "rgb(43, 41, 40)",
                  marginBottom: "15px",
                  marginTop: 0,
                  display: "block",
                  textAlign: "left",
                }}
              >
                Atlas
              </h1>
            </div>

            {/* Aceternity Animated Search Bar */}
            <PlaceholdersAndVanishInput
              placeholders={[
                "Search for calculus exams...",
                "Find linear algebra problem sets...",
                "Look up physics lecture notes...",
                "Discover CS algorithm solutions...",
                "Explore MIT OCW materials...",
              ]}
              onChange={(e) => setQuery(e.target.value)}
              onSubmit={handleSearch}
            />

            {/* Server Status */}
            {serverStatus === "offline" && (
              <div className="text-center">
                <p className="text-sm text-destructive flex items-center justify-center gap-1.5">
                  <AlertCircle className="size-3.5" />
                  API offline - start with: uvicorn search_api:app --port 8000
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Results Page
  return (
    <div className="w-full min-h-screen bg-background py-6 px-4">
      <div className="w-full max-w-4xl mx-auto space-y-6">
        {/* Header with Logo and Search */}
        <div className="flex items-center gap-4 pb-4 border-b border-border">
          {/* Clickable Atlas Logo */}
          <button
            onClick={goHome}
            className="hover:opacity-70 transition-opacity"
          >
            <span className="text-xl font-bold text-foreground tracking-tight">
              Atlas
            </span>
          </button>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <div className="absolute inset-0 bg-card/50 backdrop-blur-sm rounded-lg border border-border" />
              <div className="relative flex items-center">
                <Search className="absolute left-3 text-muted-foreground size-4" />
                <Input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search..."
                  className="pl-10 h-10 bg-transparent border-0 focus-visible:ring-0"
                />
              </div>
            </div>
          </form>

          {/* Results Limit */}
          <Select value={limit} onValueChange={setLimit}>
            <SelectTrigger className="w-[80px] h-10 bg-card/50 border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="50">50</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Results Info */}
        {!loading && results.length > 0 && (
          <p className="text-sm text-muted-foreground">
            {results.length} results for "{searchedQuery}"
          </p>
        )}

        {/* Error */}
        {error && (
          <Card className="border-destructive bg-destructive/10">
            <CardContent className="py-4 text-destructive text-sm flex items-center gap-2">
              <AlertCircle className="size-4" />
              {error}
            </CardContent>
          </Card>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-16">
            <Loader2 className="size-8 mx-auto animate-spin text-muted-foreground" />
            <p className="text-muted-foreground mt-4">Searching...</p>
          </div>
        )}

        {/* Results */}
        <div className="space-y-4">
          {results.map((result) => {
            const typeStyle = getTypeStyle(result.resource_type);
            const TypeIcon = typeStyle.icon;

            return (
              <Card
                key={result.id}
                className="transition-all hover:shadow-md hover:border-primary/30 group"
              >
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge className={`text-xs gap-1 ${typeStyle.color}`}>
                          <TypeIcon className="size-3" />
                          {result.resource_type}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {result.source}
                        </Badge>
                        {result.score && (
                          <span className="text-xs text-muted-foreground font-mono">
                            {(result.score * 100).toFixed(0)}% match
                          </span>
                        )}
                      </div>
                      <CardTitle className="text-lg leading-snug">
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-primary transition-colors inline-flex items-center gap-1.5 group-hover:underline"
                        >
                          {result.title}
                          <ExternalLink className="size-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </a>
                      </CardTitle>
                      {result.authors && result.authors.length > 0 && (
                        <p className="text-xs text-muted-foreground">
                          By: {result.authors.slice(0, 3).join(", ")}
                          {result.authors.length > 3 &&
                            ` +${result.authors.length - 3} more`}
                        </p>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm leading-relaxed line-clamp-3">
                    {result.summary_preview || result.content}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}

          {/* No Results */}
          {!loading && results.length === 0 && !error && (
            <div className="text-center py-16">
              <div className="text-muted-foreground">
                <Search className="size-12 mx-auto mb-4 opacity-30" />
                <p className="text-lg">
                  No results found for "{searchedQuery}"
                </p>
                {suggestion && (
                  <p className="text-sm mt-2">
                    Did you mean:{" "}
                    <button
                      onClick={handleSuggestionClick}
                      className="text-primary hover:underline font-medium"
                    >
                      {suggestion}
                    </button>
                    ?
                  </p>
                )}
                {!suggestion && (
                  <p className="text-sm mt-1">
                    Try different keywords or adjust your filters
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
