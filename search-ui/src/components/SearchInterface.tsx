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
  content: string;
  source: string;
  resource_type: string;
  authors: string[];
  score: number;
  summary_preview?: string;
}

const API_URL = "http://localhost:8000";

// Resource type badge styles
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
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [limit, setLimit] = useState<string>("10");
  const [resourceType, setResourceType] = useState<string>("All");

  // UX State
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");
  const [error, setError] = useState("");

  // On mount: Check Backend Health
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
      } else {
        console.error("Expected array but got:", data);
        setResults([]);
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

  const getTypeStyle = (type: string) => {
    return TYPE_STYLES[type] || TYPE_STYLES.Paper;
  };

  return (
    <div className="dark w-full min-h-screen bg-background py-12 px-4">
      <div className="w-full max-w-4xl mx-auto space-y-8">
        {/* Header & Status */}
        <div className="flex justify-between items-center border-b border-border pb-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground tracking-tight">
              🎓 Atlas
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

        {/* Search Form */}
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

          {/* Filters Row */}
          <div className="flex gap-3 items-center">
            <span className="text-sm text-muted-foreground">Filter by:</span>

            <Select value={resourceType} onValueChange={setResourceType}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Resource Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All">All Types</SelectItem>
                <SelectItem value="Paper">📄 Papers</SelectItem>
                <SelectItem value="Lecture Slides">
                  📊 Lecture Slides
                </SelectItem>
                <SelectItem value="Course Notes">📝 Course Notes</SelectItem>
                <SelectItem value="Syllabus">📋 Syllabus</SelectItem>
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

        {/* Error Message */}
        {error && (
          <Card className="border-destructive bg-destructive/10">
            <CardContent className="py-4 text-destructive text-sm flex items-center gap-2">
              <AlertCircle className="size-4" />
              {error}
            </CardContent>
          </Card>
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
                      {/* Badges Row */}
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge className={`text-xs gap-1 ${typeStyle.color}`}>
                          <TypeIcon className="size-3" />
                          {result.resource_type}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {result.source}
                        </Badge>
                        <span className="text-xs text-muted-foreground font-mono">
                          {(result.score * 100).toFixed(0)}% match
                        </span>
                      </div>

                      {/* Title */}
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

                      {/* Authors */}
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

          {/* Empty State */}
          {!loading && hasSearched && results.length === 0 && !error && (
            <div className="text-center py-16">
              <div className="text-muted-foreground">
                <Search className="size-12 mx-auto mb-4 opacity-30" />
                <p className="text-lg">No results found for "{query}"</p>
                <p className="text-sm mt-1">
                  Try different keywords or adjust your filters
                </p>
              </div>
            </div>
          )}

          {/* Initial State */}
          {!hasSearched && !loading && (
            <div className="text-center py-16">
              <div className="text-muted-foreground">
                <GraduationCap className="size-12 mx-auto mb-4 opacity-30" />
                <p className="text-lg">Search academic resources</p>
                <p className="text-sm mt-1">
                  Find papers on "machine learning", lectures on "algorithms",
                  or notes on "linear algebra"
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
