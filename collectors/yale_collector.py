"""
Open Yale Courses Collector for Atlas Academic Search Engine.
Scrapes course materials from Yale's open courseware.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from .base import BaseCollector


class YaleCollector(BaseCollector):
    """
    Collector for Open Yale Courses materials.
    Yale offers courses across many disciplines.
    """
    
    BASE_URL = "https://oyc.yale.edu"
    
    # Popular Yale courses
    COURSES = [
        {"path": "/introduction-psychology", "name": "Introduction to Psychology", "dept": "Psychology"},
        {"path": "/financial-markets", "name": "Financial Markets", "dept": "Economics"},
        {"path": "/game-theory", "name": "Game Theory", "dept": "Economics"},
        {"path": "/fundamentals-physics-i", "name": "Fundamentals of Physics I", "dept": "Physics"},
        {"path": "/fundamentals-physics-ii", "name": "Fundamentals of Physics II", "dept": "Physics"},
        {"path": "/introduction-ancient-greek-history", "name": "Introduction to Ancient Greek History", "dept": "Classics"},
        {"path": "/philosophy-death", "name": "Philosophy of Death", "dept": "Philosophy"},
        {"path": "/introduction-theory-literature", "name": "Introduction to Theory of Literature", "dept": "English"},
    ]
    
    def __init__(self):
        super().__init__(name="Yale OYC")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _safe_get(self, url: str) -> Optional[requests.Response]:
        """Safely fetch a URL."""
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp
        except Exception as e:
            print(f"[Yale] Request failed: {e}")
        return None
    
    def _scrape_course(self, course: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape a single course."""
        payloads = []
        course_url = f"{self.BASE_URL}{course['path']}"
        
        resp = self._safe_get(course_url)
        if not resp:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        course_title = course['name']
        
        print(f"[Yale] Scraping: {course_title}")
        
        # Get course description
        description = ""
        desc_elem = soup.find('div', class_='course-description') or soup.find('div', class_='field-body')
        if desc_elem:
            description = desc_elem.get_text(strip=True)[:500]
        
        # Get instructor
        instructor = "Yale Faculty"
        instructor_elem = soup.find('div', class_='instructor') or soup.find('span', class_='instructor-name')
        if instructor_elem:
            instructor = instructor_elem.get_text(strip=True)
        
        # Look for lecture materials
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True)
            
            # Look for sessions, lectures, transcripts
            if any(x in href.lower() for x in ['session', 'lecture', 'transcript', '.pdf']):
                full_url = urljoin(self.BASE_URL, href)
                
                if not self.is_new(full_url):
                    continue
                
                if 'transcript' in link_text.lower():
                    resource_type = "Course Notes"
                    title = f"{course_title}: {link_text}"
                elif 'lecture' in link_text.lower() or 'session' in link_text.lower():
                    resource_type = "Course Notes"
                    title = f"{course_title}: {link_text}"
                else:
                    resource_type = "Course Notes"
                    title = f"{course_title}: {link_text}" if link_text else f"{course_title}"
                
                summary = f"Yale University {course['dept']} course: {course_title}. " \
                          f"Taught by {instructor}. {description[:200]}"
                
                payload = self.create_payload(
                    title=title,
                    summary=summary,
                    authors=[instructor],
                    url=full_url,
                    source="Yale OYC",
                    resource_type=resource_type
                )
                
                payloads.append(payload)
                print(f"[Yale] Collected: {title[:60]}...")
                
                if len(payloads) >= 10:  # Limit per course
                    break
        
        # If no materials found, add the course page
        if len(payloads) == 0:
            payload = self.create_payload(
                title=course_title,
                summary=f"Yale University {course['dept']} course: {course_title}. "
                        f"Taught by {instructor}. {description}",
                authors=[instructor],
                url=course_url,
                source="Yale OYC",
                resource_type="Course Notes"
            )
            payloads.append(payload)
            print(f"[Yale] Collected course page: {course_title}")
        
        return payloads
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from Open Yale Courses."""
        payloads = []
        
        for course in self.COURSES:
            if len(payloads) >= limit:
                break
            payloads.extend(self._scrape_course(course))
        
        return payloads[:limit]
