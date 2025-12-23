"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Server,
  AlertCircle,
  Loader2,
  ExternalLink,
  FileText,
  BookOpen,
  GraduationCap,
  ClipboardList,
  List,
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

interface BrowseItem {
  id: string;
  title: string;
  source: string;
  resource_type: string;
  url: string;
  authors: string[];
}

const API_URL = "http://localhost:8000";

const TYPE_STYLES: Record<string, { color: string; icon: React.ElementType }> =
  {
    Paper: {
      color: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      icon: FileText,
    },
    "Lecture Slides": {
      color: "bg-orange-500/20 text-orange-400 border-orange-500/30",
      icon: BookOpen,
    },
    "Course Notes": {
      color: "bg-green-500/20 text-green-400 border-green-500/30",
      icon: GraduationCap,
    },
    Syllabus: {
      color: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      icon: ClipboardList,
    },
  };

export default function SearchInterface() {
  const [activeTab, setActiveTab] = useState<"search" | "browse">("search");

  // Search state
  const [query, setQuery] = useState("");
  const [searchedQuery, setSearchedQuery] = useState(""); // The query that was actually searched
  const [results, setResults] = useState<SearchResult[]>([]);
  const [limit, setLimit] = useState<string>("10");
  const [resourceType, setResourceType] = useState<string>("All");
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestion, setSuggestion] = useState<string | null>(null);

  // Browse state
  const [browseItems, setBrowseItems] = useState<BrowseItem[]>([]);
  const [browseLoading, setBrowseLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

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
      } catch (e) {
        setServerStatus("offline");
      }
    }
    checkHealth();
  }, []);

  // Simple spell check - common misspellings
  const getSpellingSuggestion = (term: string): string | null => {
    const corrections: Record<string, string> = {
      algoritm: "algorithm",
      algorythm: "algorithm",
      algroithm: "algorithm",
      machin: "machine",
      machien: "machine",
      learing: "learning",
      learnign: "learning",
      neaural: "neural",
      nueral: "neural",
      netwrok: "network",
      netowrk: "network",
      programing: "programming",
      programmin: "programming",
      optimzation: "optimization",
      optmization: "optimization",
      artifical: "artificial",
      artifcial: "artificial",
      inteligence: "intelligence",
      intelgence: "intelligence",
      structre: "structure",
      struture: "structure",
      databse: "database",
      datbase: "database",
      compuer: "computer",
      computor: "computer",
      cryptogrpahy: "cryptography",
      criptography: "cryptography",
      linera: "linear",
      linaer: "linear",
      algebre: "algebra",
      algerbra: "algebra",
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
    setHasSearched(false);
    setSuggestion(null);
    setSearchedQuery(query.trim()); // Store the query that was searched

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
        setHasSearched(true);

        // If no results, check for spelling suggestion
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
    } catch (err: any) {
      setError(err.message || "Failed to fetch results");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = () => {
    if (suggestion) {
      setQuery(suggestion);
      // Trigger search with the suggestion
      setTimeout(() => {
        const form = document.querySelector("form");
        if (form) form.requestSubmit();
      }, 0);
    }
  };

  const loadBrowseItems = async () => {
    setBrowseLoading(true);
    try {
      const response = await fetch(`${API_URL}/browse?limit=200`);
      const data = await response.json();
      setBrowseItems(data.items || []);
      setTotalCount(data.count || 0);
    } catch (err) {
      console.error("Browse error:", err);
      setBrowseItems([]);
    } finally {
      setBrowseLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "browse" && browseItems.length === 0) {
      loadBrowseItems();
    }
  }, [activeTab]);

  const getTypeStyle = (type: string) => {
    return TYPE_STYLES[type] || TYPE_STYLES.Paper;
  };

  return (
    <div className="dark w-full min-h-screen bg-background py-12 px-4">
      <div className="w-full max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center border-b border-border pb-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground tracking-tight">
              Atlas
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Academic search for papers, lectures, and course materials
            </p>
          </div>

          <div className="flex items-center gap-2 text-sm">
            {serverStatus === "checking" && (
              <Badge variant="outline" className="gap-1.5">
                <Loader2 className="size-3 animate-spin" />
                Connecting...
              </Badge>
            )}
            {serverStatus === "online" && (
              <Badge
                variant="secondary"
                className="gap-1.5 text-green-500 border-green-500/30"
              >
                <Server className="size-3" /> Online
              </Badge>
            )}
            {serverStatus === "offline" && (
              <Badge variant="destructive" className="gap-1.5">
                <AlertCircle className="size-3" /> Offline
              </Badge>
            )}
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-2">
          <Button
            variant={activeTab === "search" ? "default" : "outline"}
            onClick={() => setActiveTab("search")}
            className="gap-2"
          >
            <Search className="size-4" />
            Search
          </Button>
          <Button
            variant={activeTab === "browse" ? "default" : "outline"}
            onClick={() => setActiveTab("browse")}
            className="gap-2"
          >
            <List className="size-4" />
            Browse All ({totalCount || "..."})
          </Button>
        </div>

        {/* Search Tab */}
        {activeTab === "search" && (
          <>
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground size-4" />
                  <Input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search papers, lectures, course notes..."
                    className="pl-10 h-11 text-base"
                  />
                </div>
                <Button
                  type="submit"
                  size="lg"
                  disabled={loading || serverStatus === "offline"}
                  className="h-11 px-6"
                >
                  {loading ? (
                    <>
                      <Loader2 className="size-4 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    "Search"
                  )}
                </Button>
              </div>

              <div className="flex gap-3 items-center">
                <span className="text-sm text-muted-foreground">
                  Filter by:
                </span>
                <Select value={resourceType} onValueChange={setResourceType}>
                  <SelectTrigger className="w-[160px]">
                    <SelectValue placeholder="Resource Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="All">All Types</SelectItem>
                    <SelectItem value="Paper">Papers</SelectItem>
                    <SelectItem value="Lecture Slides">
                      Lecture Slides
                    </SelectItem>
                    <SelectItem value="Course Notes">Course Notes</SelectItem>
                    <SelectItem value="Syllabus">Syllabus</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={limit} onValueChange={setLimit}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="Results" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5">5 results</SelectItem>
                    <SelectItem value="10">10 results</SelectItem>
                    <SelectItem value="20">20 results</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </form>

            {error && (
              <Card className="border-destructive bg-destructive/10">
                <CardContent className="py-4 text-destructive text-sm flex items-center gap-2">
                  <AlertCircle className="size-4" />
                  {error}
                </CardContent>
              </Card>
            )}

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
                            <Badge
                              className={`text-xs gap-1 ${typeStyle.color}`}
                            >
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

              {!loading && hasSearched && results.length === 0 && !error && (
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

              {!hasSearched && !loading && (
                <div className="text-center py-16">
                  <div className="text-muted-foreground">
                    <GraduationCap className="size-12 mx-auto mb-4 opacity-30" />
                    <p className="text-lg">Search academic resources</p>
                    <p className="text-sm mt-1">
                      Find papers on "machine learning", lectures on
                      "algorithms", or notes on "linear algebra"
                    </p>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Browse Tab */}
        {activeTab === "browse" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-muted-foreground">
                Showing {browseItems.length} indexed resources
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={loadBrowseItems}
                disabled={browseLoading}
              >
                {browseLoading ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  "Refresh"
                )}
              </Button>
            </div>

            {browseLoading ? (
              <div className="text-center py-16">
                <Loader2 className="size-8 mx-auto animate-spin text-muted-foreground" />
                <p className="text-muted-foreground mt-4">
                  Loading resources...
                </p>
              </div>
            ) : browseItems.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-muted-foreground">
                  <List className="size-12 mx-auto mb-4 opacity-30" />
                  <p className="text-lg">No resources indexed yet</p>
                  <p className="text-sm mt-1">
                    Run the producer and stream processor to index resources
                  </p>
                </div>
              </div>
            ) : (
              <div className="border rounded-lg divide-y">
                {browseItems.map((item) => {
                  const typeStyle = getTypeStyle(item.resource_type);
                  const TypeIcon = typeStyle.icon;

                  return (
                    <div
                      key={item.id}
                      className="p-4 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1 flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge
                              className={`text-xs gap-1 ${typeStyle.color}`}
                            >
                              <TypeIcon className="size-3" />
                              {item.resource_type}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {item.source}
                            </Badge>
                          </div>
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm font-medium hover:text-primary hover:underline block truncate"
                          >
                            {item.title}
                          </a>
                          {item.authors && item.authors.length > 0 && (
                            <p className="text-xs text-muted-foreground truncate">
                              {item.authors.slice(0, 2).join(", ")}
                            </p>
                          )}
                        </div>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="size-4 text-muted-foreground hover:text-primary" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
