"""
GitHub Course Notes Collector for Atlas Course Materials Search Engine.
Crawls GitHub repos containing university course notes and materials.
"""
import requests
import os
from typing import List, Dict, Any
import time
import re
from .base import BaseCollector


class GitHubNotesCollector(BaseCollector):
    """
    Collector for course notes from GitHub repositories.
    Uses GitHub API to find PDFs and markdown files in course-related repos.
    """
    
    # Known repos with course materials (curated list)
    COURSE_REPOS = [
        # Waterloo
        {"owner": "Dakkers", "repo": "UW-Course-Notes", "school": "Waterloo"},
        {"owner": "Uberi", "repo": "University-Notes", "school": "Waterloo"},
        {"owner": "aaronabraham311", "repo": "Notes", "school": "Waterloo"},
        
        # UofT
        {"owner": "ICPRplshelp", "repo": "UofT-Notes", "school": "UofT"},
        {"owner": "tingfengx", "repo": "uoftnotes", "school": "UofT"},
        
        # UC Berkeley
        {"owner": "64bitpandas", "repo": "notes", "school": "Berkeley"},
        {"owner": "aparande", "repo": "BerkeleyNotes", "school": "Berkeley"},
        
        # McGill
        {"owner": "francis-piche", "repo": "study-guides-mcgill", "school": "McGill"},
        {"owner": "kraglalbert", "repo": "mcgill-swe-class-notes", "school": "McGill"},
    ]


    
    # File extensions to collect
    VALID_EXTENSIONS = ['.pdf', '.md', '.tex', '.ipynb']
    
    # Keywords for filtering relevant files
    CONTENT_KEYWORDS = [
        'lecture', 'notes', 'slides', 'assignment', 'homework', 'pset',
        'exam', 'midterm', 'final', 'solution', 'chapter', 'week'
    ]
    
    def __init__(self):
        super().__init__(name="GitHub Notes")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Atlas-Course-Collector"
        })
        # Use GitHub token for higher rate limits (5000/hr vs 60/hr)
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            self.session.headers["Authorization"] = f"token {github_token}"
            print("[GitHub] Using authenticated requests (5000/hr limit)")
    
    def _get_repo_files(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get files from a GitHub repo using the contents API."""
        files = []
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code == 403:
                print(f"[GitHub] Rate limited, waiting...")
                time.sleep(60)
                return files
            
            if resp.status_code != 200:
                return files
            
            items = resp.json()
            if not isinstance(items, list):
                return files
            
            for item in items:
                if item["type"] == "file":
                    files.append(item)
                elif item["type"] == "dir" and len(files) < 100:
                    # Recurse into directories (with limit)
                    time.sleep(0.5)  # Rate limiting
                    files.extend(self._get_repo_files(owner, repo, item["path"]))
            
        except Exception as e:
            print(f"[GitHub] Error fetching {owner}/{repo}/{path}: {e}")
        
        return files
    
    def _classify_file(self, filename: str, path: str) -> str:
        """Classify file type based on name."""
        text = (filename + " " + path).lower()
        
        if any(kw in text for kw in ['exam', 'midterm', 'final', 'quiz']):
            return "Exam"
        elif any(kw in text for kw in ['solution', 'answer', 'sol']):
            return "Solutions"
        elif any(kw in text for kw in ['assignment', 'homework', 'pset', 'hw']):
            return "Problem Set"
        elif any(kw in text for kw in ['slide', 'lecture', 'lec']):
            return "Lecture Slides"
        else:
            return "Course Notes"
    
    def _is_relevant_file(self, filename: str, path: str) -> bool:
        """Check if file is likely course material."""
        # Check extension
        ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        if ext not in self.VALID_EXTENSIONS:
            return False
        
        # Check for content keywords (optional, can be relaxed)
        text = (filename + " " + path).lower()
        return True  # Accept all PDFs/MDs in course repos
    
    def _extract_course_name(self, path: str, filename: str, repo: str) -> str:
        """Extract course name from path - checks all path components."""
        # Common course code patterns: CS135, MATH 135, ECE124, etc.
        course_pattern = r'([A-Z]{2,4})\s*[-_]?\s*(\d{2,4}[A-Z]?)'
        
        # Check full path for course code
        full_text = path.upper()
        match = re.search(course_pattern, full_text)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        
        # Check filename without extension
        basename = filename.rsplit('.', 1)[0].upper()
        match = re.search(course_pattern, basename)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        
        # Check if filename looks like "135_Notes" -> might be course number
        # Try to extract from parent directory
        path_parts = path.split('/')
        for part in path_parts:
            match = re.search(course_pattern, part.upper())
            if match:
                return f"{match.group(1)} {match.group(2)}"
        
        # Fall back to repo name
        return repo.replace('-', ' ').replace('_', ' ').title()
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from GitHub repos."""
        payloads = []
        
        for repo_info in self.COURSE_REPOS:
            if len(payloads) >= limit:
                break
            
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            school = repo_info["school"]
            
            print(f"[GitHub] Scanning {owner}/{repo}...")
            
            files = self._get_repo_files(owner, repo)
            
            for file in files:
                if len(payloads) >= limit:
                    break
                
                filename = file.get("name", "")
                path = file.get("path", "")
                html_url = file.get("html_url", "")
                download_url = file.get("download_url", "")
                
                if not self._is_relevant_file(filename, path):
                    continue
                
                if not self.is_new(html_url):
                    continue
                
                try:
                    course_name = self._extract_course_name(path, filename, repo)
                    resource_type = self._classify_file(filename, path)
                    
                    # Use html_url (GitHub blob view) so users view instead of download
                    url = html_url
                    
                    # Better title with course code prominently displayed
                    title = f"{school} {course_name}: {filename}"
                    summary = f"Course notes for {course_name} from {school}. File: {filename}. Path: {path}"
                    
                    payload = self.create_payload(
                        title=title,
                        summary=summary,
                        authors=[school, owner],
                        url=url,
                        source=school,
                        resource_type=resource_type
                    )
                    payloads.append(payload)
                    print(f"[GitHub] Found: {filename[:40]}... ({resource_type})")
                    
                except Exception as e:
                    print(f"[GitHub] Error processing {filename}: {e}")
            
            # Rate limiting between repos
            time.sleep(1)
        
        return payloads[:limit]
