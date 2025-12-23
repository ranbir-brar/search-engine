"""
Stanford Engineering Everywhere Collector for Atlas Academic Search Engine.
Scrapes course materials from Stanford's open courseware platform.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from .base import BaseCollector


class StanfordCollector(BaseCollector):
    """
    Collector for Stanford Engineering Everywhere (SEE) materials.
    """
    
    BASE_URL = "https://see.stanford.edu"
    
    # Courses available on SEE with instructor info
    COURSES = [
        {"code": "CS106A", "name": "Programming Methodology", "instructor": "Mehran Sahami"},
        {"code": "CS106B", "name": "Programming Abstractions", "instructor": "Julie Zelenski"},
        {"code": "CS107", "name": "Programming Paradigms", "instructor": "Jerry Cain"},
        {"code": "CS223A", "name": "Introduction to Robotics", "instructor": "Oussama Khatib"},
        {"code": "CS229", "name": "Machine Learning", "instructor": "Andrew Ng"},
        {"code": "EE261", "name": "The Fourier Transform and its Applications", "instructor": "Brad Osgood"},
        {"code": "EE263", "name": "Introduction to Linear Dynamical Systems", "instructor": "Stephen Boyd"},
        {"code": "EE364A", "name": "Convex Optimization I", "instructor": "Stephen Boyd"},
        {"code": "EE364B", "name": "Convex Optimization II", "instructor": "Stephen Boyd"},
    ]
    
    def __init__(self):
        super().__init__(name="Stanford SEE")
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
            print(f"[Stanford] Request failed: {e}")
        return None
    
    def _scrape_course(self, course: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape a single course for materials."""
        payloads = []
        course_url = f"{self.BASE_URL}/Course/{course['code']}"
        
        resp = self._safe_get(course_url)
        if not resp:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        course_title = f"{course['code']}: {course['name']}"
        
        print(f"[Stanford] Scraping: {course_title}")
        
        # Look for lecture/material links
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True)
            
            # Look for materials, handouts, transcripts
            if any(x in href.lower() for x in ['materials', 'handout', 'transcript', '.pdf']):
                full_url = urljoin(self.BASE_URL, href)
                
                if not self.is_new(full_url):
                    continue
                
                # Determine resource type
                if 'transcript' in href.lower() or 'transcript' in link_text.lower():
                    resource_type = "Course Notes"
                    title = f"{course_title}: Video Transcript"
                elif '.pdf' in href.lower():
                    resource_type = "Course Notes"
                    title = f"{course_title}: {link_text}" if link_text else f"{course_title}: Handout"
                else:
                    resource_type = "Course Notes"
                    title = f"{course_title}: {link_text}" if link_text else f"{course_title}: Material"
                
                summary = f"Stanford University course material from {course['name']} ({course['code']}), " \
                          f"taught by Professor {course['instructor']}."
                
                payload = self.create_payload(
                    title=title,
                    summary=summary,
                    authors=[course['instructor']],
                    url=full_url,
                    source="Stanford SEE",
                    resource_type=resource_type
                )
                
                payloads.append(payload)
                print(f"[Stanford] Collected: {title[:60]}...")
        
        # If no materials found, create an entry for the course itself
        if len(payloads) == 0:
            summary = f"Stanford University course: {course['name']} ({course['code']}). " \
                      f"Taught by Professor {course['instructor']}. " \
                      f"Topics include {course['name'].lower()} fundamentals and advanced concepts."
            
            payload = self.create_payload(
                title=course_title,
                summary=summary,
                authors=[course['instructor']],
                url=course_url,
                source="Stanford SEE",
                resource_type="Course Notes"
            )
            payloads.append(payload)
            print(f"[Stanford] Collected course page: {course_title}")
        
        return payloads
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from Stanford SEE."""
        payloads = []
        
        for course in self.COURSES:
            if len(payloads) >= limit:
                break
            payloads.extend(self._scrape_course(course))
        
        return payloads[:limit]
