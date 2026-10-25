import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.models import Course
from app.schemas.interview_session_schema import (
    InterviewDifficulty,
    InterviewEvaluation,
    InterviewSessionCreate,
)
from app.services.ai_config import GEMINI_API_KEY
from app.services.interview_question_bank import build_default_questions

logger = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TIMEOUT_SECONDS = 30


class GeneratedQuestion(BaseModel):
    question: str = Field(min_length=12, max_length=1000)
    category: str = Field(min_length=2, max_length=100)
    difficulty: InterviewDifficulty
    expected_answer: str = Field(min_length=10, max_length=5000)


class GeneratedQuestionList(BaseModel):
    questions: list[GeneratedQuestion] = Field(min_length=1, max_length=20)


def _generate_content(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI interview generation is unavailable because the Gemini API key is not configured.",
        )

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={quote(GEMINI_API_KEY, safe='')}"
    )
    request = Request(
        endpoint,
        data=json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.7,
                },
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=GEMINI_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        logger.warning("Gemini interview request failed with status %s", exc.code)
        if exc.code == 429:
            raise HTTPException(
                status_code=503,
                detail="The AI provider is rate-limiting requests. Please try again shortly.",
            ) from exc
        raise HTTPException(
            status_code=502,
            detail="The AI provider could not complete the interview request.",
        ) from exc
    except (URLError, TimeoutError, OSError) as exc:
        logger.warning("Gemini interview request failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=504,
            detail="The AI provider did not respond in time. Please try again.",
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        logger.warning("Gemini returned an unreadable response")
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an invalid response.",
        ) from exc

    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an empty response.",
        ) from exc

    if not isinstance(text, str) or not text.strip():
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an empty response.",
        )
    return text


def _parse_json_response(response_text: str, response_model: type[BaseModel]) -> Any:
    text = response_text.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(text)
        return response_model.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned data that did not match the required response format.",
        ) from exc


def generate_interview_questions(
    request: InterviewSessionCreate,
    course: Course | None,
) -> list[dict[str, Any]]:
    default_questions = build_default_questions(
        course,
        request.category,
        request.difficulty,
    )[:20]
    if request.number_of_questions > len(default_questions):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Only {len(default_questions)} default questions are available "
                "for this course, category, and difficulty."
            ),
        )

    if not GEMINI_API_KEY:
        return default_questions[:request.number_of_questions]

    course_context = {
        "title": course.title,
        "description": course.description,
        "lessons": [
            {
                "title": lesson.title,
                "notes": lesson.notes,
                "important_concepts": lesson.important_concepts,
                "topics": [
                    {
                        "title": topic.title,
                        "description": topic.description,
                        "learning_questions": [
                            {
                                "question": question.question,
                                "answer": question.quick_answer or question.explanation,
                            }
                            for question in topic.questions[:10]
                        ],
                    }
                    for topic in lesson.topics[:20]
                ],
            }
            for lesson in course.lessons[:30]
        ],
    } if course else None
    prompt = f"""
You are an experienced, supportive interviewer preparing a realistic student interview.
Generate exactly {request.number_of_questions} distinct questions.
Interview category: {request.category}
Selected learning course and its actual content: {json.dumps(course_context, ensure_ascii=False)}
Difficulty: {request.difficulty}

Make every question specific, appropriate to its difficulty, educational, and answerable.
For technical questions, use the selected course's actual lessons, topics, and learning
questions. Do not introduce an unrelated technical subject. For HR/communication
questions, use suitable behavioral or communication prompts rather than technical trivia.
Mixed interviews should combine course-specific technical and HR/communication questions.
Do not repeat or paraphrase questions.
Provide a concise, accurate reference explanation for each question.
Return JSON only in this format:
{{"questions":[{{"question":"...","category":"...","difficulty":"{request.difficulty}","expected_answer":"..."}}]}}
"""

    try:
        generated = _parse_json_response(
            _generate_content(prompt),
            GeneratedQuestionList,
        )
        questions = [question.model_dump() for question in generated.questions]
        if len(questions) != request.number_of_questions:
            raise HTTPException(
                status_code=502,
                detail="The AI provider generated an unexpected number of questions.",
            )
        normalized = [item["question"].strip().casefold() for item in questions]
        if len(set(normalized)) != len(normalized):
            raise HTTPException(
                status_code=502,
                detail="The AI provider generated duplicate questions.",
            )
        question_categories = [
            item["category"].casefold() for item in questions
        ]
        has_hr_question = any(
            any(marker in category for marker in ("hr", "behavior"))
            for category in question_categories
        )
        has_communication_question = any(
            "communication" in category for category in question_categories
        )
        has_people_question = has_hr_question or has_communication_question
        has_technical_question = any(
            not any(
                marker in category
                for marker in ("hr", "behavior", "communication")
            )
            for category in question_categories
        )
        if request.category == "mixed" and not (
            has_people_question and has_technical_question
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI provider did not return a balanced mixed interview.",
            )
        if request.category == "hr" and not has_hr_question:
            raise HTTPException(
                status_code=502,
                detail="The AI provider returned questions outside the HR category.",
            )
        if request.category == "communication" and not any(
            "communication" in category for category in question_categories
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI provider returned questions outside the communication category.",
            )
        for question in questions:
            question["course_id"] = (
                course.id
                if request.category in {"technical", "mixed"} and course
                else None
            )
            question["question_source"] = "ai"
        return questions
    except HTTPException as exc:
        logger.warning(
            "AI question generation failed; using course question bank (status %s)",
            exc.status_code,
        )
        return default_questions[:request.number_of_questions]


def evaluate_interview_answer(
    question: dict[str, Any],
    answer: str,
    interview_category: str,
) -> InterviewEvaluation:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI answer evaluation is unavailable because the Gemini API key is not configured.",
        )

    category = question["category"].lower()
    if interview_category == "hr" or any(
        marker in category for marker in ("hr", "behavior")
    ):
        criteria = "relevance, behavioral_specificity, completeness, clarity, communication"
    elif interview_category == "communication" or "communication" in category:
        criteria = "relevance, organization, clarity, audience_awareness, completeness"
    else:
        criteria = "technical_correctness, conceptual_understanding, completeness, relevance, clarity"

    prompt = f"""
Evaluate the student's answer to this interview question fairly and constructively.
Overall interview category: {interview_category}
Question category: {question["category"]}
Question: {question["question"]}
Reference explanation (use as guidance, not an exact-match requirement):
{question["expected_answer"]}
Student answer:
{answer}

Score the answer from 0 to 100. Assess {criteria}. A blank answer must not be evaluated
as correct. For HR or communication answers, assess the quality and relevance of the
response, not technical correctness. Return JSON only:
{{
  "score": 0,
  "strengths": ["..."],
  "missing_concepts": ["..."],
  "areas_for_improvement": ["..."],
  "model_answer": "...",
  "next_attempt_suggestion": "...",
  "criterion_scores": {{"criterion_name": 0}}
}}
Use concise, answer-specific feedback. Do not award points for concepts the student
did not mention, and do not use empty feedback lists.
"""
    evaluation = _parse_json_response(
        _generate_content(prompt),
        InterviewEvaluation,
    )
    return evaluation
