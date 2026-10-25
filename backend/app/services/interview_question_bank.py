from itertools import zip_longest
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import Course, Lesson, Question, Topic


GENERAL_QUESTIONS = {
    "hr": {
        "easy": [
            ("Tell me about yourself and the experiences that led you to this opportunity.", "Give a concise introduction connecting your background, relevant experience, and motivation."),
            ("What interests you about this role and the organization?", "Connect a specific role responsibility and a genuine reason for choosing the organization."),
            ("What is one strength you would bring to a team?", "Support a relevant strength with a brief, concrete example."),
            ("Describe a goal you set for yourself and how you worked toward it.", "Explain the goal, actions taken, and a measurable or observable outcome."),
            ("What kind of work helps you stay motivated?", "Describe the environment or work that motivates you and relate it to the role."),
            ("How do you organize your work when you have several responsibilities?", "Explain a practical prioritization method and how you communicate changing priorities."),
        ],
        "medium": [
            ("Describe a time you received difficult feedback. How did you respond?", "Explain the feedback, how you clarified it, the changes you made, and what improved."),
            ("Tell me about a disagreement with a teammate and how you handled it.", "Show how you listened, focused on shared goals, resolved the disagreement, and followed up."),
            ("Describe a mistake you made on a project and what you learned.", "Take ownership, explain the impact, corrective action, and a concrete lesson."),
            ("Tell me about a time you had to learn something quickly to meet a commitment.", "Describe the learning plan, how you checked understanding, and the outcome."),
            ("Give an example of balancing quality with a tight deadline.", "Explain trade-offs, prioritization, stakeholder communication, and the result."),
            ("Describe a team contribution you are especially proud of.", "Clarify your individual contribution and its impact on the team or outcome."),
        ],
        "hard": [
            ("Tell me about a decision you made with incomplete information and how you managed the risk.", "Explain assumptions, consultation, decision criteria, mitigation, and how you revisited the decision."),
            ("Describe a time you changed your approach after realizing your initial plan was not working.", "Show how you recognized evidence, adapted, communicated the change, and measured the result."),
            ("How would you respond if a key stakeholder rejected work you believed was complete?", "Explore expectations, seek specific evidence, align on criteria, and propose a constructive next step."),
            ("Tell me about a time you influenced a team without formal authority.", "Describe the shared goal, how you built trust, addressed concerns, and achieved an outcome."),
            ("Describe a situation where two important commitments conflicted. How did you decide what to do?", "Explain impact-based prioritization, transparent escalation, and how the commitments were managed."),
            ("What is a professional view you changed after hearing a persuasive opposing perspective?", "Demonstrate openness, evidence-based reflection, and how the updated view changed your actions."),
        ],
    },
    "communication": {
        "easy": [
            ("Explain a technical idea you know well to someone new to the subject.", "Use plain language, a clear structure, and a simple example without relying on unexplained jargon."),
            ("How do you check that someone has understood your explanation?", "Invite questions or a summary, listen for gaps, and adjust the explanation respectfully."),
            ("Describe how you would introduce yourself in a short professional meeting.", "Give a concise introduction covering context, relevant focus, and purpose."),
            ("How would you ask for clarification when a request is unclear?", "State what you understand, identify the ambiguity, and ask a focused question."),
            ("How do you keep a listener engaged when explaining a complex topic?", "Break the idea into steps, use relevant examples, and check in with the listener."),
            ("Describe one way you adapt your communication for a new audience.", "Mention audience needs, vocabulary, level of detail, and feedback."),
        ],
        "medium": [
            ("How would you explain a project delay to a stakeholder who is not technical?", "Communicate impact and cause plainly, own next steps, and provide a credible revised plan."),
            ("Describe how you would present two competing solutions and help a team choose.", "Define shared criteria, compare evidence and trade-offs, invite perspectives, and recommend transparently."),
            ("How would you respond when a meeting discussion becomes confusing or goes off topic?", "Summarize the points, clarify the decision needed, and propose a respectful path back to the agenda."),
            ("Tell me how you would give constructive feedback to a teammate.", "Use specific observations, explain impact, invite their perspective, and agree on a supportive next step."),
            ("How would you write a concise status update for a project with a significant risk?", "State status, risk and impact, mitigation, owner, and the decision or help needed."),
            ("Describe how you handle questions you cannot answer immediately in a presentation.", "Acknowledge the question, be transparent about uncertainty, and commit to a reliable follow-up."),
        ],
        "hard": [
            ("How would you communicate a high-impact technical risk when leaders disagree about its urgency?", "Present evidence and consequences clearly, distinguish facts from uncertainty, and offer actionable options."),
            ("Explain how you would facilitate a decision between teams with competing priorities.", "Surface shared outcomes, make constraints visible, establish decision criteria, and document ownership."),
            ("How would you correct misinformation about your team's work without escalating conflict?", "Respond promptly with verifiable facts, acknowledge concerns, and use a constructive channel."),
            ("Describe a strategy for communicating a complex change to audiences with very different needs.", "Segment audiences, tailor detail and channels, maintain a consistent core message, and collect feedback."),
            ("How would you handle a sensitive disagreement in a remote meeting?", "Create space for perspectives, clarify the underlying issue, agree on facts, and record next steps."),
            ("How would you communicate uncertainty while still enabling a time-sensitive decision?", "State confidence and assumptions, describe possible outcomes, identify reversible choices, and set a review point."),
        ],
    },
}

COURSE_QUESTION_TEMPLATES = {
    "easy": (
        (
            "Explain {topic} in your own words. What problem does it solve in {course}?",
            "Define {topic}, describe its purpose, and give a relevant example grounded in {context}.",
        ),
        (
            "What are the main parts or steps involved in {topic}, and how do they fit together?",
            "Identify the key parts of {topic} and explain their relationship using the course context: {context}.",
        ),
        (
            "Give a simple example of using {topic} in a {course} task.",
            "Describe a straightforward use of {topic}, the steps involved, and the expected outcome. Course context: {context}.",
        ),
    ),
    "medium": (
        (
            "How would you apply {topic} to solve a practical problem in {course}? Walk through your approach.",
            "Outline the problem, explain how {topic} applies, and walk through the solution. Relevant course material: {context}.",
        ),
        (
            "A {course} task involving {topic} is not producing the expected result. How would you investigate it?",
            "Reproduce the issue, inspect assumptions and inputs, isolate the relevant {topic} behavior, and verify a fix. Course context: {context}.",
        ),
        (
            "What would you consider when choosing an approach that uses {topic}?",
            "Compare suitable approaches against correctness, complexity, and maintainability, using {context} as the scope.",
        ),
    ),
    "hard": (
        (
            "Design a robust {course} solution that uses {topic}. Explain your choices and trade-offs.",
            "Propose a solution using {topic}, justify its structure, and discuss relevant constraints and trade-offs. Course context: {context}.",
        ),
        (
            "What can go wrong when relying on {topic} in a larger {course} system, and how would you mitigate it?",
            "Identify realistic failure modes or limitations of {topic} and explain how testing, validation, or design choices mitigate them. Context: {context}.",
        ),
        (
            "How would you evaluate whether a solution based on {topic} is correct and ready to maintain?",
            "Describe correctness checks, edge cases, measurable quality criteria, and maintenance considerations for {topic}. Course context: {context}.",
        ),
    ),
}


def get_course(course_id: int, db: Session) -> Course:
    course = (
        db.query(Course)
        .options(
            joinedload(Course.lessons)
            .joinedload(Lesson.topics)
            .joinedload(Topic.questions)
        )
        .filter(Course.id == course_id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Learning course not found.")
    return course


def _course_concepts(course: Course) -> list[dict[str, str]]:
    concepts: list[dict[str, str]] = []
    seen: set[str] = set()
    for lesson in sorted(course.lessons, key=lambda item: item.lesson_order):
        for topic in sorted(lesson.topics, key=lambda item: item.topic_number):
            topic_name = topic.title.strip()
            details = topic.description or ""
            bank_questions = sorted(
                topic.questions,
                key=lambda item: item.question_number,
            )
            for question in bank_questions:
                details = " ".join(
                    part.strip()
                    for part in (
                        details,
                        question.quick_answer or "",
                        question.explanation or "",
                        question.key_points or "",
                    )
                    if part and part.strip()
                )
            if topic_name and topic_name.casefold() not in seen:
                concepts.append({"topic": topic_name, "context": details or topic_name})
                seen.add(topic_name.casefold())

        lesson_name = lesson.title.strip()
        if lesson_name and lesson_name.casefold() not in seen:
            concepts.append(
                {
                    "topic": lesson_name,
                    "context": lesson.notes or lesson.important_concepts or lesson_name,
                }
            )
            seen.add(lesson_name.casefold())

    if not concepts and course.title.strip():
        concepts.append(
            {
                "topic": course.title.strip(),
                "context": course.description or course.title.strip(),
            }
        )
    return concepts


def build_default_questions(
    course: Course | None,
    category: str,
    difficulty: str,
) -> list[dict[str, Any]]:
    if category in {"hr", "communication"}:
        return [
            {
                "question": question,
                "category": category,
                "difficulty": difficulty,
                "expected_answer": answer,
                "course_id": None,
            }
            for question, answer in GENERAL_QUESTIONS[category][difficulty]
        ]

    if course is None:
        raise HTTPException(
            status_code=422,
            detail="Select a learning course for technical or mixed interview questions.",
        )

    templates = COURSE_QUESTION_TEMPLATES[difficulty]
    questions = []
    for concept in _course_concepts(course):
        for question_template, answer_template in templates:
            questions.append(
                {
                    "question": question_template.format(
                        topic=concept["topic"],
                        course=course.title,
                        context=concept["context"][:1000],
                    ),
                    "category": concept["topic"],
                    "difficulty": difficulty,
                    "expected_answer": answer_template.format(
                        topic=concept["topic"],
                        course=course.title,
                        context=concept["context"][:1000],
                    ),
                    "course_id": course.id,
                }
            )

    if category == "mixed":
        hr_questions = build_default_questions(None, "hr", difficulty)
        technical_count = min(len(questions), max(1, len(questions) // 2))
        technical_questions = questions[:technical_count]
        questions = [
            question
            for pair in zip_longest(technical_questions, hr_questions)
            for question in pair
            if question is not None
        ]
    for question in questions:
        question["question_source"] = "default"
    return questions


def get_available_questions(
    course_id: int | None,
    category: str,
    difficulty: str,
    db: Session,
) -> dict[str, Any]:
    course = get_course(course_id, db) if course_id is not None else None
    questions = build_default_questions(course, category, difficulty)
    return {
        "course_id": course.id if course else None,
        "course_title": course.title if course else None,
        "questions": [
            {
                "question": question["question"],
                "category": question["category"],
                "difficulty": question["difficulty"],
                "course_id": question["course_id"],
            }
            for question in questions[:20]
        ],
        "available_count": min(len(questions), 20),
    }
