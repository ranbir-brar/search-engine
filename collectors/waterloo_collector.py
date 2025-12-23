"""
University of Waterloo Collector for Atlas Course Materials Search Engine.
Collects course materials from UWaterloo CS and Math departments.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin
from .base import BaseCollector


class WaterlooCollector(BaseCollector):
    """
    Collector for University of Waterloo course materials.
    Focuses on CS and Math course notes publicly available.
    """
    
    BASE_URL = "https://cs.uwaterloo.ca"
    
    # Known public course materials
    COURSES = [
        # CS Courses with public materials
        {
            "code": "CS 135",
            "name": "Designing Functional Programs",
            "url": "https://cs.uwaterloo.ca/~cbrMDlly/cs135/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CS 136",
            "name": "Elementary Algorithm Design and Data Abstraction",
            "url": "https://cs.uwaterloo.ca/~cs136/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CS 240",
            "name": "Data Structures and Data Management",
            "url": "https://cs.uwaterloo.ca/~shallit/Courses/240/",
            "instructor": "Jeffrey Shallit",
        },
        {
            "code": "CS 241",
            "name": "Foundations of Sequential Programs",
            "url": "https://cs.uwaterloo.ca/~cs241/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CS 341",
            "name": "Algorithms",
            "url": "https://cs.uwaterloo.ca/~eblais/cs341/",
            "instructor": "Eric Blais",
        },
        {
            "code": "CS 350",
            "name": "Operating Systems",
            "url": "https://cs.uwaterloo.ca/~brecht/courses/cs350/",
            "instructor": "Tim Brecht",
        },
        {
            "code": "CS 370",
            "name": "Numerical Computation",
            "url": "https://cs.uwaterloo.ca/~cs370/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CS 442",
            "name": "Principles of Programming Languages",
            "url": "https://cs.uwaterloo.ca/~plragde/442/",
            "instructor": "Prabhakar Ragde",
        },
        {
            "code": "CS 444",
            "name": "Compiler Construction",
            "url": "https://cs.uwaterloo.ca/~cs444/",
            "instructor": "CS Faculty",
        },
        {
            "code": "CS 466",
            "name": "Algorithm Design and Analysis",
            "url": "https://cs.uwaterloo.ca/~shallit/Courses/466/",
            "instructor": "Jeffrey Shallit",
        },
        # Math Courses
        {
            "code": "MATH 135",
            "name": "Algebra for Honours Mathematics",
            "url": "https://www.math.uwaterloo.ca/~snburris/htdocs/lp.html",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 136",
            "name": "Linear Algebra 1 for Honours Mathematics",
            "url": "https://www.math.uwaterloo.ca/~lwmarcou/courses/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 137",
            "name": "Calculus 1 for Honours Mathematics",
            "url": "https://www.math.uwaterloo.ca/~baMDld/MATH137/",
            "instructor": "Math Faculty",
        },
        {
            "code": "MATH 138",
            "name": "Calculus 2 for Honours Mathematics",
            "url": "https://www.math.uwaterloo.ca/~badubc/MATH138/",
            "instructor": "Math Faculty",
        },
        {
            "code": "CO 250",
            "name": "Introduction to Optimization",
            "url": "https://www.math.uwaterloo.ca/~bico/",
            "instructor": "Math Faculty",
        },
        {
            "code": "STAT 230",
            "name": "Probability",
            "url": "https://www.math.uwaterloo.ca/~dlmcleis/stat230/",
            "instructor": "Don McLeish",
        },
        {
            "code": "STAT 231",
            "name": "Statistics",
            "url": "https://www.math.uwaterloo.ca/~dlmcleis/stat231/",
            "instructor": "Don McLeish",
        },
    ]
    
    def __init__(self):
        super().__init__(name="UWaterloo")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _create_course_entry(self, course: Dict[str, str]) -> Dict[str, Any]:
        """Create a payload for a course."""
        title = f"{course['code']}: {course['name']}"
        summary = (
            f"University of Waterloo course: {course['name']} ({course['code']}). "
            f"This course is part of Waterloo's rigorous Computer Science and Mathematics programs, "
            f"known for producing top-tier software engineers and mathematicians."
        )
        
        return self.create_payload(
            title=title,
            summary=summary,
            authors=[course["instructor"]],
            url=course["url"],
            source="UWaterloo",
            resource_type="Course Notes"
        )
    
    def collect(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect course materials from UWaterloo."""
        payloads = []
        
        for course in self.COURSES:
            if len(payloads) >= limit:
                break
            
            if not self.is_new(course["url"]):
                continue
            
            try:
                payload = self._create_course_entry(course)
                payloads.append(payload)
                print(f"[UWaterloo] Collected: {course['code']}")
            except Exception as e:
                print(f"[UWaterloo] Error with {course['code']}: {e}")
        
        return payloads[:limit]
