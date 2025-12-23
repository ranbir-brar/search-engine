"""
OpenStax Collector for Atlas Academic Search Engine.
Collects educational textbook content from OpenStax free textbooks.
"""
import requests
from typing import List, Dict, Any, Optional
from .base import BaseCollector


class OpenStaxCollector(BaseCollector):
    """
    Collector for OpenStax free textbook content.
    OpenStax provides peer-reviewed, openly licensed textbooks.
    """
    
    BASE_URL = "https://openstax.org"
    
    # OpenStax textbooks with chapter structures
    TEXTBOOKS = [
        # Mathematics
        {
            "slug": "calculus-volume-1",
            "title": "Calculus Volume 1",
            "subject": "Mathematics",
            "chapters": [
                "Functions and Graphs",
                "Limits",
                "Derivatives",
                "Applications of Derivatives",
                "Integration",
                "Applications of Integration",
            ]
        },
        {
            "slug": "calculus-volume-2",
            "title": "Calculus Volume 2",
            "subject": "Mathematics",
            "chapters": [
                "Integration Techniques",
                "Introduction to Differential Equations",
                "Sequences and Series",
                "Power Series",
                "Parametric Equations and Polar Coordinates",
            ]
        },
        {
            "slug": "calculus-volume-3",
            "title": "Calculus Volume 3",
            "subject": "Mathematics",
            "chapters": [
                "Vectors in Space",
                "Vector-Valued Functions",
                "Differentiation of Functions of Several Variables",
                "Multiple Integration",
                "Vector Calculus",
                "Second-Order Differential Equations",
            ]
        },
        {
            "slug": "algebra-and-trigonometry",
            "title": "Algebra and Trigonometry",
            "subject": "Mathematics",
            "chapters": [
                "Prerequisites",
                "Equations and Inequalities",
                "Functions",
                "Linear Functions",
                "Polynomial and Rational Functions",
                "Exponential and Logarithmic Functions",
                "Trigonometric Functions",
                "Periodic Functions",
                "Trigonometric Identities and Equations",
            ]
        },
        {
            "slug": "introductory-statistics",
            "title": "Introductory Statistics",
            "subject": "Mathematics",
            "chapters": [
                "Sampling and Data",
                "Descriptive Statistics",
                "Probability Topics",
                "Discrete Random Variables",
                "Continuous Random Variables",
                "The Normal Distribution",
                "The Central Limit Theorem",
                "Confidence Intervals",
                "Hypothesis Testing",
                "Linear Regression and Correlation",
            ]
        },
        {
            "slug": "prealgebra",
            "title": "Prealgebra",
            "subject": "Mathematics",
            "chapters": [
                "Whole Numbers",
                "The Language of Algebra",
                "Integers",
                "Fractions",
                "Decimals",
                "Percents",
                "Properties of Real Numbers",
                "Equations",
            ]
        },
        # Physics
        {
            "slug": "college-physics",
            "title": "College Physics",
            "subject": "Physics",
            "chapters": [
                "Introduction: The Nature of Science and Physics",
                "Kinematics",
                "Two-Dimensional Kinematics",
                "Dynamics: Force and Newton's Laws of Motion",
                "Friction, Drag, and Elasticity",
                "Work, Energy, and Energy Resources",
                "Linear Momentum and Collisions",
                "Statics and Torque",
                "Rotational Motion and Angular Momentum",
                "Fluid Statics",
                "Fluid Dynamics",
                "Temperature, Kinetic Theory, and Gas Laws",
                "Heat and Heat Transfer Methods",
                "Thermodynamics",
                "Oscillatory Motion and Waves",
                "Physics of Hearing",
                "Electric Charge and Electric Field",
                "Electric Potential and Electric Field",
            ]
        },
        {
            "slug": "university-physics-volume-1",
            "title": "University Physics Volume 1",
            "subject": "Physics",
            "chapters": [
                "Units and Measurement",
                "Vectors",
                "Motion Along a Straight Line",
                "Motion in Two and Three Dimensions",
                "Newton's Laws of Motion",
                "Applications of Newton's Laws",
                "Work and Kinetic Energy",
                "Potential Energy and Conservation of Energy",
                "Linear Momentum and Collisions",
                "Fixed-Axis Rotation",
                "Angular Momentum",
                "Static Equilibrium and Elasticity",
            ]
        },
        {
            "slug": "university-physics-volume-2",
            "title": "University Physics Volume 2",
            "subject": "Physics",
            "chapters": [
                "Temperature and Heat",
                "The Kinetic Theory of Gases",
                "The First Law of Thermodynamics",
                "The Second Law of Thermodynamics",
                "Electric Charges and Fields",
                "Gauss's Law",
                "Electric Potential",
                "Capacitance",
                "Current and Resistance",
                "Direct-Current Circuits",
                "Magnetic Forces and Fields",
                "Sources of Magnetic Fields",
                "Electromagnetic Induction",
            ]
        },
        {
            "slug": "university-physics-volume-3",
            "title": "University Physics Volume 3",
            "subject": "Physics",
            "chapters": [
                "The Nature of Light",
                "Geometric Optics and Image Formation",
                "Interference",
                "Diffraction",
                "Relativity",
                "Photons and Matter Waves",
                "Quantum Mechanics",
                "Atomic Structure",
                "Condensed Matter Physics",
                "Nuclear Physics",
                "Particle Physics and Cosmology",
            ]
        },
        # Chemistry
        {
            "slug": "chemistry-2e",
            "title": "Chemistry 2e",
            "subject": "Chemistry",
            "chapters": [
                "Essential Ideas",
                "Atoms, Molecules, and Ions",
                "Composition of Substances and Solutions",
                "Stoichiometry of Chemical Reactions",
                "Thermochemistry",
                "Electronic Structure and Periodic Properties",
                "Chemical Bonding and Molecular Geometry",
                "Advanced Theories of Covalent Bonding",
                "Gases",
                "Liquids and Solids",
                "Solutions and Colloids",
                "Kinetics",
                "Fundamental Equilibrium Concepts",
                "Acid-Base Equilibria",
                "Equilibria of Other Reaction Classes",
                "Electrochemistry",
            ]
        },
        {
            "slug": "organic-chemistry",
            "title": "Organic Chemistry",
            "subject": "Chemistry",
            "chapters": [
                "Structure and Bonding",
                "Polar Covalent Bonds; Acids and Bases",
                "Organic Compounds: Alkanes and Their Stereochemistry",
                "Stereochemistry of Alkanes and Cycloalkanes",
                "An Overview of Organic Reactions",
                "Alkenes: Structure and Reactivity",
                "Alkenes: Reactions and Synthesis",
                "Alkynes: An Introduction to Organic Synthesis",
                "Stereochemistry",
                "Organohalides",
            ]
        },
        # Biology
        {
            "slug": "biology-2e",
            "title": "Biology 2e",
            "subject": "Biology",
            "chapters": [
                "The Study of Life",
                "The Chemical Foundation of Life",
                "Biological Macromolecules",
                "Cell Structure",
                "Structure and Function of Plasma Membranes",
                "Metabolism",
                "Cellular Respiration",
                "Photosynthesis",
                "Cell Communication",
                "Cell Reproduction",
                "Meiosis and Sexual Reproduction",
                "Mendel's Experiments and Heredity",
                "Modern Understandings of Inheritance",
                "DNA Structure and Function",
                "Genes and Proteins",
                "Gene Expression",
                "Biotechnology and Genomics",
                "Evolution and the Origin of Species",
                "The Evolution of Populations",
            ]
        },
        {
            "slug": "microbiology",
            "title": "Microbiology",
            "subject": "Biology",
            "chapters": [
                "An Invisible World",
                "How We See the Invisible World",
                "The Cell",
                "Prokaryotic Diversity",
                "The Eukaryotes of Microbiology",
                "Acellular Pathogens",
                "Microbial Biochemistry",
                "Microbial Metabolism",
                "Microbial Growth",
                "Biochemistry of the Genome",
                "Mechanisms of Microbial Genetics",
            ]
        },
        {
            "slug": "anatomy-and-physiology",
            "title": "Anatomy and Physiology",
            "subject": "Biology",
            "chapters": [
                "An Introduction to the Human Body",
                "The Chemical Level of Organization",
                "The Cellular Level of Organization",
                "The Tissue Level of Organization",
                "The Integumentary System",
                "Bone Tissue and the Skeletal System",
                "Axial Skeleton",
                "The Appendicular Skeleton",
                "Joints",
                "Muscle Tissue",
                "The Muscular System",
                "The Nervous System and Nervous Tissue",
            ]
        },
        # Economics
        {
            "slug": "principles-economics-2e",
            "title": "Principles of Economics 2e",
            "subject": "Economics",
            "chapters": [
                "Welcome to Economics!",
                "Choice in a World of Scarcity",
                "Demand and Supply",
                "Labor and Financial Markets",
                "Elasticity",
                "Consumer Choices",
                "Production, Costs, and Industry Structure",
                "Perfect Competition",
                "Monopoly",
                "Monopolistic Competition and Oligopoly",
                "Environmental Protection and Negative Externalities",
                "Positive Externalities and Public Goods",
            ]
        },
        {
            "slug": "principles-macroeconomics-2e",
            "title": "Principles of Macroeconomics 2e",
            "subject": "Economics",
            "chapters": [
                "Welcome to Economics!",
                "Choice in a World of Scarcity",
                "Demand and Supply",
                "The Macroeconomic Perspective",
                "Economic Growth",
                "Unemployment",
                "Inflation",
                "The International Trade and Capital Flows",
                "Government Budgets and Fiscal Policy",
                "The Impacts of Government Borrowing",
                "Macroeconomic Policy around the World",
            ]
        },
        {
            "slug": "principles-microeconomics-2e",
            "title": "Principles of Microeconomics 2e",
            "subject": "Economics",
            "chapters": [
                "Welcome to Economics!",
                "Choice in a World of Scarcity",
                "Demand and Supply",
                "Labor and Financial Markets",
                "Elasticity",
                "Consumer Choices",
                "Production, Costs, and Industry Structure",
                "Perfect Competition",
                "Monopoly",
                "Monopolistic Competition and Oligopoly",
                "Poverty and Economic Inequality",
            ]
        },
        # Psychology
        {
            "slug": "psychology-2e",
            "title": "Psychology 2e",
            "subject": "Psychology",
            "chapters": [
                "Introduction to Psychology",
                "Psychological Research",
                "Biopsychology",
                "States of Consciousness",
                "Sensation and Perception",
                "Learning",
                "Thinking and Intelligence",
                "Memory",
                "Lifespan Development",
                "Motivation and Emotion",
                "Personality",
                "Social Psychology",
                "Industrial-Organizational Psychology",
                "Stress, Lifestyle, and Health",
                "Psychological Disorders",
                "Therapy and Treatment",
            ]
        },
    ]
    
    def __init__(self):
        super().__init__(name="OpenStax")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        })
    
    def _generate_textbook_resources(self, textbook: Dict) -> List[Dict[str, Any]]:
        """Generate resources for a textbook and its chapters."""
        payloads = []
        slug = textbook["slug"]
        title = textbook["title"]
        subject = textbook["subject"]
        chapters = textbook["chapters"]
        
        # Create textbook overview
        book_url = f"{self.BASE_URL}/details/books/{slug}"
        if self.is_new(book_url):
            payload = self.create_payload(
                title=f"OpenStax: {title}",
                summary=f"Free, peer-reviewed {subject.lower()} textbook from OpenStax. "
                        f"Covers {len(chapters)} chapters on {title.lower()} topics. "
                        f"Used by students and educators worldwide.",
                authors=["OpenStax"],
                url=book_url,
                source="OpenStax",
                resource_type="Course Notes"
            )
            payloads.append(payload)
            print(f"[OpenStax] Collected: {title}")
        
        # Create chapter resources
        for i, chapter in enumerate(chapters, 1):
            chapter_slug = chapter.lower().replace(" ", "-").replace(",", "").replace("'", "").replace(":", "")
            chapter_url = f"{self.BASE_URL}/books/{slug}/pages/{i}-{chapter_slug}"
            
            if self.is_new(chapter_url):
                payload = self.create_payload(
                    title=f"{title}: Chapter {i} - {chapter}",
                    summary=f"Chapter {i} of OpenStax {title} covering {chapter.lower()}. "
                            f"Part of a comprehensive {subject.lower()} textbook.",
                    authors=["OpenStax"],
                    url=chapter_url,
                    source="OpenStax",
                    resource_type="Course Notes"
                )
                payloads.append(payload)
                print(f"[OpenStax] Collected: {title} - Chapter {i}")
        
        return payloads
    
    def collect(self, limit: int = 300) -> List[Dict[str, Any]]:
        """Collect textbook content from OpenStax."""
        payloads = []
        
        for textbook in self.TEXTBOOKS:
            if len(payloads) >= limit:
                break
            payloads.extend(self._generate_textbook_resources(textbook))
        
        return payloads[:limit]
