from __future__ import annotations

import random
import re
from typing import Protocol

from fastapi import HTTPException

SUBJECT = "React JS"
DIFFICULTIES = ("Beginner", "Intermediate", "Advanced")
QUESTION_COUNTS = (5, 10, 15, 20)

_QUESTIONS: dict[str, dict[str, tuple[tuple[str, tuple[str, str, str, str], int, str], ...]]] = {
    "What is React?": {
        "Beginner": (
            ("What is React primarily used to build?", ("User interfaces", "Relational databases", "Operating systems", "Network routers"), 0, "React is a JavaScript library for building user interfaces, commonly for web applications."),
            ("Which description best matches a React component?", ("A reusable piece of UI", "A database table", "A CSS file only", "A browser extension"), 0, "Components package UI and behavior into reusable parts of a React application."),
            ("What does JSX let developers do?", ("Describe UI using syntax embedded in JavaScript", "Query SQL databases directly", "Replace JavaScript with CSS", "Run code on a web server"), 0, "JSX is a syntax extension commonly used to describe React elements inside JavaScript."),
            ("Where does a React application normally update its interface?", ("The browser's document", "A database index", "A DNS record", "A server's filesystem"), 0, "React renders UI into the browser document and updates it as application state changes."),
            ("Which technology is React built around?", ("JavaScript", "SQL", "Bash", "CSS alone"), 0, "React is a JavaScript library; CSS can style the interface but does not provide React's component model."),
        ),
        "Intermediate": (
            ("What is the main purpose of React's reconciliation process?", ("Compare rendered element trees and determine necessary UI updates", "Validate SQL migrations", "Compile CSS into JavaScript", "Route HTTP requests on the server"), 0, "Reconciliation compares the previous and next React element trees so React can update the rendered UI."),
            ("Why should a React component render remain free of side effects?", ("Rendering may run more than once, so side effects belong in event handlers or effects", "React components cannot access JavaScript", "Side effects are only allowed in CSS", "It makes all rendering synchronous"), 0, "Render logic should be pure because React may render again; side effects are handled separately."),
            ("What does a React key help identify in a rendered list?", ("The identity of an item between renders", "The user's password", "The URL of a stylesheet", "The order of CSS declarations"), 0, "Keys let React match list items across renders, supporting correct updates when items change."),
            ("Which statement about React elements is accurate?", ("They are descriptions of UI, not DOM nodes themselves", "They are always database records", "They are CSS selectors", "They are browser event objects"), 0, "React elements are lightweight descriptions that React uses to produce and update the UI."),
            ("Why is changing a component's local variable insufficient to request a React render?", ("React does not observe ordinary local-variable assignments as state updates", "JavaScript variables are immutable", "React renders only on page reload", "Local variables are stored in PostgreSQL"), 0, "React schedules a render when recognized inputs such as state or props change, not for arbitrary local assignments."),
        ),
        "Advanced": (
            ("In concurrent rendering, why may React pause or restart rendering work?", ("To prioritize urgent updates without committing incomplete work", "To retry every database query", "To avoid executing JavaScript", "To make every component render exactly once"), 0, "Concurrent rendering allows React to interrupt and restart render work; only completed work is committed."),
            ("What is the significance of React's render and commit phases?", ("Render calculates a UI update; commit applies it to the host environment", "Render writes the database; commit compiles JavaScript", "Render handles CSS; commit handles network routing", "They are two names for browser layout"), 0, "React separates calculating a tree of changes from applying those changes to the DOM or another host."),
            ("Why can an unstable key such as an array index cause incorrect state association after reordering?", ("React may associate a component instance with a different logical item", "Indexes are not valid JavaScript values", "React sorts every list by key", "The browser rejects numeric keys"), 0, "When positions change, index keys can cause React to reuse component state for the wrong logical item."),
            ("What does memoization in React optimize, and what does it not guarantee?", ("It can skip some repeated work when inputs are unchanged, but is not a correctness guarantee", "It guarantees network requests are cached forever", "It prevents all component renders", "It makes mutable state safe"), 0, "Memoization can avoid recalculation or rendering in eligible cases, but correctness must not depend on it."),
            ("Why should an external-store subscription use a React-compatible subscription API?", ("It lets React read a consistent snapshot and coordinate updates", "It converts the store into a SQL table", "It disables component rendering", "It guarantees the store is immutable"), 0, "React's external-store APIs coordinate snapshot reads and subscriptions with rendering to reduce inconsistent views."),
        ),
    },
    "Understanding Props": {
        "Beginner": (
            ("What are props in a React component?", ("Inputs passed from a parent component", "A component's private database", "CSS media queries", "Browser cookies"), 0, "Props are values supplied by a parent to configure a child component."),
            ("How does a parent usually pass a text value named title to a child?", ("<Card title=\"Welcome\" />", "Card.title = \"Welcome\" in CSS", "SELECT title FROM Card", "document.title(Card, \"Welcome\")"), 0, "A JSX attribute passes a prop to the component."),
            ("Should a child component directly mutate a prop it receives?", ("No; props are read-only inputs", "Yes, every render", "Only when the prop is text", "Only when the parent is a function"), 0, "A component should treat its props as read-only and request changes through callbacks when appropriate."),
            ("What is a common way to provide fallback behavior for an optional prop?", ("Use a default value when the prop is absent", "Delete the parent component", "Store it in a CSS class", "Convert it into a database index"), 0, "Optional props can be given defaults through parameter defaults or another explicit fallback."),
            ("What does the special children prop commonly contain?", ("Nested content placed between a component's opening and closing tags", "The component's CSS file", "The list of browser tabs", "A server response status"), 0, "Nested JSX content is passed to a component as its children prop."),
        ),
        "Intermediate": (
            ("Why should a callback prop be used when a child needs to notify its parent of an event?", ("It lets the parent own state while the child reports an interaction", "It allows the child to mutate props directly", "It forces a full page reload", "It converts state into a URL"), 0, "The parent can own the state and pass a callback for the child to request an update."),
            ("What is prop drilling?", ("Passing data through intermediate components that do not use it", "Rendering a prop twice", "Changing a prop's CSS", "Sending props to a database"), 0, "Prop drilling refers to forwarding values through components that do not themselves need them."),
            ("What should a component do if it needs to derive a display value from a prop?", ("Compute it during rendering when it is a pure derivation", "Mutate the prop and store it globally", "Copy it to local state in every render", "Write it into a cookie"), 0, "Pure values derived from props can usually be calculated during rendering rather than duplicated as state."),
            ("Why is passing a newly created object prop on every parent render sometimes relevant to memoization?", ("Its reference changes, which can make shallow comparisons see a changed prop", "Objects cannot be passed as props", "React serializes all objects to SQL", "It always causes a browser crash"), 0, "A new object has a new reference, which can defeat memoization based on shallow prop comparison."),
            ("Which is a sound rule for component API design?", ("Pass the smallest clear set of data and callbacks the child needs", "Pass the entire application state to every child", "Use props to mutate the parent directly", "Encode all values in CSS selectors"), 0, "A focused prop interface makes component responsibilities clearer and reduces unnecessary coupling."),
        ),
        "Advanced": (
            ("What is a trade-off of using a render prop or function-as-child API?", ("It provides flexible composition but can add nesting and make component flow harder to follow", "It prevents reuse", "It removes all props", "It disables state updates"), 0, "Render functions are flexible composition tools, but deeply nested callback APIs can reduce readability."),
            ("Why can a context value object recreated on every render cause broad consumer updates?", ("Consumers observe a changed value identity", "Context only accepts strings", "React compares context values by database key", "Consumers never update from context"), 0, "A new object identity is considered a changed context value and can notify consumers."),
            ("When is mirroring a prop into state most likely to create a bug?", ("When the prop later changes but the copied state is not synchronized intentionally", "When the prop is a number", "When the component has a key", "When the prop is passed in JSX"), 0, "A copied prop can become stale if the component does not define how subsequent prop changes affect its local state."),
            ("What should a component library consider when exposing callback props?", ("Document callback arguments and whether callbacks may be omitted", "Require callbacks to change props directly", "Hide callback behavior from consumers", "Use callback names as CSS classes"), 0, "A predictable callback contract should specify its purpose, arguments, and optionality."),
            ("Why can a component receiving many unrelated props indicate a design issue?", ("It may combine responsibilities that could be separated or composed", "React limits components to five props", "Props are stored in the DOM", "The component cannot be memoized"), 0, "A broad unrelated prop surface can indicate that the component has too many responsibilities."),
        ),
    },
    "Understanding State with useState": {
        "Beginner": (
            ("What does the useState Hook provide to a function component?", ("A state value and a function to request its update", "A database connection", "A route table", "A CSS stylesheet"), 0, "useState returns the current state value and a setter function."),
            ("What does calling a useState setter normally cause?", ("React to schedule a render with the updated state", "The browser to restart", "The component file to be rewritten", "A PostgreSQL table to be created"), 0, "The setter schedules a render so the component can display the new state."),
            ("Where must a component call useState?", ("At the top level of a React function component or custom Hook", "Inside a loop", "Only inside a click handler", "Inside a CSS file"), 0, "Hooks must be called unconditionally at the top level of function components or custom Hooks."),
            ("How should an array in React state usually be updated?", ("Create a new array containing the desired changes", "Mutate the existing array and do not call the setter", "Convert it to a CSS selector", "Change the browser URL"), 0, "Creating a new array preserves immutable update patterns and gives React a new state value."),
            ("What does a functional state update receive?", ("The previous state value", "The component's CSS", "The HTTP response headers", "The browser's DOM tree"), 0, "A setter callback receives the previous state, which is useful when the next value depends on it."),
        ),
        "Intermediate": (
            ("Why use setCount(previous => previous + 1) when the next state depends on the prior count?", ("It calculates from the latest queued state value", "It prevents React from rendering", "It stores the count in a prop", "It runs the update only once ever"), 0, "Functional updates compose correctly with queued updates by using the latest previous state."),
            ("Why is mutating an object in state and passing the same object back unreliable?", ("The object identity is unchanged and the mutation bypasses React's immutable update expectations", "React state supports only strings", "Objects cannot be rendered", "JavaScript forbids object mutation"), 0, "Mutating and reusing an object can prevent React from detecting a meaningful state change and makes updates harder to reason about."),
            ("What does React state batching generally do?", ("Groups updates so React can avoid unnecessary intermediate renders", "Combines separate users' database rows", "Prevents all state updates", "Turns updates into network requests"), 0, "Batching can process multiple state updates together and reduce redundant rendering."),
            ("When is lazy initialization useful with useState?", ("When computing the initial state is expensive and should run only for initialization", "When state must update on every render", "When the value comes from props only", "When a component has no state"), 0, "Passing an initializer function lets React compute the initial state during initialization rather than on every render."),
            ("Why may reading state immediately after calling its setter still show the old value in the current handler?", ("The current render's state is a snapshot; the setter schedules a later render", "The setter always fails", "State is stored only on the server", "JavaScript handlers cannot read variables"), 0, "A setter schedules an update; it does not mutate the state variable captured by the current render."),
        ),
        "Advanced": (
            ("Why can a state update based on a stale closure produce an incorrect result?", ("The closure may reference the state snapshot from an earlier render", "Closures cannot read state", "React state is always synchronous", "The browser removes the callback"), 0, "Callbacks capture values from the render in which they were created; functional updates avoid stale calculations for queued state changes."),
            ("What is a sound strategy for updating one field in object state?", ("Create a new object that copies existing fields and overrides the target field", "Mutate the existing object without the setter", "Replace the component with a class", "Use a prop as temporary state"), 0, "Immutable object updates preserve the other fields while creating a new object for React to observe."),
            ("Why should state not be duplicated when it can be derived from other state?", ("Duplicated state can become inconsistent and requires synchronization", "Derived values cannot be displayed", "React deletes derived variables", "State setters do not accept objects"), 0, "Keeping one source of truth avoids stale duplicated values and unnecessary synchronization logic."),
            ("What can happen when state updates are issued from an effect that depends on the same state without a stopping condition?", ("The effect can repeatedly schedule renders", "The state becomes immutable", "React skips the component forever", "The app converts to server rendering"), 0, "An effect that updates a dependency on every run can form a render loop unless guarded or structured differently."),
            ("How should a reducer be considered relative to multiple useState calls?", ("Use a reducer when related state transitions benefit from one explicit update function", "Always replace useState with a reducer", "Use a reducer only for strings", "Reducers prevent state from changing"), 0, "Reducers can centralize complex related transitions; simple independent state is often clearer with useState."),
        ),
    },
}


class MCQQuestionProvider(Protocol):
    def subjects(self) -> list[dict[str, object]]: ...

    def available_count(self, subject: str, topic: str, difficulty: str) -> int: ...

    def get_questions(
        self, subject: str, topic: str, difficulty: str, count: int
    ) -> list[dict[str, object]]: ...


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def _build_question(
    topic: str,
    difficulty: str,
    index: int,
    item: tuple[str, tuple[str, str, str, str], int, str],
) -> dict[str, object]:
    question_text, source_options, correct_index, explanation = item
    topic_id = re.sub(r"[^a-z0-9]+", "-", topic.casefold()).strip("-")
    difficulty_id = difficulty.casefold()
    question_id = f"react:{topic_id}:{difficulty_id}:{index + 1:03d}"
    shuffled = list(enumerate(source_options))
    random.Random(question_id).shuffle(shuffled)
    options = [
        {"id": f"{question_id}:option:{source_index + 1}", "text": text}
        for source_index, text in shuffled
    ]
    correct_option_id = f"{question_id}:option:{correct_index + 1}"
    question = {
        "id": question_id,
        "subject": SUBJECT,
        "topic": topic,
        "difficulty": difficulty,
        "question": question_text,
        "options": options,
        "correct_option_id": correct_option_id,
        "correct_answer": source_options[correct_index],
        "explanation": explanation,
    }
    validate_question(question)
    return question


def validate_question(question: dict[str, object]) -> None:
    if not isinstance(question.get("id"), str) or not question["id"]:
        raise ValueError("Question ID must be a nonempty string.")
    if question.get("subject") != SUBJECT:
        raise ValueError("Question subject is unsupported.")
    topic = question.get("topic")
    difficulty = question.get("difficulty")
    if not isinstance(topic, str) or topic not in _QUESTIONS:
        raise ValueError("Question topic is unsupported.")
    if not isinstance(difficulty, str) or difficulty not in DIFFICULTIES:
        raise ValueError("Question difficulty is unsupported.")
    if not isinstance(question.get("question"), str) or not question["question"].strip():
        raise ValueError("Question text must not be empty.")
    options = question.get("options")
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("Every MCQ must have exactly four options.")
    option_ids: set[str] = set()
    option_texts: set[str] = set()
    for option in options:
        if not isinstance(option, dict):
            raise ValueError("Each answer option must be an object.")
        option_id = option.get("id")
        text = option.get("text")
        if not isinstance(option_id, str) or not option_id or not isinstance(text, str) or not text.strip():
            raise ValueError("Every answer option needs a nonempty ID and text.")
        option_ids.add(option_id)
        option_texts.add(_normalized(text))
    if len(option_ids) != 4 or len(option_texts) != 4:
        raise ValueError("Answer option IDs and normalized texts must be distinct.")
    correct_option_id = question.get("correct_option_id")
    if not isinstance(correct_option_id, str) or correct_option_id not in option_ids:
        raise ValueError("Correct option must refer to one of the four options.")
    correct_answer = question.get("correct_answer")
    correct_option = next(option for option in options if option["id"] == correct_option_id)
    if correct_option["text"] != correct_answer:
        raise ValueError("Correct answer text must match the correct option.")
    if not isinstance(question.get("explanation"), str) or not question["explanation"].strip():
        raise ValueError("Question explanation must not be empty.")


class RuleBasedMCQQuestionProvider:
    def subjects(self) -> list[dict[str, object]]:
        return [
            {
                "name": SUBJECT,
                "topics": [
                    {
                        "name": topic,
                        "available_counts": {
                            difficulty: [len(items)]
                            for difficulty, items in difficulty_items.items()
                        },
                    }
                    for topic, difficulty_items in _QUESTIONS.items()
                ],
            }
        ]

    def available_count(self, subject: str, topic: str, difficulty: str) -> int:
        if subject != SUBJECT or topic not in _QUESTIONS:
            raise HTTPException(status_code=422, detail="Unsupported subject or topic.")
        if difficulty not in DIFFICULTIES:
            raise HTTPException(status_code=422, detail="Unsupported difficulty.")
        return len(_QUESTIONS[topic][difficulty])

    def get_questions(
        self, subject: str, topic: str, difficulty: str, count: int
    ) -> list[dict[str, object]]:
        available = self.available_count(subject, topic, difficulty)
        if count not in QUESTION_COUNTS:
            raise HTTPException(
                status_code=422,
                detail="Question count must be 5, 10, 15, or 20.",
            )
        if count > available:
            raise HTTPException(
                status_code=422,
                detail=f"Only {available} validated questions are available for this topic and difficulty.",
            )
        pool = [
            _build_question(topic, difficulty, index, item)
            for index, item in enumerate(_QUESTIONS[topic][difficulty])
        ]
        selected = pool[:count]
        question_ids = [question["id"] for question in selected]
        question_texts = [_normalized(str(question["question"])) for question in selected]
        if len(set(question_ids)) != len(question_ids) or len(set(question_texts)) != len(question_texts):
            raise RuntimeError("The MCQ provider produced duplicate questions.")
        return selected


rule_based_provider = RuleBasedMCQQuestionProvider()
