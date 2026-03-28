import re
from typing import Dict, List

class AIInquisitor:
    def __init__(self):
        # В реальном ML здесь загружались бы веса SentenceTransformers
        self.llm_markers = ["безусловно", "в современном мире", "важно отметить", "играет ключевую роль", "подводя итог"]
        self.action_verbs = ["разработал", "запустил", "увеличил", "собрал", "руководил", "внедрил"]

    def check_authenticity(self, text: str) -> Dict:
        """Анализирует текст на вероятность генерации ИИ и водянистость"""
        text_lower = text.lower()
        llm_score = sum(1 for marker in self.llm_markers if marker in text_lower)
        words = text.split()
        lexical_density = len(set(words)) / len(words) if words else 0
        
        penalty = 0
        status = "Аутентичный текст"
        if llm_score >= 2 or lexical_density < 0.4:
            penalty = 30
            status = "Высокий риск использования ИИ (ChatGPT). Текст слишком шаблонный."
            
        return {"penalty": penalty, "status": status, "density": round(lexical_density, 2)}

    def extract_hard_facts(self, text: str) -> List[str]:
        """Ищет конкретику (цифры, проекты), а не воду"""
        # Ищем паттерны: цифры, проценты, аббревиатуры IT/бизнеса
        facts = re.findall(r'\b\d+[%]?\b|\b[A-Z]{2,}\b', text)
        strong_actions = [verb for verb in self.action_verbs if verb in text.lower()]
        return {"metrics_found": len(facts), "strong_actions": strong_actions}

    def generate_interview_probes(self, text: str, facts: Dict) -> List[str]:
        """Генерирует вопросы для комиссии на основе заявленных фактов"""
        probes = []
        if not facts["strong_actions"]:
            probes.append("Кандидат описывает процессы, но не свои действия. Спросить: 'Какова была лично ваша роль в описанных проектах?'")
        if facts["metrics_found"] == 0:
            probes.append("В эссе нет измеримых результатов. Спросить: 'В каких метриках вы оценивали успех своего проекта?'")
        if "создал" in text.lower() or "разработал" in text.lower():
            probes.append("Кандидат заявляет о создании продукта. Спросить: 'С какими главными техническими сложностями вы столкнулись при разработке?'")
        
        # Дефолтный вопрос, если не за что зацепиться
        if not probes:
            probes.append("Попросить привести пример ситуации, когда план полностью провалился, и как кандидат из нее выходил.")
            
        return probes

    def evaluate(self, profile_data: dict) -> dict:
        """Главный пайплайн оценки"""
        combined_text = f"{profile_data['essay_text']} {profile_data['extracurricular_activities']}"
        
        auth_report = self.check_authenticity(combined_text)
        facts_report = self.extract_hard_facts(combined_text)
        probes = self.generate_interview_probes(combined_text, facts_report)
        
        # Расчет базового скора
        base_score = 50 + (facts_report["metrics_found"] * 5) + (len(facts_report["strong_actions"]) * 10)
        final_score = max(0, min(100, base_score - auth_report["penalty"]))
        
        return {
            "final_score": final_score,
            "authenticity_status": auth_report["status"],
            "fact_check": facts_report,
            "interview_questions": probes
        }