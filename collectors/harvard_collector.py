"""
Harvard CS50 Collector for Atlas Academic Search Engine.
Scrapes course materials from Harvard's CS50 open courseware.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from .base import BaseCollector


class HarvardCollector(BaseCollector):
    """
    Collector for Harvard CS50 course materials.
    CS50 is Harvard's introduction to computer science.
    """
    
    BASE_URL = "https://cs50.harvard.edu"
    
    # CS50x 2024 weekly topics
    WEEKS = [
        {"week": 0, "topic": "Scratch", "url": "/x/2024/weeks/0/"},
        {"week": 1, "topic": "C", "url": "/x/2024/weeks/1/"},
        {"week": 2, "topic": "Arrays", "url": "/x/2024/weeks/2/"},
        {"week": 3, "topic": "Algorithms", "url": "/x/2024/weeks/3/"},
        {"week": 4, "topic": "Memory", "url": "/x/2024/weeks/4/"},
        {"week": 5, "topic": "Data Structures", "url": "/x/2024/weeks/5/"},
        {"week": 6, "topic": "Python", "url": "/x/2024/weeks/6/"},
        {"week": 7, "topic": "SQL", "url": "/x/2024/weeks/7/"},
        {"week": 8, "topic": "HTML, CSS, JavaScript", "url": "/x/2024/weeks/8/"},
        {"week": 9, "topic": "Flask", "url": "/x/2024/weeks/9/"},
        {"week": 10, "topic": "Cybersecurity", "url": "/x/2024/weeks/10/"},
    ]
    
    SYLLABUS_URL = "/x/2024/syllabus/"
    
    def __init__(self):
        super().__init__(name="Harvard CS50")
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
            print(f"[Harvard] Request failed: {e}")
        return None
    
    def _scrape_week(self, week_info: Dict) -> List[Dict[str, Any]]:
        """Scrape a single week's materials."""
        payloads = []
        week_url = urljoin(self.BASE_URL, week_info['url'])
        
        resp = self._safe_get(week_url)
        if not resp:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        week_num = week_info['week']
        topic = week_info['topic']
        title = f"CS50 Week {week_num}: {topic}"
        
        print(f"[Harvard] Scraping: {title}")
        
        # Get page content for description
        main_content = soup.find('main') or soup.find('article')
        description = ""
        if main_content:
            # Get first few paragraphs
            paragraphs = main_content.find_all('p')[:3]
            description = " ".join(p.get_text(strip=True) for p in paragraphs)[:500]
        
        if not description:
            description = f"Introduction to {topic} in computer science."
        
        # Look for Notes, Slides, and other materials
        materials_found = False
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()
            
            # Look for notes, slides, shorts
            if any(x in link_text for x in ['notes', 'slides', 'shorts', 'pdf']):
                full_url = urljoin(self.BASE_URL, href)
                
                if not self.is_new(full_url):
                    continue
                
                if 'slides' in link_text:
                    resource_type = "Lecture Slides"
                    material_title = f"{title} - Slides"
                elif 'notes' in link_text:
                    resource_type = "Course Notes"
                    material_title = f"{title} - Notes"
                else:
                    resource_type = "Course Notes"
                    material_title = f"{title} - {link_text.title()}"
                
                payload = self.create_payload(
                    title=material_title,
                    summary=f"Harvard CS50 material for Week {week_num}: {topic}. {description[:200]}",
                    authors=["David J. Malan"],
                    url=full_url,
                    source="Harvard CS50",
                    resource_type=resource_type
                )
                
                payloads.append(payload)
                materials_found = True
                print(f"[Harvard] Collected: {material_title[:60]}...")
        
        # If no specific materials, add the week page itself
        if not materials_found:
            payload = self.create_payload(
                title=title,
                summary=f"Harvard CS50 Week {week_num} covering {topic}. {description}",
                authors=["David J. Malan"],
                url=week_url,
                source="Harvard CS50",
                resource_type="Course Notes"
            )
            payloads.append(payload)
            print(f"[Harvard] Collected week page: {title}")
        
        return payloads
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from Harvard CS50."""
        payloads = []
        
        # Collect syllabus first
        syllabus_url = urljoin(self.BASE_URL, self.SYLLABUS_URL)
        if self.is_new(syllabus_url):
            payload = self.create_payload(
                title="CS50: Introduction to Computer Science - Syllabus",
                summary="Harvard University's introduction to the intellectual enterprises of computer science "
                        "and the art of programming. Topics include abstraction, algorithms, data structures, "
                        "encapsulation, resource management, security, software engineering, and web programming.",
                authors=["David J. Malan"],
                url=syllabus_url,
                source="Harvard CS50",
                resource_type="Syllabus"
            )
            payloads.append(payload)
            print("[Harvard] Collected: CS50 Syllabus")
        
        # Collect weekly materials
        for week in self.WEEKS:
            if len(payloads) >= limit:
                break
            payloads.extend(self._scrape_week(week))
        
        return payloads[:limit]
