import os
import re
from typing import List, Dict, Any, Optional
from app.utils.logger import app_logger

class KnowledgeSection:
    def __init__(self, doc_name: str, doc_title: str, section_title: str, text: str):
        self.doc_name = doc_name
        self.doc_title = doc_title
        self.section_title = section_title
        self.text = text

class KnowledgeService:
    def __init__(self):
        self.kb_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge_base"
        )
        self.sections: List[KnowledgeSection] = []
        self._load_documents()

    def _load_documents(self):
        if not os.path.exists(self.kb_dir):
            app_logger.warning("Knowledge base dir {} does not exist.", self.kb_dir)
            return

        for fname in os.listdir(self.kb_dir):
            if not fname.endswith(".txt"):
                continue
            fpath = os.path.join(self.kb_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                self._parse_doc(fname, content)
            except Exception as e:
                app_logger.error("Error reading KB file {}: {}", fname, e)

        app_logger.info("Loaded {} knowledge sections from {}", len(self.sections), self.kb_dir)

    def _parse_doc(self, fname: str, content: str):
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not lines:
            return
        doc_title = lines[0]
        current_section = "General"
        current_text = []

        for line in lines[1:]:
            # Match section pattern like "1. Eligibility" or "Q: ..."
            sec_match = re.match(r"^(?:\d+\.|\b[A-Z0-9\s\-]+:)\s*(.+)$", line)
            if sec_match and len(line) < 80 and not line.endswith("."):
                if current_text:
                    self.sections.append(KnowledgeSection(
                        doc_name=fname,
                        doc_title=doc_title,
                        section_title=current_section,
                        text=" ".join(current_text)
                    ))
                    current_text = []
                current_section = line
            else:
                current_text.append(line)

        if current_text:
            self.sections.append(KnowledgeSection(
                doc_name=fname,
                doc_title=doc_title,
                section_title=current_section,
                text=" ".join(current_text)
            ))

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Search knowledge base for top matching policy sections.
        """
        if not query or not self.sections:
            return []

        q_terms = set(re.findall(r"\b\w{3,}\b", query.lower()))
        if not q_terms:
            return []

        scored = []
        for sec in self.sections:
            sec_lower = sec.text.lower() + " " + sec.section_title.lower() + " " + sec.doc_title.lower()
            sec_words = set(re.findall(r"\b\w{3,}\b", sec_lower))
            overlap = len(q_terms.intersection(sec_words))
            if overlap > 0:
                # Bonus if query terms match in section title
                title_words = set(re.findall(r"\b\w{3,}\b", sec.section_title.lower()))
                bonus = len(q_terms.intersection(title_words)) * 1.5
                score = (overlap + bonus) / (len(q_terms) + 2)
                scored.append((score, sec))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, sec in scored[:top_k]:
            results.append({
                "title": sec.doc_title,
                "section": sec.section_title,
                "snippet": sec.text,
                "confidence": round(min(0.99, max(0.50, float(score))), 2),
                "doc_name": sec.doc_name
            })
        return results

    def get_all_documents(self) -> List[Dict[str, Any]]:
        docs = {}
        for s in self.sections:
            if s.doc_name not in docs:
                docs[s.doc_name] = {
                    "doc_name": s.doc_name,
                    "title": s.doc_title,
                    "sections": []
                }
            docs[s.doc_name]["sections"].append({
                "section_title": s.section_title,
                "text": s.text
            })
        return list(docs.values())


knowledge_service = KnowledgeService()
