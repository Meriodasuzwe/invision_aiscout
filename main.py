from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
from inquisitor import AIInquisitor

app = FastAPI(title="inVision U - Deep-Scout API")
engine = AIInquisitor()

class CandidateProfile(BaseModel):
    user_id: int
    full_name: str
    essay_text: str
    extracurricular_activities: str

class VerificationResult(BaseModel):
    score: int
    authenticity_warning: str
    verified_actions: List[str]
    recommended_interview_questions: List[str]
    explanation: str

@app.post("/api/v1/analyze_candidate", response_model=VerificationResult)
async def analyze(profile: CandidateProfile):
    # Прогоняем данные через наш ML-пайплайн
    analysis = engine.evaluate(profile.dict())
    
    # Формируем красивое объяснение для жюри
    explanation = (
        f"Оценка базируется на {len(analysis['fact_check']['strong_actions'])} подтвержденных маркерах действий. "
        f"Лексический анализ: {analysis['authenticity_status']}."
    )

    return VerificationResult(
        score=analysis["final_score"],
        authenticity_warning=analysis["authenticity_status"],
        verified_actions=analysis["fact_check"]["strong_actions"],
        recommended_interview_questions=analysis["interview_questions"],
        explanation=explanation
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)