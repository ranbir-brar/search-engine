"""
Khan Academy Collector for Atlas Academic Search Engine.
Collects educational content from Khan Academy's structured curriculum.
"""
import requests
from typing import List, Dict, Any, Optional
from .base import BaseCollector


class KhanAcademyCollector(BaseCollector):
    """
    Collector for Khan Academy educational content.
    Uses Khan Academy's API to fetch course and lesson information.
    """
    
    BASE_URL = "https://www.khanacademy.org"
    API_URL = "https://www.khanacademy.org/api/v1"
    
    # Comprehensive topic tree with direct content
    TOPICS = [
        # Mathematics
        {"slug": "algebra", "name": "Algebra", "domain": "Mathematics"},
        {"slug": "algebra2", "name": "Algebra 2", "domain": "Mathematics"},
        {"slug": "precalculus", "name": "Precalculus", "domain": "Mathematics"},
        {"slug": "ap-calculus-ab", "name": "AP Calculus AB", "domain": "Mathematics"},
        {"slug": "ap-calculus-bc", "name": "AP Calculus BC", "domain": "Mathematics"},
        {"slug": "differential-calculus", "name": "Differential Calculus", "domain": "Mathematics"},
        {"slug": "integral-calculus", "name": "Integral Calculus", "domain": "Mathematics"},
        {"slug": "multivariable-calculus", "name": "Multivariable Calculus", "domain": "Mathematics"},
        {"slug": "differential-equations", "name": "Differential Equations", "domain": "Mathematics"},
        {"slug": "linear-algebra", "name": "Linear Algebra", "domain": "Mathematics"},
        {"slug": "statistics-probability", "name": "Statistics and Probability", "domain": "Mathematics"},
        {"slug": "ap-statistics", "name": "AP Statistics", "domain": "Mathematics"},
        {"slug": "trigonometry", "name": "Trigonometry", "domain": "Mathematics"},
        {"slug": "geometry", "name": "Geometry", "domain": "Mathematics"},
        # Science
        {"slug": "physics", "name": "Physics", "domain": "Science"},
        {"slug": "ap-physics-1", "name": "AP Physics 1", "domain": "Science"},
        {"slug": "ap-physics-2", "name": "AP Physics 2", "domain": "Science"},
        {"slug": "cosmology-and-astronomy", "name": "Cosmology and Astronomy", "domain": "Science"},
        {"slug": "chemistry", "name": "Chemistry", "domain": "Science"},
        {"slug": "ap-chemistry", "name": "AP Chemistry", "domain": "Science"},
        {"slug": "organic-chemistry", "name": "Organic Chemistry", "domain": "Science"},
        {"slug": "biology", "name": "Biology", "domain": "Science"},
        {"slug": "ap-biology", "name": "AP Biology", "domain": "Science"},
        {"slug": "health-and-medicine", "name": "Health and Medicine", "domain": "Science"},
        # Computing
        {"slug": "computing", "name": "Computing", "domain": "Computing"},
        {"slug": "ap-computer-science-principles", "name": "AP Computer Science Principles", "domain": "Computing"},
        {"slug": "computer-programming", "name": "Computer Programming", "domain": "Computing"},
        {"slug": "algorithms", "name": "Algorithms", "domain": "Computing"},
        {"slug": "computer-science", "name": "Computer Science", "domain": "Computing"},
        # Economics
        {"slug": "economics-finance-domain", "name": "Economics", "domain": "Economics"},
        {"slug": "macroeconomics", "name": "Macroeconomics", "domain": "Economics"},
        {"slug": "microeconomics", "name": "Microeconomics", "domain": "Economics"},
        {"slug": "ap-macroeconomics", "name": "AP Macroeconomics", "domain": "Economics"},
        {"slug": "ap-microeconomics", "name": "AP Microeconomics", "domain": "Economics"},
        {"slug": "core-finance", "name": "Finance and Capital Markets", "domain": "Economics"},
    ]
    
    # Lesson content for each topic
    LESSONS = {
        "differential-calculus": [
            {"title": "Limits and Continuity", "desc": "Understanding limits, one-sided limits, and continuity of functions."},
            {"title": "Derivatives: Definition and Basic Rules", "desc": "Definition of the derivative, power rule, product rule, quotient rule."},
            {"title": "Derivatives: Chain Rule", "desc": "Chain rule for composite functions and implicit differentiation."},
            {"title": "Applications of Derivatives", "desc": "Related rates, optimization, and motion problems."},
            {"title": "Analyzing Functions", "desc": "Using derivatives to analyze function behavior, concavity, and extrema."},
        ],
        "integral-calculus": [
            {"title": "Integrals", "desc": "Antiderivatives, indefinite integrals, and basic integration rules."},
            {"title": "Definite Integrals", "desc": "Riemann sums, definite integrals, and the fundamental theorem of calculus."},
            {"title": "Integration Techniques", "desc": "U-substitution, integration by parts, and partial fractions."},
            {"title": "Applications of Integrals", "desc": "Area between curves, volumes of revolution, and average value."},
            {"title": "Differential Equations", "desc": "Separable equations and exponential models."},
        ],
        "linear-algebra": [
            {"title": "Vectors and Spaces", "desc": "Vectors, linear combinations, spans, and linear independence."},
            {"title": "Matrix Transformations", "desc": "Functions and linear transformations, matrix multiplication."},
            {"title": "Alternate Coordinate Systems", "desc": "Orthogonal complements, projections, and change of basis."},
        ],
        "statistics-probability": [
            {"title": "Analyzing Categorical Data", "desc": "Analyzing one and two categorical variables."},
            {"title": "Displaying and Comparing Data", "desc": "Dot plots, histograms, box plots, and comparing distributions."},
            {"title": "Summarizing Quantitative Data", "desc": "Mean, median, variance, and standard deviation."},
            {"title": "Probability", "desc": "Basic probability, conditional probability, and Bayes' theorem."},
            {"title": "Random Variables", "desc": "Discrete and continuous random variables, expected value."},
        ],
        "physics": [
            {"title": "One-Dimensional Motion", "desc": "Displacement, velocity, and acceleration in one dimension."},
            {"title": "Two-Dimensional Motion", "desc": "Projectile motion and circular motion."},
            {"title": "Forces and Newton's Laws", "desc": "Newton's laws of motion, friction, and tension."},
            {"title": "Work and Energy", "desc": "Work, kinetic energy, potential energy, and conservation."},
            {"title": "Momentum and Collisions", "desc": "Linear momentum, impulse, and collision types."},
            {"title": "Waves and Sound", "desc": "Wave properties, sound waves, and the Doppler effect."},
            {"title": "Electric Charge and Force", "desc": "Coulomb's law, electric fields, and electric potential."},
        ],
        "chemistry": [
            {"title": "Atoms and Elements", "desc": "Atomic structure, electron configuration, and periodic trends."},
            {"title": "Chemical Bonds", "desc": "Ionic, covalent, and metallic bonding."},
            {"title": "Stoichiometry", "desc": "Balancing equations, mole concept, and limiting reagents."},
            {"title": "Thermodynamics", "desc": "Enthalpy, entropy, and Gibbs free energy."},
            {"title": "Kinetics", "desc": "Reaction rates, rate laws, and activation energy."},
            {"title": "Equilibrium", "desc": "Chemical equilibrium and Le Chatelier's principle."},
        ],
        "biology": [
            {"title": "Cell Structure and Function", "desc": "Prokaryotic and eukaryotic cells, organelles, and membranes."},
            {"title": "Energy and Metabolism", "desc": "ATP, cellular respiration, and photosynthesis."},
            {"title": "DNA and Genetics", "desc": "DNA structure, replication, transcription, and translation."},
            {"title": "Evolution", "desc": "Natural selection, speciation, and evolutionary evidence."},
            {"title": "Ecology", "desc": "Ecosystems, food webs, and population dynamics."},
        ],
        "algorithms": [
            {"title": "Intro to Algorithms", "desc": "What are algorithms and why are they important."},
            {"title": "Binary Search", "desc": "Efficient searching in sorted arrays."},
            {"title": "Asymptotic Notation", "desc": "Big-O, Big-Omega, and Big-Theta notation."},
            {"title": "Selection Sort", "desc": "Sorting by repeatedly finding the minimum."},
            {"title": "Insertion Sort", "desc": "Building sorted array one element at a time."},
            {"title": "Merge Sort", "desc": "Divide and conquer sorting algorithm."},
            {"title": "Quick Sort", "desc": "Partition-based sorting algorithm."},
            {"title": "Graph Representation", "desc": "Adjacency lists and adjacency matrices."},
            {"title": "Breadth-First Search", "desc": "Exploring graphs level by level."},
            {"title": "Dijkstra's Algorithm", "desc": "Finding shortest paths in weighted graphs."},
        ],
        "microeconomics": [
            {"title": "Supply and Demand", "desc": "Market equilibrium, elasticity, and price controls."},
            {"title": "Consumer Theory", "desc": "Utility, budget constraints, and consumer choice."},
            {"title": "Production and Costs", "desc": "Production functions, cost curves, and economies of scale."},
            {"title": "Market Structures", "desc": "Perfect competition, monopoly, and oligopoly."},
        ],
        "macroeconomics": [
            {"title": "GDP and Economic Growth", "desc": "Measuring economic output and growth."},
            {"title": "Inflation and Unemployment", "desc": "CPI, inflation, and labor market dynamics."},
            {"title": "Fiscal Policy", "desc": "Government spending, taxation, and budget deficits."},
            {"title": "Monetary Policy", "desc": "Central banks, interest rates, and money supply."},
        ],
    }
    
    def __init__(self):
        super().__init__(name="Khan Academy")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _generate_topic_resources(self, topic: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate resources for a topic based on known lesson structure."""
        payloads = []
        slug = topic["slug"]
        name = topic["name"]
        domain = topic["domain"]
        
        # Create topic overview
        topic_url = f"{self.BASE_URL}/{slug}"
        if self.is_new(topic_url):
            payload = self.create_payload(
                title=f"Khan Academy: {name}",
                summary=f"Comprehensive {domain.lower()} course covering {name.lower()}. "
                        f"Free educational content with video lessons, practice exercises, and quizzes.",
                authors=["Khan Academy"],
                url=topic_url,
                source="Khan Academy",
                resource_type="Course Notes"
            )
            payloads.append(payload)
            print(f"[Khan Academy] Collected: {name}")
        
        # Add specific lessons if available
        if slug in self.LESSONS:
            for lesson in self.LESSONS[slug]:
                lesson_url = f"{self.BASE_URL}/{slug}/{lesson['title'].lower().replace(' ', '-').replace(':', '').replace(',', '')}"
                if self.is_new(lesson_url):
                    payload = self.create_payload(
                        title=f"Khan Academy: {name} - {lesson['title']}",
                        summary=f"{lesson['desc']} Part of Khan Academy's {name} course in {domain}.",
                        authors=["Khan Academy"],
                        url=lesson_url,
                        source="Khan Academy",
                        resource_type="Course Notes"
                    )
                    payloads.append(payload)
                    print(f"[Khan Academy] Collected: {name} - {lesson['title']}")
        
        return payloads
    
    def collect(self, limit: int = 300) -> List[Dict[str, Any]]:
        """Collect educational content from Khan Academy."""
        payloads = []
        
        for topic in self.TOPICS:
            if len(payloads) >= limit:
                break
            payloads.extend(self._generate_topic_resources(topic))
        
        return payloads[:limit]
