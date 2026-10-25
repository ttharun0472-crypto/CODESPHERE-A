"""Update the existing React lesson records with complete beginner notes.

Run from the backend directory with the project's configured database:
    python update_react_lesson_notes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config.database import SessionLocal
from app.models import Course, Lesson


LESSONS = [
    {
        "title": "Getting Started with React",
        "important_concepts": (
            "React library; components; JSX; functional components; "
            "Vite; declarative UI; reusable interface"
        ),
        "notes": r"""GETTING STARTED WITH REACT

INTRODUCTION

React helps you build interactive web interfaces from small, reusable pieces. In this lesson you will learn what React is, why developers use it, how a React application is organized, and how to create and run a first component with Vite.

1. WHAT IS REACT AND WHY IS IT USED?

React is an open-source JavaScript library for building user interfaces. A user interface (UI) is the part of an application that people see and use: headings, buttons, forms, navigation, and lists. React is especially useful when the page must respond to changing data, such as a course list, shopping cart, or dashboard.

Without a UI library, JavaScript code often has to find individual HTML elements and update them manually. In React, you describe the UI for the current data. When that data changes, React updates the parts of the page that need to change.

React is a library, not a complete web framework. It focuses on the UI. Applications commonly add tools for routing, data access, and other needs.

2. IMPORTANT REACT FEATURES

- Components: Divide the UI into independent, reusable parts.
- Declarative rendering: Describe what should appear for the current data; React handles updating the browser DOM.
- One-way data flow: Data is commonly passed from parent components to child components, making changes easier to follow.
- JSX: Write HTML-like UI descriptions alongside JavaScript.
- Ecosystem: React can be combined with libraries for routing, testing, forms, and server communication.

React may compare a new UI description with the previous one and update the necessary browser DOM nodes. This avoids manually coordinating every visual change; it does not mean that the browser DOM is never updated.

3. COMPONENT-BASED ARCHITECTURE

A component is a focused piece of UI. For example, a learning page can be divided into Navbar, CourseCard, LessonList, and ProgressBar components. Each piece can be understood and changed independently, and a reusable component can appear in several places.

Think of a component tree like this:

App
  Navbar
  CoursePage
    CourseCard
    LessonList
      LessonRow
  Footer

4. JSX

JSX is a syntax extension that lets JavaScript describe UI using HTML-like tags. Build tools such as Vite transform JSX into JavaScript that React can run. JSX is not plain HTML, so remember these common rules:

- Return one parent element, or use a fragment written as <> ... </>.
- Use className rather than class for CSS classes.
- Close tags such as <img /> and <input />.
- Put JavaScript expressions inside curly braces, for example {studentName}.
- Use camelCase for event props such as onClick.
- JSX expressions can contain values and expressions, but not statements such as if directly. Use a conditional expression or compute a value before return.

5. FUNCTIONAL COMPONENTS

A functional component is a JavaScript function whose name starts with a capital letter and which returns JSX:

function Welcome() {
  const learner = "Asha";

  return (
    <section className="welcome">
      <h1>Welcome, {learner}!</h1>
      <p>Your React journey starts here.</p>
    </section>
  );
}

export default Welcome;

HOW THIS EXAMPLE WORKS

1. The function Welcome is the component. Capitalization tells React it is a component rather than a normal HTML tag.
2. The learner variable is ordinary JavaScript data.
3. The return value describes the UI. Curly braces insert the learner value into the heading.
4. className connects the section to a CSS class.
5. The default export allows another file to import this component.

To show the component from App.jsx, import it and use it as a JSX element:

import Welcome from "./Welcome";

function App() {
  return (
    <main>
      <Welcome />
    </main>
  );
}

export default App;

6. INSTALL THE REQUIRED TOOLS AND CREATE A VITE APP

Install a current Node.js LTS release from the official Node.js website. Node.js includes npm, which downloads project dependencies and runs scripts. Verify the tools in a terminal:

node --version
npm --version

Create a JavaScript React project with Vite:

npm create vite@latest my-react-app -- --template react
cd my-react-app
npm install
npm run dev

1. The first command creates a project named my-react-app using Vite's React JavaScript template.
2. cd moves the terminal into the new project directory.
3. npm install downloads the dependencies listed by the project.
4. npm run dev starts Vite's development server. Open the local address printed in the terminal.
5. Stop the server with Ctrl+C when you are finished.

7. UNDERSTANDING THE BASIC PROJECT STRUCTURE

index.html is the browser document used to start the app.
src/main.jsx is the entry point. It asks React to render the root component into the document.
src/App.jsx is a common place for the main application UI.
src/index.css or src/App.css contains global or component styling.
public/ contains static files that can be served as-is.
package.json lists dependencies and scripts such as dev and build.
vite.config.js contains Vite configuration.

The root component is not the whole app forever: as the project grows, split its UI into focused components and import them where needed.

8. FIRST PRACTICE COMPONENT

Replace the starter UI in src/App.jsx with this small course card:

function CourseCard() {
  const courseName = "React Fundamentals";
  const level = "Beginner";

  return (
    <article className="course-card">
      <h1>{courseName}</h1>
      <p>Level: {level}</p>
      <button type="button">Start learning</button>
    </article>
  );
}

export default CourseCard;

STEP-BY-STEP

1. CourseCard is a function component.
2. courseName and level are JavaScript constants local to the function.
3. The article groups the related content semantically.
4. Curly braces display the values rather than the literal words courseName and level.
5. The button has type="button", so it does not accidentally submit a form if moved inside one.
6. Exporting the component lets the Vite entry point render it.

PRACTICE

Add a duration variable and display it in another paragraph. Then create a StudentCard component with a learner name, current topic, and a goal. Try changing a value and observe how the rendered UI changes when the component renders again.

COMMON BEGINNER MISTAKES

- Starting a component name with a lowercase letter: use Welcome, not welcome.
- Writing class instead of className in JSX.
- Forgetting to close a JSX element.
- Returning sibling elements without a parent or fragment.
- Forgetting to export or correctly import a component.
- Treating JSX as a string: use {expression} to insert a JavaScript value.

IMPORTANT CONCEPTS AND KEY TAKEAWAYS

- React is a JavaScript UI library built around reusable components.
- A component describes UI; React handles rendering and updating the browser DOM.
- JSX is transformed by the build tool and lets JavaScript describe UI.
- A functional component is a capitalized function that returns JSX.
- Vite scaffolds and serves a development project; npm installs and runs its scripts.
- Props and state, introduced in later lessons, let components work with changing data.

LESSON SUMMARY

You learned what React is, why it is useful, how component-based UI is organized, and the basic JSX rules. You also created a Vite React project, identified its key files, and wrote a functional course-card component. Practice by building small pieces of UI and combining them into a page."""
    },
    {
        "title": "Components and Props",
        "important_concepts": (
            "Functional components; reusable UI; parent and child components; "
            "props; destructuring; one-way data flow"
        ),
        "notes": r"""COMPONENTS AND PROPS

INTRODUCTION

Components help organize a React page into small pieces that each have a clear purpose. Props are the values a parent gives to a child component. In this lesson you will build reusable components, pass information through props, and compose a page from parent and child components.

1. WHAT ARE COMPONENTS?

A React component is a reusable unit of UI. It is usually a JavaScript function that returns JSX. Examples include a navigation bar, course card, button, profile panel, or lesson row.

Components are useful because they:

- Break a large interface into smaller, understandable parts.
- Let you reuse the same design and behavior with different data.
- Keep related markup and logic together.
- Make it easier to test, debug, and update one part of a page.

2. FUNCTIONAL COMPONENTS AND REUSE

Component names begin with a capital letter. A component is rendered using JSX:

function Greeting() {
  return <h2>Welcome to the course!</h2>;
}

function App() {
  return (
    <main>
      <Greeting />
      <Greeting />
    </main>
  );
}

The Greeting function is written once and used twice. React renders a separate instance at each location. Keep components focused: a component that has one clear job is generally easier to reuse.

3. PARENT AND CHILD COMPONENTS

When a component renders another component, the renderer is the parent and the rendered component is its child. A page may be the parent of several cards, and each card may contain smaller child components. Data normally flows from parent to child through props.

function CoursePage() {
  return (
    <main>
      <h1>Available courses</h1>
      <CourseCard />
    </main>
  );
}

function CourseCard() {
  return <article>React Fundamentals</article>;
}

CoursePage is the parent of CourseCard in this example.

4. WHAT ARE PROPS?

Props (short for properties) are read-only inputs passed to a component. A parent decides the values, and a child uses them to render its UI. A child should not modify its props; to change data, the parent supplies new values or uses state.

Pass a prop as an attribute:

function CourseCard(props) {
  return (
    <article>
      <h2>{props.title}</h2>
      <p>Level: {props.level}</p>
    </article>
  );
}

function CoursePage() {
  return (
    <CourseCard
      title="React Fundamentals"
      level="Beginner"
    />
  );
}

STEP-BY-STEP

1. CoursePage sets title and level on the CourseCard element.
2. React collects those values into the props object.
3. CourseCard reads props.title and props.level.
4. JSX displays each value, so the card can be reused with another title or level.

5. PROPS DESTRUCTURING

Destructuring is a JavaScript way to pull named values out of an object. It makes component parameters easier to read:

function CourseCard({ title, level }) {
  return (
    <article className="course-card">
      <h2>{title}</h2>
      <p>Level: {level}</p>
    </article>
  );
}

The parameter { title, level } is shorthand for receiving props and reading props.title and props.level. The values are still props and should still be treated as read-only.

6. PASSING MULTIPLE PROPS AND CHILD CONTENT

Props can hold strings, numbers, booleans, arrays, objects, and functions. Use curly braces for JavaScript values:

function CourseCard({ title, level, lessonCount, isOpen }) {
  return (
    <article>
      <h2>{title}</h2>
      <p>{level} | {lessonCount} lessons</p>
      {isOpen ? <p>Enrollment is open.</p> : <p>Enrollment is closed.</p>}
    </article>
  );
}

function App() {
  const course = {
    title: "React Fundamentals",
    level: "Beginner",
    lessonCount: 5,
    isOpen: true,
  };

  return <CourseCard {...course} />;
}

The spread syntax {...course} passes each object property as a prop. For beginners, listing props explicitly is often clearer; spread syntax is useful when the object and component props intentionally match.

The special children prop contains JSX placed between a component's opening and closing tags:

function Panel({ children }) {
  return <section className="panel">{children}</section>;
}

function App() {
  return (
    <Panel>
      <h2>Study tip</h2>
      <p>Practice a small example after each topic.</p>
    </Panel>
  );
}

Here, the heading and paragraph become Panel's children.

7. REUSING COMPONENTS IN A LIST

The parent can create data and render one card for each item:

const courses = [
  { id: 1, title: "React Fundamentals", level: "Beginner" },
  { id: 2, title: "JavaScript Basics", level: "Beginner" },
];

function CourseCard({ title, level }) {
  return (
    <article>
      <h2>{title}</h2>
      <p>{level}</p>
    </article>
  );
}

function CourseList() {
  return (
    <section>
      {courses.map((course) => (
        <CourseCard
          key={course.id}
          title={course.title}
          level={course.level}
        />
      ))}
    </section>
  );
}

STEP-BY-STEP

1. courses is an array of objects; each object describes one course.
2. map() calls the callback once for every course and returns a new array of JSX elements.
3. Each card receives its own title and level props.
4. key gives React a stable identity for each sibling item. Use a stable unique ID when available rather than the array index if items may be inserted, removed, or reordered.

PRACTICE

Create a StudentCard component that accepts name, course, and goal props. Render three students from an array using map(). Add a small Badge child component that displays each student's level. Change one object's data and confirm the matching card updates.

COMMON MISTAKES

- Calling a component like a normal function instead of rendering <CourseCard />.
- Using a lowercase component name.
- Trying to change props inside the child.
- Forgetting to use curly braces when passing a number or JavaScript variable.
- Rendering a mapped list without a stable key.
- Passing a prop name that the child does not read.

IMPORTANT CONCEPTS AND KEY TAKEAWAYS

- A component is a reusable function that describes a piece of UI.
- A parent composes child components and passes them input through props.
- Props are read-only; the parent owns the values.
- Destructuring provides convenient names for props.
- children lets a component wrap arbitrary JSX.
- map() can reuse one component for every data item; each sibling needs a stable key.

LESSON SUMMARY

You learned how functional components form a parent-child tree and how props move data down that tree. You practiced destructuring, passing multiple values and children, and rendering reusable course cards from an array. Build a small page by composing several focused components."""
    },
    {
        "title": "State and Events",
        "important_concepts": (
            "State versus props; useState; state updates; onClick; onChange; "
            "onSubmit; event handlers"
        ),
        "notes": r"""STATE AND EVENTS

INTRODUCTION

Interactive interfaces respond to user actions. State is data a component remembers between renders, while event handlers describe what should happen after a click, typing, or form submission. In this lesson you will use useState and common React event props to build a counter and a controlled input.

1. WHAT IS STATE?

State is a component's current, changeable data. Examples include a counter value, whether a menu is open, text typed into a field, or data returned by an API. When state changes through React's state setter, React schedules a new render so the screen reflects the new value.

Props and state are different:

- Props are inputs supplied by a parent. The receiving component treats them as read-only.
- State is data owned by a component and updated by that component using a setter.
- A parent can pass its state to a child as props, so the child receives the latest parent value after the next render.

Do not change a state object or array directly. Create an updated value and pass it to the setter.

2. THE useState HOOK

useState is a built-in React Hook for adding state to a functional component. It returns a pair: the current state value and a function to update it.

import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <section>
      <p>Count: {count}</p>
      <button
        type="button"
        onClick={() => setCount(count + 1)}
      >
        Add one
      </button>
    </section>
  );
}

STEP-BY-STEP

1. Import useState from React.
2. useState(0) sets the initial count to 0 on the first render.
3. count is the value to display; setCount is the update function.
4. onClick receives a function. React calls it when the button is clicked.
5. setCount requests a render with the next count; React updates the displayed number.

When the next value depends on the previous value, use the updater form. It remains correct when React groups multiple updates:

setCount((previousCount) => previousCount + 1);

Never write count = count + 1 or setCount(count++). Those do not correctly update React state.

3. HANDLING BUTTON CLICKS WITH onClick

An event handler is a function that runs in response to an event. Pass the function itself to onClick:

function ResetButton({ onReset }) {
  return (
    <button type="button" onClick={onReset}>
      Reset
    </button>
  );
}

<ResetButton onReset={() => setCount(0)} />

Use onClick={handleClick}, not onClick={handleClick()}. The second form calls the function immediately during rendering instead of waiting for a click.

4. HANDLING INPUT WITH onChange

An input's onChange event runs when its value changes. Combine it with state to make a controlled input:

import { useState } from "react";

function NameGreeting() {
  const [name, setName] = useState("");

  function handleNameChange(event) {
    setName(event.target.value);
  }

  return (
    <section>
      <label htmlFor="learner-name">Your name</label>
      <input
        id="learner-name"
        value={name}
        onChange={handleNameChange}
      />
      <p>Hello, {name || "learner"}!</p>
    </section>
  );
}

HOW THIS WORKS

1. name begins as an empty string.
2. The input value comes from name, so React is the source of truth.
3. When the user types, handleNameChange reads event.target.value.
4. setName stores the new value and React renders the greeting again.
5. A label linked with htmlFor makes the input easier to identify and use with assistive technology.

5. HANDLING FORM SUBMISSION WITH onSubmit

Use onSubmit on the form rather than only a button click. Prevent the browser's default full-page navigation when handling the form in React:

function SearchForm() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    setSubmittedQuery(query.trim());
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="course-search">Course name</label>
      <input
        id="course-search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <button type="submit">Search</button>
      {submittedQuery && <p>Searching for: {submittedQuery}</p>}
    </form>
  );
}

The form's submit event works when the user clicks Search or presses Enter in the input. preventDefault stops the browser's normal page reload. The handler can then validate the value or start an API request.

6. COMPLETE COUNTER WITH ADD AND RESET

import { useState } from "react";

function PracticeCounter() {
  const [count, setCount] = useState(0);

  function addOne() {
    setCount((currentCount) => currentCount + 1);
  }

  function reset() {
    setCount(0);
  }

  return (
    <section>
      <h2>Practice counter</h2>
      <p aria-live="polite">Current value: {count}</p>
      <button type="button" onClick={addOne}>Add one</button>
      <button type="button" onClick={reset}>Reset</button>
    </section>
  );
}

The updater callback receives the latest queued count. reset sets the value back to zero. aria-live="polite" allows assistive technology to announce the updated value without interrupting the user.

PRACTICE

Build a simple reading tracker with a page count. Add buttons to add one page and reset the count. Then add a controlled text input for a book title and a submit handler that displays a message with the entered title. Try submitting an empty value and decide what validation should be shown.

COMMON MISTAKES

- Mutating a state variable directly rather than using its setter.
- Calling an event handler during render instead of passing a function.
- Forgetting event.preventDefault() in a client-handled form.
- Reading an input without storing the current value when a controlled input is needed.
- Using the current state value in several dependent updates instead of the updater callback.
- Assuming setting state changes the variable immediately in the same running function; state updates schedule a future render.

IMPORTANT CONCEPTS AND KEY TAKEAWAYS

- State is component-owned data that can change; props are read-only inputs from a parent.
- useState returns the current value and a setter.
- Calling the setter asks React to render using the new state.
- onClick, onChange, and onSubmit receive functions as event handlers.
- Controlled inputs get their value from state and update it in onChange.
- Form handlers should prevent the browser's default navigation when the app handles submission.

LESSON SUMMARY

You used useState to store a counter and input text, then connected that state to onClick, onChange, and onSubmit handlers. You also practiced functional state updates and form submission. These patterns are the foundation for interactive React forms and API-driven interfaces."""
    },
    {
        "title": "Hooks and Lists",
        "important_concepts": (
            "Hooks; Rules of Hooks; useState; useEffect; effect dependencies; "
            "map; stable keys; empty states"
        ),
        "notes": r"""HOOKS AND LISTS

INTRODUCTION

Hooks let functional components use React features such as state and synchronization with external systems. Lists let a component display repeated data without copying the same JSX by hand. In this lesson you will learn the Rules of Hooks, useEffect dependencies, and how to render dynamic lists with map() and stable keys.

1. WHAT ARE REACT HOOKS?

Hooks are functions provided by React that connect a functional component to React features. Common built-in Hooks include useState for component state and useEffect for synchronizing with something outside React, such as a network request or browser event.

2. RULES OF HOOKS

- Call Hooks at the top level of a React function component or a custom Hook.
- Do not call Hooks inside loops, conditions, nested functions, or event handlers.
- Call Hooks in the same order on every render.
- Custom Hook names start with use, for example useCourseList.

React uses the order of Hook calls to associate each Hook's data with the right component. Conditional Hook calls can change that order and cause incorrect behavior.

3. useState RECAP

import { useState } from "react";

function FavoriteToggle() {
  const [isFavorite, setIsFavorite] = useState(false);

  return (
    <button
      type="button"
      onClick={() => setIsFavorite((current) => !current)}
    >
      {isFavorite ? "Remove favorite" : "Add favorite"}
    </button>
  );
}

The boolean isFavorite is the current state. Clicking the button uses the updater form to invert the latest value; React renders the matching label.

4. useEffect AND DEPENDENCIES

useEffect runs a side effect after React renders. It is useful for work that synchronizes a component with an external system, such as fetching data, subscribing to an event, or starting a timer. Do not use an effect just to calculate a value that can be computed during rendering.

import { useEffect, useState } from "react";

function PageTitle({ courseName }) {
  useEffect(() => {
    document.title = `${courseName} | CodeSphere`;
  }, [courseName]);

  return <h1>{courseName}</h1>;
}

STEP-BY-STEP

1. React renders the heading.
2. After rendering, the effect sets the browser tab title.
3. The dependency array [courseName] tells React to run the effect after the first render and again when courseName changes.
4. With an empty array [], an effect runs after the first render (and may run an extra development check under Strict Mode).
5. Without a dependency array, the effect runs after every render; this is rarely what you want.

If an effect adds a listener, timer, or subscription, return a cleanup function to undo it:

useEffect(() => {
  function handleResize() {
    console.log(window.innerWidth);
  }

  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, []);

The returned function removes the same listener when the component is removed. Include every reactive value used by an effect in its dependency array; a linter can help identify missing dependencies.

5. RENDERING LISTS WITH map()

JavaScript array.map() transforms each array item into a new value. In React, it is commonly used to turn data into JSX:

const lessons = [
  { id: 101, title: "Getting Started with React" },
  { id: 102, title: "Components and Props" },
];

function LessonList() {
  return (
    <ol>
      {lessons.map((lesson) => (
        <li key={lesson.id}>{lesson.title}</li>
      ))}
    </ol>
  );
}

1. map visits each lesson.
2. The callback returns one list item for that lesson.
3. React renders the returned array of elements in order.
4. key identifies each sibling element so React can match items when the list changes.

6. UNDERSTANDING key

Use a stable, unique key among siblings, usually a database ID. A key is for React's reconciliation and is not passed to the child as a normal prop. If a child also needs the ID, pass it separately as id={lesson.id}.

Avoid array indexes as keys when rows can be inserted, removed, or reordered. An index changes meaning when positions change and can make component state appear on the wrong row. Use an index only for a truly static list that will never change order or membership.

7. DYNAMIC COURSE LIST AND EMPTY STATE

function CourseList({ courses }) {
  if (courses.length === 0) {
    return <p>No courses are available yet.</p>;
  }

  return (
    <ul>
      {courses.map((course) => (
        <li key={course.id}>
          <strong>{course.title}</strong>
          <span>{course.description}</span>
        </li>
      ))}
    </ul>
  );
}

The component receives the courses as a prop. If the array is empty, it displays a useful message instead of a blank area. Otherwise, it maps each real course to a list item keyed by the course's stable database ID.

For a list that can be absent while data loads, make the prop contract clear or supply an empty array in the parent. Do not silently substitute fake course data when a request fails; show a loading or error state separately.

8. PRACTICE: FILTER AND DISPLAY

const lessons = [
  { id: 1, title: "Getting Started with React", completed: true },
  { id: 2, title: "Components and Props", completed: false },
  { id: 3, title: "State and Events", completed: false },
];

function LessonChecklist() {
  const completedLessons = lessons.filter((lesson) => lesson.completed);

  return (
    <section>
      <h2>Completed lessons</h2>
      {completedLessons.length === 0 ? (
        <p>Complete a lesson to see it here.</p>
      ) : (
        <ul>
          {completedLessons.map((lesson) => (
            <li key={lesson.id}>{lesson.title}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

filter() creates a new array containing only completed lessons. The conditional renders the empty message or the filtered list. In a real application, this data might come from the backend rather than a local constant.

COMMON MISTAKES

- Calling a Hook inside a condition or loop.
- Omitting a reactive dependency used by an effect.
- Using useEffect to derive simple values that can be computed during render.
- Forgetting a key on a mapped list item.
- Using a changing array index as the key for a list that can reorder.
- Showing an empty-list message while data is still loading; keep loading and empty states separate.

IMPORTANT CONCEPTS AND KEY TAKEAWAYS

- Hooks connect function components to React features and must follow the Rules of Hooks.
- useState stores values that affect rendering.
- useEffect synchronizes with external systems; its dependency array controls when it re-runs.
- Return cleanup from an effect when you create a listener, timer, or subscription.
- map() turns data into repeated JSX; filter() can select which data to show.
- Stable keys help React track list items; they should come from stable IDs when possible.
- Handle loading, error, empty, and populated list states distinctly.

LESSON SUMMARY

You learned the purpose and rules of Hooks, used useState and useEffect, and explored dependency arrays and cleanup. You then used map() and filter() to render course and lesson lists with stable keys and a helpful empty state. Apply these patterns to data that comes from an API."""
    },
    {
        "title": "Forms and API Integration",
        "important_concepts": (
            "Controlled forms; validation; REST; HTTP methods and status codes; "
            "fetch; loading/error states; FastAPI; PostgreSQL"
        ),
        "notes": r"""FORMS AND API INTEGRATION

INTRODUCTION

Forms collect information from a user, and APIs let a frontend exchange data with a backend. In this lesson you will build a controlled form, validate its input, understand REST methods and HTTP status codes, and load real CodeSphere course data through the existing FastAPI API service.

1. CREATING A CONTROLLED REACT FORM

A controlled input gets its value from React state. Its onChange handler updates that state, so the React component remains the source of truth. This makes it easier to validate and submit the exact value on screen.

import { useState } from "react";

function CourseSearchForm() {
  const [courseName, setCourseName] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const cleanedName = courseName.trim();
    if (!cleanedName) {
      setMessage("Enter a course name before searching.");
      return;
    }

    setMessage(`Searching for ${cleanedName}`);
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="course-name">Course name</label>
      <input
        id="course-name"
        name="courseName"
        value={courseName}
        onChange={(event) => setCourseName(event.target.value)}
        required
      />
      <button type="submit">Search</button>
      {message && <p role="status">{message}</p>}
    </form>
  );
}

STEP-BY-STEP

1. courseName starts as an empty string in state.
2. value={courseName} makes the input controlled.
3. onChange reads the latest text and stores it using setCourseName.
4. When the user submits, onSubmit calls handleSubmit.
5. preventDefault stops a full-page browser submission.
6. trim() removes surrounding whitespace; the handler shows a message for an empty value or uses the cleaned input.
7. required adds browser-level validation, but applications should still validate on the server because a client can be bypassed.

For a real request, keep form validation, loading state, server errors, and success feedback visible to the user. Do not assume client-side validation is a security boundary.

2. WHAT IS AN API? WHAT IS REST?

An API (Application Programming Interface) is a defined way for programs to request or send information. A REST-style API commonly exposes resources through URLs and uses HTTP methods to describe the requested action. JSON is a common format for request and response bodies.

Common HTTP methods:

GET: Read a resource or collection. For example, CodeSphere's existing GET /learning/courses route returns courses.
POST: Create a resource or perform an action. The existing POST /learning/courses route creates a course and requires an administrator.
PUT: Replace or update a resource. CodeSphere uses PUT /learning/courses/{course_id} to update a course and protects it for administrators.
PATCH: Partially update a resource. An API supports PATCH only if it defines such a route; do not assume every server provides it.
DELETE: Delete a resource. The existing DELETE /learning/courses/{course_id} route is an administrator operation.

Do not send a POST, PUT, PATCH, or DELETE request simply to test a lesson page. These methods can change server data.

3. HTTP STATUS CODES

2xx means the request succeeded. Examples include 200 OK and 201 Created.
3xx indicates redirection.
4xx means the request could not be fulfilled due to the request or permissions. Examples include 400 Bad Request, 401 Unauthorized, 403 Forbidden, and 404 Not Found.
5xx means the server encountered an error.

Always check response.ok or response.status before treating a fetch response as successful. fetch() does not reject just because the server returned a 404 or 500; it usually rejects for network-level failures.

4. GET DATA FROM THE EXISTING CODESPHERE API

The project configures its API base URL with VITE_API_URL and already provides getCourses() in frontend/src/services/learningApi.js. It requests the real GET /learning/courses endpoint through the shared apiRequest helper, which handles the configured base URL, JSON, and errors.

Use that existing service from a component in frontend/src/pages/learning:

import { useEffect, useState } from "react";
import { getCourses } from "../../services/learningApi";

function CodeSphereCourseList() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    async function loadCourses() {
      try {
        const data = await getCourses();
        if (isCurrent) {
          setCourses(data);
          setError("");
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || "Unable to load courses.");
        }
      } finally {
        if (isCurrent) {
          setLoading(false);
        }
      }
    }

    loadCourses();
    return () => {
      isCurrent = false;
    };
  }, []);

  if (loading) return <p>Loading courses...</p>;
  if (error) return <p role="alert">{error}</p>;
  if (courses.length === 0) return <p>No courses are available.</p>;

  return (
    <ul>
      {courses.map((course) => (
        <li key={course.id}>
          <strong>{course.title}</strong>
          <span>{course.description}</span>
        </li>
      ))}
    </ul>
  );
}

export default CodeSphereCourseList;

HOW THE EXAMPLE WORKS

1. The initial state represents a request that has not finished.
2. The effect calls the existing API service after the first render.
3. getCourses() uses the configured VITE_API_URL and the project's /learning/courses route; no invented host is required.
4. On success, the returned array is saved in state. The course response fields are id, title, and description.
5. On failure, the error is shown rather than replacing the real response with hardcoded courses.
6. finally ends the loading state whether the request succeeds or fails.
7. The cleanup flag prevents a late response from updating this component after it is removed.
8. The database id is used as the list key.

The same service file exposes getCourseLessons(courseId), which calls GET /learning/courses/{course_id}/lessons, and getLesson(lessonId), which calls GET /learning/lessons/{lesson_id}. The learning pages use these endpoints to load lessons and lesson details by their real database IDs. Lesson notes are returned in the lesson response; they are not stored as frontend constants.

The frontend's VITE_API_URL must point to the project's FastAPI base URL in its environment configuration. The API path above is the actual CodeSphere route; do not copy a made-up hostname into application code.

5. CONNECTING REACT, FASTAPI, AND POSTGRESQL

The data flow in CodeSphere is:

React page
  -> frontend/src/services/learningApi.js
  -> shared apiRequest helper and configured VITE_API_URL
  -> FastAPI learning route
  -> SQLAlchemy learning service/model
  -> PostgreSQL

The route receives the HTTP request and uses a database session. SQLAlchemy queries the existing Course and Lesson models. FastAPI serializes the returned model fields through response schemas into JSON. The browser receives that JSON, React stores it in component state, and JSX displays the saved values.

For example, the existing lesson GET route is /learning/lessons/{lesson_id}. Its response contains id, course_id, title, notes, important_concepts, and youtube_url. The course GET route returns id, title, and description. The API, not a frontend constant, is the source of lesson content.

Some routes require authentication or an administrator role. CodeSphere's course-list GET route is public, while course creation and editing are administrator-only. Follow the existing route's permission requirements and shared API client rather than bypassing them with a separate fetch wrapper.

6. A SAFE API REQUEST PATTERN

When using raw fetch for an endpoint, follow the same essential checks as the shared client:

async function loadCourse(courseId) {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/learning/courses/${courseId}`,
    { headers: { Accept: "application/json" } }
  );

  if (!response.ok) {
    throw new Error(`Course request failed (${response.status}).`);
  }

  return response.json();
}

This uses CodeSphere's actual GET path and the project's configured API base URL. Production CodeSphere pages should prefer the existing getCourse(courseId) service because the shared helper centralizes API configuration, authentication headers, JSON parsing, and error messages.

For JSON request bodies, set Content-Type: application/json and serialize with JSON.stringify(value). Only send a write request to an endpoint that the backend documents and that the current user is authorized to use.

PRACTICE

1. Use getCourses() to display the real course list with loading, error, and empty states.
2. Add a search input that filters the returned courses by title; compute the filtered array from state rather than sending a request for each render.
3. Select a course and call getCourseLessons(course.id) to display its real lesson titles.
4. Open one lesson through getLesson(lesson.id) and show the notes returned by the API.
5. Test an invalid course or lesson ID and show a useful error rather than fake content.

COMMON MISTAKES

- Forgetting to prevent the browser's default form submission.
- Assuming fetch rejects on an HTTP 404 or 500.
- Forgetting to set JSON headers or call JSON.stringify for a JSON body.
- Displaying an empty state before the request finishes instead of showing loading first.
- Hiding API errors or silently substituting made-up lesson content.
- Hardcoding a machine-specific API host rather than using configured API settings.
- Calling a protected write endpoint without its required permissions.
- Treating frontend validation as a replacement for backend validation.

IMPORTANT CONCEPTS AND KEY TAKEAWAYS

- Controlled form values are stored in React state and updated through onChange.
- Validate input and provide visible loading, error, empty, and success states.
- REST APIs use HTTP methods such as GET, POST, PUT, PATCH, and DELETE; support depends on the server route.
- Check HTTP status because fetch does not reject for ordinary error responses.
- CodeSphere's real course route is GET /learning/courses; its lesson list route is GET /learning/courses/{course_id}/lessons, and lesson detail uses GET /learning/lessons/{lesson_id}.
- The shared learningApi service uses the configured API base URL and returns database-backed JSON.
- FastAPI routes, SQLAlchemy models/services, and PostgreSQL connect the React UI to persistent records.
- Preserve endpoint authorization and show request errors rather than substituting hardcoded content.

LESSON SUMMARY

You built a controlled form, handled submission and basic validation, and learned the purpose of REST methods and HTTP status codes. You then followed CodeSphere's real frontend-service, FastAPI, SQLAlchemy, and PostgreSQL data path and practiced loading courses and lessons with visible loading and error states. These are the core patterns for connecting a React interface to persistent backend data."""
    },
]


def update_react_lesson_notes():
    db = SessionLocal()
    try:
        courses = (
            db.query(Course)
            .filter(Course.title.ilike("React JS%"))
            .all()
        )
        if len(courses) != 1:
            raise RuntimeError(
                f"Expected exactly one React JS course, found {len(courses)}."
            )

        course = courses[0]
        lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course.id)
            .order_by(Lesson.lesson_order, Lesson.id)
            .all()
        )
        if len(lessons) != len(LESSONS):
            raise RuntimeError(
                f"Expected {len(LESSONS)} existing lessons for course "
                f"{course.id}, found {len(lessons)}."
            )

        for order, (lesson, lesson_data) in enumerate(
            zip(lessons, LESSONS), start=1
        ):
            if lesson.lesson_order != order:
                raise RuntimeError(
                    f"Lesson order {lesson.lesson_order} at position {order} "
                    "does not match the expected sequence."
                )
            title_parts = lesson.title.casefold()
            if lesson_data["title"].casefold() not in title_parts:
                raise RuntimeError(
                    f"Unexpected lesson at order {order}: {lesson.title!r}."
                )
            if not lesson_data["notes"].strip():
                raise RuntimeError(
                    f"Notes are empty for lesson at order {order}."
                )

        for lesson, lesson_data in zip(lessons, LESSONS):
            lesson.title = lesson_data["title"]
            lesson.notes = lesson_data["notes"]
            lesson.important_concepts = lesson_data["important_concepts"]

        db.commit()

        print(f"Updated course id={course.id}: {course.title}")
        for lesson, lesson_data in zip(lessons, LESSONS):
            print(
                f"lesson_id={lesson.id} order={lesson.lesson_order} "
                f"title={lesson_data['title']} "
                f"notes_chars={len(lesson_data['notes'])}"
            )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_react_lesson_notes()
