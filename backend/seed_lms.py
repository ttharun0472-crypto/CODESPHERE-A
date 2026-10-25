"""
seed_lms.py — Safe, idempotent seed script for the React: Basics to Advanced course.

Run from the backend/ directory:
    python seed_lms.py

Safety guarantees:
  - Never drops or truncates existing tables.
  - Checks for duplicate records by title/question text before inserting.
  - Safe to run multiple times — will skip already-existing records.
  - Does not touch users, courses (other than the target), lessons, or progress.
"""

import sys
import os

# Make sure the app package is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.config.database import SessionLocal
from app.models import Course, Lesson
from app.models.topic import Topic
from app.models.question import Question


# ======================================================
# SEED DATA
# Course → Lesson → Topic → [Questions]
# ======================================================

COURSE_TITLE = "React JS \u2014 Basics to Advanced"

# Maps seed lesson titles -> actual DB lesson titles (adjust to match your admin-created lessons)
LESSON_TITLE_MAP = {
    "Introduction to React": "LESSON 1: GETTING STARTED WITH REACT",
    "Components and Props": "LESSON 2: COMPONENTS AND PROPS",
    "State and Events": "LESSON 3: STATE AND EVENTS",
    "Hooks and Lists": "LESSON 4: HOOKS AND LISTS",
    "Forms and API Integration": "LESSON 5: FORMS AND API INTEGRATION",
}


SEED_DATA = [
    {
        "lesson_title": "Introduction to React",
        "topics": [
            {
                "title": "What is React?",
                "description": "Understanding the fundamentals and purpose of React as a UI library.",
                "topic_number": 1,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "What is React?",
                        "quick_answer": "React is an open-source JavaScript library developed by Facebook for building fast, interactive user interfaces.",
                        "explanation": "React is a declarative, component-based JavaScript library for building user interfaces.\n\nIt was created by Jordan Walke at Facebook in 2011 and open-sourced in 2013.\n\nReact focuses only on the view layer (the UI) of an application. This makes it lightweight and easy to integrate with other libraries or frameworks.\n\nInstead of manipulating the DOM directly, you describe what the UI should look like, and React efficiently updates the browser to match that description.",
                        "real_world_example": "Facebook, Instagram, WhatsApp Web, Netflix, Airbnb, and Atlassian all use React to build their user interfaces.\n\nFor example, when you scroll through your Facebook feed and new posts load without the entire page refreshing, that seamless experience is powered by React components updating only the part of the page that changed.",
                        "code_example": "// A simple React component\nfunction Welcome() {\n  return <h1>Hello, World!</h1>;\n}\n\nexport default Welcome;",
                        "expected_output": "Renders: Hello, World!",
                        "flowchart": "Developer writes JSX\n        ↓\nReact compiles JSX to JavaScript\n        ↓\nReact creates Virtual DOM\n        ↓\nReact updates Real DOM (only changed parts)\n        ↓\nBrowser displays updated UI",
                        "key_points": "React is a JavaScript library, not a full framework\nCreated by Facebook in 2011, open-sourced in 2013\nFocuses only on the View layer (UI)\nUses a component-based architecture\nUses a Virtual DOM for efficient updates",
                        "remember_this": "React = UI Library. It only handles the View. You combine it with other tools (like React Router for routing, Redux for state) to build a full application."
                    },
                    {
                        "question_number": 2,
                        "question": "Why is React used?",
                        "quick_answer": "React is used because it makes building complex, interactive UIs faster, more maintainable, and more efficient through reusable components and the Virtual DOM.",
                        "explanation": "React is used for several key reasons:\n\n1. Component Reusability: Build a button, card, or form once and reuse it anywhere in your application.\n\n2. Efficient Updates: React's Virtual DOM ensures only the parts of the UI that actually changed are updated in the browser — avoiding expensive full-page reloads.\n\n3. Declarative Syntax: You describe what the UI should look like for a given state, and React handles the DOM manipulation.\n\n4. Large Ecosystem: Thousands of libraries, tools, and a massive community make React highly productive.\n\n5. One-way Data Flow: Data flows in one direction (parent → child), making applications predictable and easier to debug.",
                        "real_world_example": "Imagine building a social media dashboard that shows user posts, comments, likes, and notifications — all updating in real time.\n\nWith React, each of these sections is a separate component. When a new like comes in, only the like count component re-renders — not the entire page. This is much faster than rebuilding the entire DOM.",
                        "code_example": "// Reusable Button component\nfunction Button({ label, onClick }) {\n  return (\n    <button onClick={onClick} className=\"btn\">\n      {label}\n    </button>\n  );\n}\n\n// Used in multiple places\nfunction App() {\n  return (\n    <div>\n      <Button label=\"Submit\" onClick={() => alert(\"Submitted!\")} />\n      <Button label=\"Cancel\" onClick={() => alert(\"Cancelled!\")} />\n    </div>\n  );\n}",
                        "expected_output": "Two buttons rendered: Submit and Cancel\nClicking each shows the respective alert",
                        "flowchart": None,
                        "key_points": "Component reusability reduces development time\nVirtual DOM minimizes expensive real DOM operations\nDeclarative style makes code easier to read and maintain\nOne-way data flow prevents unexpected side effects\nHuge ecosystem accelerates development",
                        "remember_this": "React's superpower is its component model + Virtual DOM. Together, they make large applications fast and manageable."
                    },
                    {
                        "question_number": 3,
                        "question": "What problems does React solve?",
                        "quick_answer": "React solves the problem of building large, dynamic UIs that are difficult to maintain with vanilla JavaScript or jQuery.",
                        "explanation": "Before React, developers used vanilla JavaScript or jQuery to update the DOM manually. This caused several problems:\n\n1. DOM Manipulation Complexity: Manually tracking which DOM elements to update when data changes is error-prone and hard to maintain at scale.\n\n2. Spaghetti Code: As apps grew, jQuery-based code became tangled and hard to debug.\n\n3. Performance Issues: Re-rendering the entire page or large DOM sections on every update was slow.\n\n4. No Component Structure: Code had no natural way to organize into reusable, isolated pieces.\n\nReact solves these by:\n- Providing a component model that organizes code into self-contained units\n- Using a Virtual DOM that batches and minimizes actual DOM changes\n- Offering a predictable data flow that makes debugging straightforward",
                        "real_world_example": "In a shopping cart, when a user adds an item, only the cart counter and the cart list need to update — not the entire product listing page.\n\nWith vanilla JS you'd manually select the DOM elements and update them. With React, state change triggers automatic re-rendering of only the affected components.",
                        "code_example": "// Vanilla JS approach (manual, fragile)\ndocument.getElementById('count').innerText = newCount;\n\n// React approach (declarative, automatic)\nfunction CartCounter({ count }) {\n  return <span id=\"count\">{count}</span>;\n}\n// React automatically updates the DOM when 'count' changes",
                        "expected_output": "Both display the count, but React automatically manages updates",
                        "flowchart": "State Changes\n     ↓\nReact detects change\n     ↓\nCreates new Virtual DOM\n     ↓\nDiffs old vs new Virtual DOM\n     ↓\nUpdates only changed Real DOM nodes",
                        "key_points": "Eliminates manual DOM manipulation\nSolves spaghetti code in large applications\nFixes performance issues from full-page re-renders\nProvides component structure for organized code\nMakes UI state predictable",
                        "remember_this": "React was built to solve the problem of maintaining large UIs as they scale. It replaces error-prone manual DOM manipulation with a clean, declarative component model."
                    },
                    {
                        "question_number": 4,
                        "question": "Where is React used in real applications?",
                        "quick_answer": "React is used in the frontends of Facebook, Instagram, Netflix, Airbnb, WhatsApp Web, Atlassian, and thousands of other production applications.",
                        "explanation": "React is used across industries and company sizes — from startups to Fortune 500 companies.\n\nCommon use cases:\n1. Single Page Applications (SPAs): Gmail-style apps where navigation doesn't reload the page.\n2. Dashboards: Data-heavy admin panels with real-time updates.\n3. E-commerce UIs: Product listings, filters, and dynamic shopping carts.\n4. Social Media Feeds: Infinite-scroll feeds with real-time comments and likes.\n5. Mobile Apps: Via React Native (same concept, different renderer, targets iOS and Android).\n6. Static Sites: Via Next.js for marketing pages and blogs with SEO support.",
                        "real_world_example": "Facebook uses React for its news feed. When you like a post, only the like button component re-renders — not the entire feed.\n\nAirbnb uses React for search result pages with dynamic filters. Netflix uses React for their browse UI with smooth hover previews.",
                        "code_example": "// Example: A like button component\nfunction LikeButton({ postId }) {\n  const [liked, setLiked] = React.useState(false);\n  const [count, setCount] = React.useState(0);\n\n  function handleLike() {\n    setLiked(true);\n    setCount(count + 1);\n  }\n\n  return (\n    <button onClick={handleLike} disabled={liked}>\n      {liked ? `♥ ${count}` : `♡ Like`}\n    </button>\n  );\n}",
                        "expected_output": "Button shows: ♡ Like\nAfter click shows: ♥ 1",
                        "flowchart": None,
                        "key_points": "Used by Facebook, Instagram, Netflix, Airbnb\nPowers Single Page Applications (SPAs)\nUsed for dashboards, e-commerce, social feeds\nReact Native extends React to mobile (iOS/Android)\nNext.js extends React to server-side rendering and static sites",
                        "remember_this": "React is everywhere. Any modern web app that feels fast and responsive without full page reloads is likely using React or a similar library."
                    },
                    {
                        "question_number": 5,
                        "question": "What are the advantages of React?",
                        "quick_answer": "React's main advantages are reusable components, Virtual DOM performance, one-way data flow, rich ecosystem, and strong community support.",
                        "explanation": "Key advantages of React:\n\n1. Component Reusability: Write a component once and use it everywhere — reducing duplication.\n\n2. Virtual DOM: React only updates what changed in the real DOM, making UIs fast.\n\n3. Declarative UI: Code describes what to render, not how — easier to read and maintain.\n\n4. One-Way Data Flow: Data flows parent → child, making state changes predictable.\n\n5. Rich Ecosystem: React Router, Redux, React Query, Next.js, and thousands of npm packages.\n\n6. Developer Tools: React DevTools allow inspection of the component tree and state.\n\n7. SEO with Next.js: Server-side rendering support through Next.js makes React apps SEO-friendly.\n\n8. Large Community: Millions of developers, abundant tutorials, Stack Overflow answers, and GitHub projects.",
                        "real_world_example": "A design system at a company might have a Button, Input, Modal, and Card component. All 20 developers on the team use the same components — ensuring visual consistency and avoiding duplicated code.",
                        "code_example": "// Reusable Card component\nfunction Card({ title, description, imageUrl }) {\n  return (\n    <div className=\"card\">\n      <img src={imageUrl} alt={title} />\n      <h3>{title}</h3>\n      <p>{description}</p>\n    </div>\n  );\n}\n\n// Use it anywhere:\n<Card title=\"React Basics\" description=\"Learn React\" imageUrl=\"/react.png\" />\n<Card title=\"Advanced Hooks\" description=\"Deep dive\" imageUrl=\"/hooks.png\" />",
                        "expected_output": "Two card components rendered with different content",
                        "flowchart": None,
                        "key_points": "Reusable components reduce code duplication\nVirtual DOM ensures high performance\nDeclarative code is easier to understand\nOne-way data flow prevents bugs\nLarge ecosystem covers almost every use case\nStrong community and excellent documentation",
                        "remember_this": "React's biggest advantage is its component-based architecture. Everything else (Virtual DOM, data flow, ecosystem) flows from that core idea."
                    },
                ],
            },
            {
                "title": "Features of React",
                "description": "Core features that make React powerful: JSX, Virtual DOM, components, and more.",
                "topic_number": 2,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "What is a React component?",
                        "quick_answer": "A React component is a reusable, self-contained piece of UI that returns JSX describing what to render.",
                        "explanation": "A React component is a JavaScript function (or class) that:\n- Accepts inputs called props\n- Returns JSX (what should be displayed on screen)\n- Is reusable — you can use it multiple times\n- Is self-contained — its logic and UI are in one place\n\nThere are two types:\n1. Function Components (modern, preferred): Plain JavaScript functions\n2. Class Components (legacy): ES6 classes that extend React.Component\n\nToday, function components with Hooks are the standard.",
                        "real_world_example": "A product card on an e-commerce site — showing image, title, price, and an Add to Cart button — is a perfect React component. You can reuse it for every product in your store, passing different data each time.",
                        "code_example": "// Function Component\nfunction ProductCard({ name, price, image }) {\n  return (\n    <div className=\"product-card\">\n      <img src={image} alt={name} />\n      <h3>{name}</h3>\n      <p>${price}</p>\n      <button>Add to Cart</button>\n    </div>\n  );\n}\n\n// Usage:\n<ProductCard name=\"Laptop\" price={999} image=\"/laptop.jpg\" />\n<ProductCard name=\"Phone\" price={499} image=\"/phone.jpg\" />",
                        "expected_output": "Two product cards with different content rendered",
                        "flowchart": None,
                        "key_points": "Components are reusable UI building blocks\nThey accept props as input and return JSX\nFunction components are the modern standard\nComponents can be nested inside each other\nEach component manages its own concerns",
                        "remember_this": "Think of components like LEGO blocks. Each block has a specific shape and function, and you snap them together to build complex UIs."
                    },
                    {
                        "question_number": 2,
                        "question": "What is JSX?",
                        "quick_answer": "JSX (JavaScript XML) is a syntax extension that lets you write HTML-like code inside JavaScript files.",
                        "explanation": "JSX stands for JavaScript XML. It is a syntax extension for JavaScript that looks like HTML but is actually JavaScript.\n\nJSX is not valid JavaScript by itself — a tool called Babel transforms it into regular React.createElement() calls before the browser runs it.\n\nBenefits of JSX:\n- Readable: HTML-like syntax is familiar to developers\n- Powerful: You can embed JavaScript expressions with {}\n- Syntax checking: Errors are caught at compile time\n\nImportant differences from HTML:\n- className instead of class (class is a reserved word in JS)\n- htmlFor instead of for\n- All tags must be closed (even self-closing: <img />)\n- camelCase attribute names (onClick, onChange)",
                        "real_world_example": "When building a weather app, JSX lets you write the temperature display as: <h1>{temperature}°C</h1> instead of the verbose document.createElement('h1') approach.",
                        "code_example": "// JSX\nfunction Greeting({ name, age }) {\n  return (\n    <div className=\"greeting\">\n      <h1>Hello, {name}!</h1>\n      <p>You are {age} years old.</p>\n      {age >= 18 && <span>You are an adult.</span>}\n    </div>\n  );\n}\n\n// What Babel compiles JSX to:\n// React.createElement('div', { className: 'greeting' },\n//   React.createElement('h1', null, 'Hello, ', name, '!'),\n//   React.createElement('p', null, 'You are ', age, ' years old.')\n// )",
                        "expected_output": "Hello, Alice!\nYou are 25 years old.\nYou are an adult.",
                        "flowchart": "JSX code\n   ↓\nBabel transforms JSX\n   ↓\nReact.createElement() calls\n   ↓\nVirtual DOM objects\n   ↓\nReal DOM nodes",
                        "key_points": "JSX is JavaScript + HTML-like syntax\nMust use className instead of class\nAll tags must be closed\nJavaScript expressions go inside {}\nBabel compiles JSX to React.createElement()\nConditional rendering with && or ternary operators",
                        "remember_this": "JSX is syntactic sugar — it looks like HTML but is actually JavaScript. Every JSX element becomes a React.createElement() call."
                    },
                    {
                        "question_number": 3,
                        "question": "What is the Virtual DOM?",
                        "quick_answer": "The Virtual DOM is a lightweight JavaScript copy of the real DOM that React uses to calculate the minimum changes needed before updating the browser.",
                        "explanation": "The DOM (Document Object Model) is the browser's representation of the web page. Manipulating the real DOM is slow because every change may cause the browser to recalculate layout and repaint.\n\nReact solves this with the Virtual DOM:\n1. React maintains a Virtual DOM — a lightweight JavaScript object tree\n2. When state changes, React creates a new Virtual DOM\n3. React compares (diffs) the old and new Virtual DOM\n4. React calculates the minimum set of changes (reconciliation)\n5. React applies only those changes to the real DOM\n\nThis process is called reconciliation and the diffing algorithm runs in O(n) time.",
                        "real_world_example": "On a Twitter-like feed with 100 posts, when one post gets a new like, only the like counter for that specific post updates in the real DOM. React's Virtual DOM ensures the other 99 posts are not touched.",
                        "code_example": "function Counter() {\n  const [count, setCount] = React.useState(0);\n\n  // When setCount is called:\n  // 1. New Virtual DOM created\n  // 2. Diffed with previous Virtual DOM\n  // 3. Only the <span> text node updates in real DOM\n\n  return (\n    <div>\n      <span>{count}</span>\n      <button onClick={() => setCount(count + 1)}>+</button>\n    </div>\n  );\n}",
                        "expected_output": "Shows counter at 0. Each click increments by 1. Only the number updates in DOM.",
                        "flowchart": "State changes\n      ↓\nNew Virtual DOM created\n      ↓\nDiff: old Virtual DOM vs new\n      ↓\nMinimal change list calculated\n      ↓\nOnly changed nodes updated in Real DOM\n      ↓\nBrowser re-paints affected area only",
                        "key_points": "Virtual DOM is a JS representation of the real DOM\nFaster than directly manipulating the real DOM\nReact diffs old and new Virtual DOM after state change\nOnly changed elements are updated in the real DOM\nThis process is called Reconciliation",
                        "remember_this": "Virtual DOM = React's scratch pad. React works out all changes on the scratch pad first, then applies only the final result to the real page — minimizing browser work."
                    },
                    {
                        "question_number": 4,
                        "question": "What is component reusability?",
                        "quick_answer": "Component reusability means building a UI piece once and using it in multiple places with different data, reducing code duplication.",
                        "explanation": "Component reusability is one of React's most powerful features.\n\nInstead of copying and pasting similar HTML markup in multiple places, you create a single component and pass different data to it through props.\n\nBenefits:\n1. DRY Code (Don't Repeat Yourself): One change updates all instances\n2. Consistency: Same component = same look and behavior everywhere\n3. Maintainability: Fix a bug once, it's fixed everywhere\n4. Testability: Test the component once\n5. Design Systems: Companies build entire libraries of reusable components",
                        "real_world_example": "A news website might display articles in a card format throughout the site — on the homepage, category pages, and search results. One ArticleCard component handles all of these with different data passed in through props.",
                        "code_example": "// One reusable component\nfunction StatCard({ icon, label, value, color }) {\n  return (\n    <div className=\"stat-card\" style={{ borderColor: color }}>\n      <span>{icon}</span>\n      <strong>{value}</strong>\n      <p>{label}</p>\n    </div>\n  );\n}\n\n// Reused 4 times with different props\nfunction Dashboard() {\n  return (\n    <div className=\"stats\">\n      <StatCard icon=\"👥\" label=\"Users\" value={1204} color=\"blue\" />\n      <StatCard icon=\"💰\" label=\"Revenue\" value=\"$8,400\" color=\"green\" />\n      <StatCard icon=\"📦\" label=\"Orders\" value={342} color=\"orange\" />\n      <StatCard icon=\"⭐\" label=\"Rating\" value=\"4.9\" color=\"purple\" />\n    </div>\n  );\n}",
                        "expected_output": "Four stat cards displayed with different icons, labels, values, and colors",
                        "flowchart": None,
                        "key_points": "Write once, use everywhere with different props\nDRY principle prevents code duplication\nA bug fix in the component fixes all usages\nDesign systems are built on reusable components\nProps make components flexible and configurable",
                        "remember_this": "If you're copying and pasting the same markup, make it a component. Props are how you customize it per usage."
                    },
                    {
                        "question_number": 5,
                        "question": "Why is React suitable for interactive applications?",
                        "quick_answer": "React is ideal for interactive applications because state changes automatically trigger targeted UI updates without full page reloads.",
                        "explanation": "Interactive applications need to respond to user actions (clicks, typing, scrolling) and update the UI accordingly — often many times per second.\n\nReact excels at this because:\n1. State Management: React's useState hook tracks data that changes over time\n2. Automatic Re-rendering: When state changes, React automatically re-renders affected components\n3. Event Handling: React has a unified event system (onClick, onChange, onSubmit)\n4. Efficient Updates: Virtual DOM ensures only changed parts update\n5. Predictable Flow: Data flows one way, making complex interactions easier to debug\n\nThis makes React perfect for: forms, real-time dashboards, games, chat apps, collaborative tools, and any UI that changes frequently.",
                        "real_world_example": "A live search input that filters results as you type is a classic interactive use case. React handles the keystrokes (events), updates the search term (state), and re-renders only the filtered results list — all in milliseconds.",
                        "code_example": "function LiveSearch({ items }) {\n  const [query, setQuery] = React.useState(\"\");\n\n  const filtered = items.filter(item =>\n    item.toLowerCase().includes(query.toLowerCase())\n  );\n\n  return (\n    <div>\n      <input\n        type=\"text\"\n        placeholder=\"Search...\"\n        value={query}\n        onChange={(e) => setQuery(e.target.value)}\n      />\n      <ul>\n        {filtered.map((item, i) => (\n          <li key={i}>{item}</li>\n        ))}\n      </ul>\n    </div>\n  );\n}",
                        "expected_output": "Search input filters the list in real-time as the user types",
                        "flowchart": "User types in input\n      ↓\nonChange event fires\n      ↓\nsetQuery updates state\n      ↓\nComponent re-renders\n      ↓\nFiltered list recalculated\n      ↓\nOnly list updates in DOM",
                        "key_points": "State tracks data that changes in response to user actions\nState changes automatically trigger re-renders\nEvent handlers (onClick, onChange) respond to user input\nVirtual DOM ensures only changed parts update\nOne-way data flow keeps interactive apps predictable",
                        "remember_this": "React = State + Events + Re-rendering. Change the state, and React handles updating the UI. You never manually touch the DOM."
                    },
                ],
            },
            {
                "title": "React Environment Setup",
                "description": "Setting up a React development environment using Vite.",
                "topic_number": 3,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "What do you need to install before creating a React app?",
                        "quick_answer": "You need Node.js (which includes npm) installed on your computer.",
                        "explanation": "Before creating a React project you need:\n\n1. Node.js: A JavaScript runtime that lets you run JavaScript outside the browser. Download from nodejs.org.\n\n2. npm (Node Package Manager): Comes bundled with Node.js. Used to install React and other packages.\n\n3. A code editor: Visual Studio Code is the most popular choice for React development.\n\nVerify your installation:\n- node --version (should show v18 or higher)\n- npm --version (should show v9 or higher)",
                        "real_world_example": "Node.js is to React what Python is to Django — it's the runtime environment that makes everything work on your local machine.",
                        "code_example": "# Check if Node.js is installed\nnode --version\n# Expected: v18.x.x or higher\n\n# Check if npm is installed\nnpm --version\n# Expected: 9.x.x or higher",
                        "expected_output": "v20.11.0\n10.2.4",
                        "flowchart": None,
                        "key_points": "Install Node.js from nodejs.org\nnpm is included with Node.js\nVS Code is the recommended editor\nNode v18+ is recommended for React projects",
                        "remember_this": "You can't build React apps without Node.js. Install it first, verify with 'node --version', then create your project."
                    },
                    {
                        "question_number": 2,
                        "question": "How do you create a new React project with Vite?",
                        "quick_answer": "Run: npm create vite@latest my-app -- --template react, then cd my-app && npm install && npm run dev",
                        "explanation": "Vite is the modern, fast build tool for React. It replaced Create React App as the recommended way to start a React project.\n\nSteps:\n1. Create the project\n2. Navigate into the folder\n3. Install dependencies\n4. Start the development server",
                        "real_world_example": "Every professional React project starts with a tool like Vite. It sets up the development environment, build pipeline, and hot module replacement (instant updates when you save a file) automatically.",
                        "code_example": "# Step 1: Create the project\nnpm create vite@latest my-react-app -- --template react\n\n# Step 2: Navigate into the project\ncd my-react-app\n\n# Step 3: Install all dependencies\nnpm install\n\n# Step 4: Start the development server\nnpm run dev",
                        "expected_output": "  VITE v5.x.x  ready in 200ms\n\n  ➜  Local:   http://localhost:5173/\n  ➜  Network: use --host to expose",
                        "flowchart": "npm create vite@latest\n        ↓\nProject folder created\n        ↓\nnpm install\n        ↓\nnode_modules installed\n        ↓\nnpm run dev\n        ↓\nDev server at localhost:5173",
                        "key_points": "Vite is faster than Create React App\nnpm create vite@latest bootstraps the project\nAlways run npm install after creating the project\nnpm run dev starts the hot-reloading dev server\nOpen localhost:5173 in your browser to see your app",
                        "remember_this": "Four commands: create → cd → npm install → npm run dev. That's all you need to have a React app running."
                    },
                    {
                        "question_number": 3,
                        "question": "What is the structure of a Vite React project?",
                        "quick_answer": "A Vite React project has src/ for your code, public/ for static files, index.html as the entry point, and package.json for dependencies.",
                        "explanation": "After running npm create vite@latest, you get this structure:\n\nmy-react-app/\n├── public/          → Static files (favicon, images)\n├── src/\n│   ├── App.jsx      → Main App component\n│   ├── App.css      → App styles\n│   ├── main.jsx     → Entry point (mounts App to DOM)\n│   └── index.css   → Global styles\n├── index.html       → HTML shell React injects into\n├── package.json     → Project dependencies and scripts\n├── vite.config.js   → Vite configuration\n└── node_modules/    → Installed packages (never edit)\n\nYou will spend 95% of your time in the src/ folder.",
                        "real_world_example": "src/ is your workspace. Everything you build goes here. The public/ folder holds assets that shouldn't be processed by Vite (like a favicon).",
                        "code_example": "// src/main.jsx — Entry point\nimport React from 'react'\nimport ReactDOM from 'react-dom/client'\nimport App from './App.jsx'\nimport './index.css'\n\nReactDOM.createRoot(document.getElementById('root')).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>,\n)",
                        "expected_output": "React mounts your App component into the <div id='root'> in index.html",
                        "flowchart": "index.html (has <div id=\"root\">)\n        ↓\nmain.jsx (ReactDOM.createRoot)\n        ↓\nApp.jsx (root component)\n        ↓\nAll other components",
                        "key_points": "src/ is where all your React code lives\nmain.jsx is the JavaScript entry point\nApp.jsx is the root React component\nindex.html is the HTML shell\nnode_modules/ is managed by npm — never edit it manually",
                        "remember_this": "The React app mounts inside the <div id='root'> in index.html. main.jsx connects React to that div. App.jsx is your starting component."
                    },
                    {
                        "question_number": 4,
                        "question": "What is Hot Module Replacement (HMR) in Vite?",
                        "quick_answer": "HMR is a feature where Vite instantly updates only the changed module in the browser without a full page refresh during development.",
                        "explanation": "Hot Module Replacement (HMR) is one of Vite's most useful development features.\n\nWhen you save a file:\n1. Without HMR: The browser fully refreshes — you lose all form inputs and state\n2. With HMR: Only the changed component updates — state is preserved\n\nThis makes development much faster because:\n- No waiting for full page reloads\n- Form data and state stay while you tweak styles or logic\n- Feedback is instant (< 50ms in most cases)\n\nVite's HMR is significantly faster than Create React App's webpack-based HMR.",
                        "real_world_example": "While building a multi-step form, you can tweak the styling of Step 3 without losing the form data you entered in Steps 1 and 2. The component updates instantly without resetting.",
                        "code_example": "// Just save any .jsx or .css file\n// Vite automatically updates the browser\n// No configuration needed\n\n// vite.config.js — HMR is enabled by default\nimport { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\n\nexport default defineConfig({\n  plugins: [react()],\n})",
                        "expected_output": "Save a file → browser updates in <100ms without full reload",
                        "flowchart": None,
                        "key_points": "HMR updates only changed modules, not the full page\nPreserves application state during development\nVite's HMR is extremely fast (<100ms)\nEnabled by default in Vite projects\nFar superior to Create React App's speed",
                        "remember_this": "HMR = instant feedback. Save your file, see the change. No page reload, no state loss."
                    },
                    {
                        "question_number": 5,
                        "question": "How do you add a new component to a React project?",
                        "quick_answer": "Create a new .jsx file in src/, write and export a function component, then import and use it in another component.",
                        "explanation": "Adding a new component follows a consistent pattern:\n\n1. Create a file in src/ (e.g., src/components/Header.jsx)\n2. Write your function component\n3. Export it (export default or named export)\n4. Import it in the file where you want to use it\n5. Place it as JSX in the return statement\n\nConventions:\n- Component names start with capital letters (Header, not header)\n- File names match the component name (Header.jsx)\n- Components go in src/components/ (common convention)",
                        "real_world_example": "Building a landing page: you'd create Header.jsx, Hero.jsx, Features.jsx, and Footer.jsx. Each is its own file, imported and assembled in App.jsx.",
                        "code_example": "// Step 1: Create src/components/Header.jsx\nfunction Header() {\n  return (\n    <header>\n      <h1>My App</h1>\n      <nav>\n        <a href=\"/\">Home</a>\n        <a href=\"/about\">About</a>\n      </nav>\n    </header>\n  );\n}\n\nexport default Header;\n\n// Step 2: Import and use in App.jsx\nimport Header from './components/Header';\n\nfunction App() {\n  return (\n    <div>\n      <Header />\n      <main>Main content here</main>\n    </div>\n  );\n}",
                        "expected_output": "Header with navigation rendered at the top of the page",
                        "flowchart": "Create .jsx file\n       ↓\nWrite function component\n       ↓\nexport default ComponentName\n       ↓\nimport in parent file\n       ↓\n<ComponentName /> in JSX",
                        "key_points": "Component file names use PascalCase (MyComponent.jsx)\nExport with 'export default' for single exports\nImport with 'import Name from path'\nComponent names in JSX must start with capital letter\nOrganize components in src/components/ folder",
                        "remember_this": "Create file → write function → export → import → use as JSX tag. That's the complete React component workflow."
                    },
                ],
            },
        ],
    },
    {
        "lesson_title": "Components and Props",
        "topics": [
            {
                "title": "Understanding Props",
                "description": "How React passes data from parent to child components using props.",
                "topic_number": 1,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "What are props in React?",
                        "quick_answer": "Props (properties) are read-only inputs passed from a parent component to a child component to customize its output.",
                        "explanation": "Props are React's way of passing data from parent components to child components.\n\nKey characteristics:\n- Props are read-only — the child cannot modify them\n- They flow one direction: parent → child\n- Any JavaScript value can be a prop (string, number, array, object, function)\n- Props are received as the first argument of a function component\n\nThink of props like function arguments — they customize how a component behaves without the component needing to know the data source.",
                        "real_world_example": "A reusable ProfileCard component receives name, avatar, and role as props. The Marketing team renders it with their data, the Engineering team with theirs — same component, different data.",
                        "code_example": "// Child: receives props\nfunction ProfileCard({ name, role, avatar }) {\n  return (\n    <div className=\"profile-card\">\n      <img src={avatar} alt={name} />\n      <h2>{name}</h2>\n      <p>{role}</p>\n    </div>\n  );\n}\n\n// Parent: passes props\nfunction App() {\n  return (\n    <ProfileCard\n      name=\"Alice Johnson\"\n      role=\"Senior Engineer\"\n      avatar=\"/alice.jpg\"\n    />\n  );\n}",
                        "expected_output": "Profile card showing Alice Johnson's photo, name, and role",
                        "flowchart": "Parent Component\n       ↓ (passes props)\nChild Component\n  receives { name, role, avatar }",
                        "key_points": "Props flow from parent to child only\nProps are read-only (immutable in the child)\nAny JS value can be a prop\nReceived as the first argument of a function component\nProps make components flexible and reusable",
                        "remember_this": "Props = parameters for your component. Just like a function takes arguments, a component takes props."
                    },
                    {
                        "question_number": 2,
                        "question": "How do you pass and receive props?",
                        "quick_answer": "Pass props like HTML attributes in JSX; receive them as the first argument of the function component (usually destructured).",
                        "explanation": "Passing props: In the parent's JSX, add attributes to the component tag.\nReceiving props: In the child function, accept the props object as the first argument.\n\nTwo styles of receiving:\n1. As a whole object: function Button(props) — access with props.label\n2. Destructured: function Button({ label, onClick }) — access directly\n\nDestructuring is preferred — cleaner and more readable.",
                        "real_world_example": "A Submit Button component receives its label text and click handler as props, so the same button can say 'Login', 'Register', or 'Save Settings' depending on where it's used.",
                        "code_example": "// Style 1: props object\nfunction Greeting(props) {\n  return <h1>Hello, {props.name}!</h1>;\n}\n\n// Style 2: destructured (preferred)\nfunction Greeting({ name, age }) {\n  return (\n    <div>\n      <h1>Hello, {name}!</h1>\n      <p>Age: {age}</p>\n    </div>\n  );\n}\n\n// Parent passes:\n<Greeting name=\"Bob\" age={30} />",
                        "expected_output": "Hello, Bob!\nAge: 30",
                        "flowchart": None,
                        "key_points": "JSX attributes become props in the child\nUse curly braces for non-string values: age={30}\nDestructuring is cleaner than using props.x everywhere\nString props can omit braces: name=\"Bob\"\nFunction props use arrow functions: onClick={() => doThing()}",
                        "remember_this": "Pass props with JSX attributes. Receive them by destructuring in the function signature. Never use props.x — always destructure."
                    },
                    {
                        "question_number": 3,
                        "question": "What are default props?",
                        "quick_answer": "Default props provide fallback values for props that might not be passed by the parent, ensuring the component always has valid data.",
                        "explanation": "Default props ensure a component works even when a prop is not provided.\n\nTwo ways to define them:\n1. Default parameter values (modern, preferred): function Button({ label = 'Click me' })\n2. Component.defaultProps (legacy): Button.defaultProps = { label: 'Click me' }\n\nDefault props are useful for:\n- Optional configuration props\n- Preventing undefined errors\n- Providing sensible defaults (e.g., a button color defaulting to 'blue')",
                        "real_world_example": "A modal component might have a size prop that defaults to 'medium'. If the developer doesn't specify a size, the medium size is used automatically.",
                        "code_example": "// Default props with destructuring (modern approach)\nfunction Button({\n  label = \"Click me\",\n  color = \"blue\",\n  disabled = false\n}) {\n  return (\n    <button\n      style={{ backgroundColor: color }}\n      disabled={disabled}\n    >\n      {label}\n    </button>\n  );\n}\n\n// Without props — uses all defaults\n<Button />\n// Renders: blue button with \"Click me\" label\n\n// With some props — overrides defaults\n<Button label=\"Submit\" color=\"green\" />\n// Renders: green button with \"Submit\" label",
                        "expected_output": "Button 1: blue, 'Click me'\nButton 2: green, 'Submit'",
                        "flowchart": None,
                        "key_points": "Default values go in function parameter destructuring\nPrevents 'undefined' errors when props are omitted\nDefault props are overridden when the parent passes a value\nLegacy: ComponentName.defaultProps = {} (avoid in new code)",
                        "remember_this": "function MyComp({ value = 'default' }) — put defaults right in the parameter list. Simple and readable."
                    },
                    {
                        "question_number": 4,
                        "question": "What is prop drilling and why is it a problem?",
                        "quick_answer": "Prop drilling is passing props through multiple intermediate components that don't use the data themselves, just to reach a deeply nested component.",
                        "explanation": "Prop drilling happens when you need to pass data from a top-level component to a deeply nested child, and the intermediate components are forced to accept and pass props they don't actually use.\n\nWhy it's a problem:\n1. Verbose code: Intermediate components have unnecessary prop declarations\n2. Maintenance burden: Adding/removing a prop requires updating every component in the chain\n3. Tight coupling: Components become dependent on a data structure they don't use\n\nSolutions:\n- React Context API (built-in)\n- State management libraries (Redux, Zustand)\n- Component composition",
                        "real_world_example": "A user's theme preference stored in App needs to reach a Button inside a Sidebar inside a Layout inside a Page. Without context, every component in between must receive and pass the theme prop.",
                        "code_example": "// Prop Drilling — theme passed through intermediaries\nfunction App() {\n  const theme = \"dark\";\n  return <Page theme={theme} />;\n}\n\nfunction Page({ theme }) {\n  // Page doesn't use theme, just passes it\n  return <Layout theme={theme} />;\n}\n\nfunction Layout({ theme }) {\n  // Layout doesn't use theme, just passes it\n  return <Sidebar theme={theme} />;\n}\n\nfunction Sidebar({ theme }) {\n  // Finally uses theme!\n  return <div className={theme}>Sidebar</div>;\n}",
                        "expected_output": "Sidebar renders with dark theme after drilling through 3 components",
                        "flowchart": "App (theme=\"dark\")\n      ↓ props\nPage (passes theme)\n      ↓ props\nLayout (passes theme)\n      ↓ props\nSidebar (USES theme)",
                        "key_points": "Prop drilling = passing props through many layers unnecessarily\nIntermediate components receive props they don't use\nHard to maintain as the tree grows\nReact Context API solves this for most cases\nRedux or Zustand for complex global state",
                        "remember_this": "If you find yourself passing the same prop through 3+ components that don't use it, you have prop drilling. Use React Context to fix it."
                    },
                    {
                        "question_number": 5,
                        "question": "What is the children prop?",
                        "quick_answer": "The children prop is a special built-in prop that receives whatever JSX is placed between a component's opening and closing tags.",
                        "explanation": "The children prop lets you create wrapper components — components that wrap arbitrary content.\n\nWhen you write:\n<Card><p>Hello</p></Card>\n\nThe <p>Hello</p> becomes the children prop inside Card.\n\nUse cases:\n- Layout components (Card, Modal, Panel)\n- HOCs (Higher Order Components)\n- Generic containers\n\nchildren can be any JSX — text, elements, or even other components.",
                        "real_world_example": "A Card component at a design system level doesn't know what content it will hold. It just provides the border, shadow, and padding. Whatever the developer puts inside becomes children.",
                        "code_example": "// Card accepts anything as children\nfunction Card({ children, title }) {\n  return (\n    <div className=\"card\">\n      {title && <h2 className=\"card-title\">{title}</h2>}\n      <div className=\"card-body\">\n        {children}\n      </div>\n    </div>\n  );\n}\n\n// Usage — anything inside becomes children\nfunction App() {\n  return (\n    <Card title=\"User Info\">\n      <p>Name: Alice</p>\n      <p>Email: alice@example.com</p>\n      <button>Edit Profile</button>\n    </Card>\n  );\n}",
                        "expected_output": "Card with 'User Info' title, containing name, email, and edit button",
                        "flowchart": None,
                        "key_points": "children is an automatic built-in prop\nReceives JSX between opening and closing tags\nUsed to build flexible wrapper/container components\nCan be any valid JSX (elements, text, components)\nPattern used in layout components, modals, panels",
                        "remember_this": "Anything between <MyComponent> and </MyComponent> is automatically available as props.children inside MyComponent."
                    },
                ],
            },
        ],
    },
    {
        "lesson_title": "State and Events",
        "topics": [
            {
                "title": "Understanding State with useState",
                "description": "Managing dynamic data in components using the useState hook.",
                "topic_number": 1,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "What is state in React?",
                        "quick_answer": "State is data stored inside a component that can change over time. When state changes, React re-renders the component with the new data.",
                        "explanation": "State is the memory of a component.\n\nWhile props come from outside (parent → child), state is managed inside the component itself.\n\nKey characteristics:\n- State is local to the component (private by default)\n- State changes trigger a re-render\n- State should only hold data that affects what the UI shows\n- State is initialized with a default value\n\nExamples of state:\n- A counter's current number\n- Whether a dropdown is open or closed\n- The text in a search input\n- Whether data is loading\n- A list of items fetched from an API",
                        "real_world_example": "In a shopping cart, the item count is state. When a user adds an item, the count state updates, React re-renders the cart icon showing the new count.",
                        "code_example": "import { useState } from 'react';\n\nfunction Counter() {\n  // Declare state: count starts at 0\n  const [count, setCount] = useState(0);\n\n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => setCount(count + 1)}>+</button>\n      <button onClick={() => setCount(count - 1)}>-</button>\n      <button onClick={() => setCount(0)}>Reset</button>\n    </div>\n  );\n}",
                        "expected_output": "Count: 0\n[+] [-] [Reset] buttons\nClicking + increments, - decrements, Reset resets to 0",
                        "flowchart": "User clicks button\n       ↓\nsetCount called with new value\n       ↓\nReact schedules re-render\n       ↓\nComponent re-renders with new count\n       ↓\nUpdated UI displayed",
                        "key_points": "State is data that changes over time\nuseState hook declares state in function components\nconst [value, setValue] = useState(initialValue)\nCalling setValue triggers a re-render\nNever mutate state directly — always use the setter",
                        "remember_this": "State = component's memory. When state changes, React re-paints the UI. Never do count++ — always do setCount(count + 1)."
                    },
                    {
                        "question_number": 2,
                        "question": "How do you declare and update state with useState?",
                        "quick_answer": "const [state, setState] = useState(initialValue); — call setState with the new value to update and trigger a re-render.",
                        "explanation": "useState returns an array with exactly two items:\n1. The current state value\n2. A function to update it\n\nArray destructuring assigns names to these:\nconst [count, setCount] = useState(0);\n\nRules:\n- Always call the setter function to change state (never mutate directly)\n- The setter can accept a new value: setState(newValue)\n- Or a function: setState(prev => prev + 1) — safer for values depending on previous state\n- useState can hold any data type: number, string, boolean, array, object",
                        "real_world_example": "A toggle switch component: useState(false) starts it off. Clicking calls setIsOn(!isOn) to flip between true and false, switching the UI between on/off states.",
                        "code_example": "import { useState } from 'react';\n\nfunction ToggleSwitch() {\n  const [isOn, setIsOn] = useState(false);\n\n  const toggle = () => setIsOn(prev => !prev);\n\n  return (\n    <div>\n      <button\n        onClick={toggle}\n        style={{ background: isOn ? 'green' : 'gray' }}\n      >\n        {isOn ? 'ON' : 'OFF'}\n      </button>\n      <p>Switch is: {isOn ? 'enabled' : 'disabled'}</p>\n    </div>\n  );\n}",
                        "expected_output": "Gray OFF button → click → Green ON button\nText updates to reflect current state",
                        "flowchart": None,
                        "key_points": "useState(initialValue) returns [value, setter]\nAlways use setter function to update state\nUse functional update setState(prev => ...) when using previous value\nuseState can store any JavaScript value\nMultiple useState calls are independent",
                        "remember_this": "The pattern is always: const [thing, setThing] = useState(startingValue). Name the setter set + thing by convention."
                    },
                    {
                        "question_number": 3,
                        "question": "What is the difference between state and props?",
                        "quick_answer": "Props come from the parent and are read-only; state is managed inside the component and can be changed by the component itself.",
                        "explanation": "Props vs State:\n\n| Feature        | Props               | State              |\n|---------------|---------------------|--------------------|  \n| Source        | Parent component    | Component itself   |\n| Mutability    | Read-only (immutable)| Can be changed     |\n| Who controls  | Parent              | Component itself   |\n| When to use   | Pass data in        | Track changing data|\n\nSimple rule:\n- If data comes from outside and stays fixed → Props\n- If data changes within the component over time → State",
                        "real_world_example": "A user's username passed to a profile page is a prop (parent decides it). Whether the edit form is open or closed is state (the profile page controls it).",
                        "code_example": "function ProfilePage({ username }) {  // username = PROP\n  const [isEditing, setIsEditing] = useState(false); // isEditing = STATE\n\n  return (\n    <div>\n      <h1>{username}</h1>  {/* prop */}\n      {isEditing ? (\n        <form>...</form>\n      ) : (\n        <button onClick={() => setIsEditing(true)}>\n          Edit Profile\n        </button>\n      )}\n    </div>\n  );\n}",
                        "expected_output": "Profile page for 'username' with Edit button. Clicking opens edit form.",
                        "flowchart": None,
                        "key_points": "Props: received from parent, read-only, external data\nState: managed inside, changeable, internal data\nBoth changing props and changing state trigger re-renders\nA component can have both props and state simultaneously\nIf you find yourself trying to change a prop, use state instead",
                        "remember_this": "Props = what others tell you. State = what you remember yourself. If it changes inside your component, it's state."
                    },
                    {
                        "question_number": 4,
                        "question": "How do you handle events in React?",
                        "quick_answer": "Attach event handlers as props with camelCase names (onClick, onChange). Pass a function reference or arrow function — never invoke the function directly.",
                        "explanation": "React events are synthetic events that wrap native browser events.\n\nKey differences from HTML events:\n1. camelCase names: onClick not onclick\n2. Functions, not strings: onClick={handleClick} not onclick=\"handleClick()\"\n3. Prevent default: call e.preventDefault() in the handler\n\nEvent handler patterns:\n- Named function: onClick={handleClick}\n- Inline arrow: onClick={() => setCount(count + 1)}\n- With arguments: onClick={() => deleteItem(id)}\n\nCommon events: onClick, onChange, onSubmit, onKeyDown, onMouseOver, onFocus",
                        "real_world_example": "A delete button that removes a specific item from a list uses onClick={() => deleteItem(item.id)} — the arrow function captures the item ID at render time.",
                        "code_example": "function EventDemo() {\n  const [text, setText] = useState('');\n  const [submitted, setSubmitted] = useState(false);\n\n  function handleSubmit(e) {\n    e.preventDefault();  // prevent page refresh\n    setSubmitted(true);\n  }\n\n  return (\n    <form onSubmit={handleSubmit}>\n      <input\n        type=\"text\"\n        value={text}\n        onChange={(e) => setText(e.target.value)}\n        placeholder=\"Type something\"\n      />\n      <button type=\"submit\">Submit</button>\n      {submitted && <p>You submitted: {text}</p>}\n    </form>\n  );\n}",
                        "expected_output": "Input field + Submit button\nAfter submitting: 'You submitted: [typed text]'",
                        "flowchart": "User action (click/type)\n         ↓\nSynthetic event created\n         ↓\nEvent handler function called\n         ↓\nState updated\n         ↓\nComponent re-renders",
                        "key_points": "React events use camelCase: onClick, onChange, onSubmit\nPass function references, not function calls\nUse e.preventDefault() to stop default browser behavior\naccessors e.target.value for input values\nArrow functions in JSX are fine for simple handlers",
                        "remember_this": "onClick={handleClick} ← correct. onClick={handleClick()} ← WRONG (calls immediately). Never add () unless you're wrapping in an arrow function."
                    },
                    {
                        "question_number": 5,
                        "question": "How do you manage state for a controlled input?",
                        "quick_answer": "Bind the input's value to state and update state in onChange — making React the single source of truth for the input's value.",
                        "explanation": "A controlled input is one where React controls its value via state.\n\nUncontrolled: The DOM manages the input's value (not React). You read it with a ref.\nControlled: React state is the single source of truth. value={state} + onChange={setter}\n\nWhy controlled inputs are preferred:\n- Instant access to the value at any time\n- Easy validation as the user types\n- Can enforce formatting (e.g., uppercase only)\n- Can conditionally disable submit until valid\n\nPattern: value={stateValue} onChange={(e) => setStateValue(e.target.value)}",
                        "real_world_example": "A search bar with live filtering: as the user types, onChange updates state, the state filters the list, and results update instantly — no form submission needed.",
                        "code_example": "import { useState } from 'react';\n\nfunction RegistrationForm() {\n  const [email, setEmail] = useState('');\n  const [password, setPassword] = useState('');\n\n  const isValid = email.includes('@') && password.length >= 8;\n\n  function handleSubmit(e) {\n    e.preventDefault();\n    if (isValid) {\n      console.log('Submitting:', { email, password });\n    }\n  }\n\n  return (\n    <form onSubmit={handleSubmit}>\n      <input\n        type=\"email\"\n        value={email}\n        onChange={(e) => setEmail(e.target.value)}\n        placeholder=\"Email\"\n      />\n      <input\n        type=\"password\"\n        value={password}\n        onChange={(e) => setPassword(e.target.value)}\n        placeholder=\"Password (min 8 chars)\"\n      />\n      <button type=\"submit\" disabled={!isValid}>\n        Register\n      </button>\n      {!isValid && <p>Enter a valid email and 8+ char password</p>}\n    </form>\n  );\n}",
                        "expected_output": "Form with email and password inputs\nRegister button disabled until valid input\nValidation message shown while invalid",
                        "flowchart": "User types\n      ↓\nonChange fires\n      ↓\nsetEmail(e.target.value)\n      ↓\nState updates\n      ↓\nRe-render with new value\n      ↓\nInput shows new value (from state)",
                        "key_points": "Controlled: value from state, onChange updates state\nReact becomes single source of truth for input value\nEnables real-time validation and formatting\nAlways pair value={} with onChange={}\nDo not omit onChange — input becomes read-only",
                        "remember_this": "Controlled input = value + onChange always together. The input shows whatever state says. onChange updates state. State = truth."
                    },
                ],
            },
        ],
    },
    {
        "lesson_title": "Hooks and Lists",
        "topics": [
            {
                "title": "useEffect Hook",
                "description": "Running side effects in React components: fetching data, subscriptions, and timers.",
                "topic_number": 1,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "What is useEffect and when do you use it?",
                        "quick_answer": "useEffect runs side effects (fetching data, subscriptions, timers) after a component renders. It runs after every render by default, or conditionally based on dependencies.",
                        "explanation": "React components are pure — they take inputs (props/state) and return JSX. But some operations have side effects on the world outside the component:\n\n- Fetching data from an API\n- Setting up subscriptions or event listeners\n- Manually changing the DOM\n- Setting timers\n- Logging\n\nuseEffect runs after the component has rendered to the DOM, making it the right place for these operations.\n\nSyntax: useEffect(() => { /* effect */ }, [dependencies])",
                        "real_world_example": "When a user navigates to their profile page, useEffect triggers an API call to fetch their profile data. The data arrives, state updates, React re-renders with the real data.",
                        "code_example": "import { useState, useEffect } from 'react';\n\nfunction UserProfile({ userId }) {\n  const [user, setUser] = useState(null);\n  const [loading, setLoading] = useState(true);\n\n  useEffect(() => {\n    setLoading(true);\n    fetch(`/api/users/${userId}`)\n      .then(res => res.json())\n      .then(data => {\n        setUser(data);\n        setLoading(false);\n      });\n  }, [userId]); // Re-runs when userId changes\n\n  if (loading) return <p>Loading...</p>;\n  return <h1>{user?.name}</h1>;\n}",
                        "expected_output": "Shows 'Loading...' then displays user name after fetch completes",
                        "flowchart": "Component renders\n       ↓\nBrowser paints DOM\n       ↓\nuseEffect runs\n       ↓\nFetch API called\n       ↓\nData arrives → setState\n       ↓\nRe-render with data",
                        "key_points": "useEffect runs after every render by default\nDependency array [] runs effect only once (on mount)\nDependency array [value] runs when value changes\nNo array runs after every render (rarely needed)\nReturn a cleanup function to prevent memory leaks",
                        "remember_this": "useEffect with [] = componentDidMount. With [dep] = runs when dep changes. Without [] = after every render."
                    },
                    {
                        "question_number": 2,
                        "question": "What is the dependency array in useEffect?",
                        "quick_answer": "The dependency array tells React when to re-run the effect. Empty [] runs once on mount; [value] runs when value changes; no array runs after every render.",
                        "explanation": "The dependency array is the second argument to useEffect:\n\nuseEffect(fn, []) — runs once after first render\nuseEffect(fn, [a, b]) — runs after first render and when a or b changes\nuseEffect(fn) — runs after every render\n\nCommon mistake: not including all values used inside the effect in the dependency array — this causes stale closures where the effect uses outdated values.\n\nRule: anything from the component scope (state, props, functions) that the effect uses should be in the dependency array.",
                        "real_world_example": "A search component fetches results when the query changes. The effect depends on the query state. [query] in the dependency array ensures a new fetch happens every time the user types.",
                        "code_example": "import { useState, useEffect } from 'react';\n\nfunction SearchResults({ query }) {\n  const [results, setResults] = useState([]);\n\n  useEffect(() => {\n    if (!query) { setResults([]); return; }\n\n    // This effect re-runs every time 'query' changes\n    fetch(`/api/search?q=${query}`)\n      .then(res => res.json())\n      .then(data => setResults(data));\n  }, [query]); // <-- dependency array\n\n  return (\n    <ul>\n      {results.map(r => <li key={r.id}>{r.title}</li>)}\n    </ul>\n  );\n}",
                        "expected_output": "Empty list initially. Fetches and displays results as query changes.",
                        "flowchart": "Component mounts\n      ↓\nEffect runs (query = '')\n      ↓\nuser changes query\n      ↓\nEffect re-runs (query = 'react')\n      ↓\nNew results fetched and set",
                        "key_points": "[] = run once after mount\n[dep] = run after mount + when dep changes\nNo array = run after every render\nInclude everything the effect uses in the array\nEslint-plugin-react-hooks warns about missing deps",
                        "remember_this": "The dependency array answers: 'When should this effect re-run?' Match it to the data the effect actually uses."
                    },
                    {
                        "question_number": 3,
                        "question": "How do you clean up in useEffect?",
                        "quick_answer": "Return a cleanup function from useEffect. React runs it before the component unmounts or before the effect re-runs.",
                        "explanation": "Some effects must be cleaned up to prevent memory leaks:\n\n- Event listeners must be removed\n- Timers (setTimeout, setInterval) must be cleared\n- WebSocket connections must be closed\n- Subscriptions must be unsubscribed\n\nCleanup pattern:\nuseEffect(() => {\n  // setup\n  return () => {\n    // cleanup\n  };\n}, [dep]);\n\nReact calls the cleanup:\n1. Before the effect runs again (on the next render that changes deps)\n2. When the component unmounts",
                        "real_world_example": "A real-time clock component uses setInterval. If the cleanup doesn't clear the interval, the interval keeps running even after the clock component is removed from the screen — causing errors and memory leaks.",
                        "code_example": "import { useState, useEffect } from 'react';\n\nfunction Clock() {\n  const [time, setTime] = useState(new Date());\n\n  useEffect(() => {\n    // Set up interval\n    const intervalId = setInterval(() => {\n      setTime(new Date());\n    }, 1000);\n\n    // Cleanup: clears interval when component unmounts\n    return () => clearInterval(intervalId);\n  }, []); // Only runs once\n\n  return <p>{time.toLocaleTimeString()}</p>;\n}",
                        "expected_output": "Time updates every second: 10:30:00 → 10:30:01 → ...\nInterval clears automatically when component unmounts",
                        "flowchart": "useEffect runs → setInterval started\n         ↓\nComponent unmounts OR deps change\n         ↓\nCleanup function runs → clearInterval\n         ↓\n(If re-running: effect sets up new interval)",
                        "key_points": "Return a function from useEffect for cleanup\nCleanup prevents memory leaks and stale effects\nRuns before component unmounts\nRuns before effect re-runs on dep changes\nAlways clean up: event listeners, timers, subscriptions",
                        "remember_this": "If you start something in useEffect (timer, listener, socket), stop it in the cleanup return. If you open a door, close it."
                    },
                    {
                        "question_number": 4,
                        "question": "How do you render a list of items in React?",
                        "quick_answer": "Use the JavaScript .map() method to transform an array into an array of JSX elements. Each element must have a unique key prop.",
                        "explanation": "React can render arrays of JSX elements. The standard pattern is:\n\narray.map(item => <Element key={item.id} {...item} />)\n\nThe key prop:\n- Must be unique among siblings\n- Should be stable (same value across renders)\n- Usually the item's database ID\n- Never use the array index as key if the list can reorder\n\nWhy keys matter: React uses keys to identify which items changed, were added, or removed during re-renders. Wrong keys cause bugs.",
                        "real_world_example": "A todo list app renders all todos with .map(). When a todo is added or removed, React uses the keys to update only the changed items — not re-render the whole list.",
                        "code_example": "function TodoList({ todos }) {\n  return (\n    <ul>\n      {todos.map(todo => (\n        <li\n          key={todo.id}  // unique, stable key\n          style={{\n            textDecoration: todo.done ? 'line-through' : 'none'\n          }}\n        >\n          {todo.text}\n        </li>\n      ))}\n    </ul>\n  );\n}\n\n// Usage:\n<TodoList todos={[\n  { id: 1, text: 'Learn React', done: true },\n  { id: 2, text: 'Build a project', done: false },\n  { id: 3, text: 'Get a job', done: false },\n]} />",
                        "expected_output": "• ~~Learn React~~\n• Build a project\n• Get a job",
                        "flowchart": None,
                        "key_points": ".map() returns an array of JSX — React renders it automatically\nEvery mapped element MUST have a unique key prop\nUse the item's unique ID as the key\nDon't use array index as key (unless list is static and won't reorder)\nMap returns exactly one element per item",
                        "remember_this": "List rendering = .map() + key. Always. If you see a React 'key' warning in the console, you forgot the key prop on a mapped element."
                    },
                    {
                        "question_number": 5,
                        "question": "How do you conditionally render content in React?",
                        "quick_answer": "Use JavaScript's ternary operator (condition ? a : b) or logical AND (condition && element) inside JSX to conditionally show or hide content.",
                        "explanation": "React has no special template syntax for conditionals — it uses regular JavaScript:\n\n1. Ternary operator: condition ? <A /> : <B />\n   - Shows A when true, B when false\n   - Good when both cases have content\n\n2. Logical AND: condition && <A />\n   - Shows A when true, renders nothing when false\n   - Good for 'show this only if'\n\n3. if/else before return:\n   - Good for complex conditions or early returns\n   - Cannot be used inline in JSX\n\n4. Nullish/optional: component ?? <Fallback />",
                        "real_world_example": "A notification bell only shows the unread count badge when unreadCount > 0. Using conditional rendering: {unreadCount > 0 && <span className='badge'>{unreadCount}</span>}",
                        "code_example": "function Dashboard({ user, isLoading, error }) {\n  // Early return for loading\n  if (isLoading) return <Spinner />;\n\n  // Early return for error\n  if (error) return <ErrorMessage message={error} />;\n\n  return (\n    <div>\n      {/* Ternary: show greeting or login prompt */}\n      {user\n        ? <h1>Welcome, {user.name}!</h1>\n        : <p>Please log in.</p>\n      }\n\n      {/* AND: show badge only when needed */}\n      {user?.isAdmin && <AdminBadge />}\n\n      {/* AND: show notification count */}\n      {user?.notifications > 0 && (\n        <span>({user.notifications} notifications)</span>\n      )}\n    </div>\n  );\n}",
                        "expected_output": "Loading state → error state → user dashboard with conditional elements",
                        "flowchart": None,
                        "key_points": "Ternary (? :) for two alternatives\n&& for 'show if true, hide if false'\nif/else before return for complex conditions\nReturning null renders nothing\nAvoid nesting too many ternaries — use if/else for readability",
                        "remember_this": "React conditional rendering = JavaScript in {}. Use ternary for A or B, && for A or nothing, if/else for complex logic outside JSX."
                    },
                ],
            },
        ],
    },
    {
        "lesson_title": "Forms and API Integration",
        "topics": [
            {
                "title": "Fetching Data from APIs",
                "description": "Using fetch and async/await with useEffect to load data from backend APIs.",
                "topic_number": 1,
                "questions": [
                    {
                        "question_number": 1,
                        "question": "How do you fetch data from an API in React?",
                        "quick_answer": "Use useEffect with an async function inside it, call fetch(), await the response, convert to JSON, and store in state.",
                        "explanation": "The standard pattern for fetching data in React:\n\n1. Define state for: data, loading, error\n2. Use useEffect to trigger the fetch after render\n3. Set loading = true before fetching\n4. Fetch data with fetch() or axios\n5. Update state with the data\n6. Set loading = false\n7. Catch errors and set error state\n\nNote: useEffect callbacks cannot be async directly — create an inner async function and call it.",
                        "real_world_example": "A weather app fetches current temperature from a weather API when the page loads. useEffect with [] ensures it only fetches once. Loading state shows a spinner while waiting.",
                        "code_example": "import { useState, useEffect } from 'react';\n\nfunction Posts() {\n  const [posts, setPosts] = useState([]);\n  const [loading, setLoading] = useState(true);\n  const [error, setError] = useState('');\n\n  useEffect(() => {\n    async function fetchPosts() {\n      try {\n        setLoading(true);\n        const response = await fetch(\n          'https://jsonplaceholder.typicode.com/posts?_limit=5'\n        );\n        if (!response.ok) throw new Error('Failed to fetch');\n        const data = await response.json();\n        setPosts(data);\n      } catch (err) {\n        setError(err.message);\n      } finally {\n        setLoading(false);\n      }\n    }\n    fetchPosts();\n  }, []);\n\n  if (loading) return <p>Loading posts...</p>;\n  if (error) return <p>Error: {error}</p>;\n\n  return (\n    <ul>\n      {posts.map(post => (\n        <li key={post.id}>{post.title}</li>\n      ))}\n    </ul>\n  );\n}",
                        "expected_output": "Loading posts...\n(after ~500ms)\n• sunt aut facere...\n• qui est esse\n• ea molestiae...\n• eum et est...\n• nesciunt quas...",
                        "flowchart": "useEffect runs on mount\n       ↓\nsetLoading(true)\n       ↓\nfetch('/api/posts')\n       ↓\nawait response.json()\n       ↓\nsetPosts(data)\n       ↓\nsetLoading(false)\n       ↓\nComponent re-renders with posts",
                        "key_points": "useEffect callback cannot be async — use inner async function\nAlways handle loading and error states\nCheck response.ok before parsing JSON\nUse finally to reset loading whether success or error\nEmpty [] dependency array fetches only on mount",
                        "remember_this": "The pattern: state(data, loading, error) + useEffect(async fetch) + render(loading? or error? or data). This covers 90% of API calls in React."
                    },
                    {
                        "question_number": 2,
                        "question": "How do you send POST data to an API from a React form?",
                        "quick_answer": "In the form's onSubmit handler, call fetch() with method: 'POST', a JSON body, and Content-Type header. Use e.preventDefault() to stop page refresh.",
                        "explanation": "Sending data to a backend from React:\n\n1. Create a controlled form with state for each field\n2. Handle form submission with onSubmit\n3. Call e.preventDefault() to stop browser's default behavior\n4. Build the request body from state\n5. Call fetch() with method 'POST' and JSON body\n6. Handle the response (success or error)\n7. Reset form and update UI",
                        "real_world_example": "A contact form on a website collects name, email, and message. On submit, it POSTs to /api/contact. On success, shows a 'Message sent!' confirmation. On failure, shows an error.",
                        "code_example": "import { useState } from 'react';\n\nfunction CreatePostForm() {\n  const [title, setTitle] = useState('');\n  const [body, setBody] = useState('');\n  const [status, setStatus] = useState('');\n  const [loading, setLoading] = useState(false);\n\n  async function handleSubmit(e) {\n    e.preventDefault();\n    setLoading(true);\n    setStatus('');\n\n    try {\n      const response = await fetch(\n        'https://jsonplaceholder.typicode.com/posts',\n        {\n          method: 'POST',\n          headers: { 'Content-Type': 'application/json' },\n          body: JSON.stringify({ title, body, userId: 1 }),\n        }\n      );\n\n      if (!response.ok) throw new Error('Failed to create post');\n\n      const data = await response.json();\n      setStatus(`Post created with ID: ${data.id}`);\n      setTitle('');\n      setBody('');\n    } catch (err) {\n      setStatus(`Error: ${err.message}`);\n    } finally {\n      setLoading(false);\n    }\n  }\n\n  return (\n    <form onSubmit={handleSubmit}>\n      <input value={title} onChange={e => setTitle(e.target.value)} placeholder=\"Title\" required />\n      <textarea value={body} onChange={e => setBody(e.target.value)} placeholder=\"Body\" required />\n      <button type=\"submit\" disabled={loading}>\n        {loading ? 'Creating...' : 'Create Post'}\n      </button>\n      {status && <p>{status}</p>}\n    </form>\n  );\n}",
                        "expected_output": "Form with title and body inputs\nAfter submit: 'Post created with ID: 101'",
                        "flowchart": "User fills form\n      ↓\nClick Submit\n      ↓\nonSubmit handler runs\n      ↓\ne.preventDefault()\n      ↓\nfetch POST with JSON body\n      ↓\nResponse received\n      ↓\nShow success/error + reset form",
                        "key_points": "Always call e.preventDefault() in onSubmit\nSet Content-Type: application/json header\nJSON.stringify() converts JS object to JSON string\nCheck response.ok before trusting the response\nReset form state after successful submit",
                        "remember_this": "POST from React = fetch() with method:'POST' + headers:{Content-Type:json} + body:JSON.stringify(data). Always prevent default first."
                    },
                    {
                        "question_number": 3,
                        "question": "What is the difference between fetch and axios?",
                        "quick_answer": "fetch is a built-in browser API; axios is a third-party library with more features like automatic JSON parsing, request cancellation, and interceptors.",
                        "explanation": "Both fetch and axios make HTTP requests, but with key differences:\n\nfetch:\n- Built-in to browsers — no installation needed\n- Returns a Response object, requires manual .json() call\n- Does NOT throw errors for 4xx/5xx status codes — must check response.ok\n- More verbose for common tasks\n\naxios:\n- Must install: npm install axios\n- Automatically parses JSON responses\n- Throws errors for 4xx/5xx responses automatically\n- Supports request/response interceptors\n- Easier cancellation\n- Better timeout support\n\nFor most React projects, axios is preferred for cleaner code.",
                        "real_world_example": "A production API client using axios can add the auth token automatically via interceptors — one setup, every request is authenticated. With fetch, you'd manually add the header each time.",
                        "code_example": "// With fetch (more verbose)\nasync function fetchWithFetch() {\n  const response = await fetch('/api/users');\n  if (!response.ok) throw new Error('Failed');\n  const data = await response.json();\n  return data;\n}\n\n// With axios (cleaner)\nimport axios from 'axios';\n\nasync function fetchWithAxios() {\n  // Throws automatically for 4xx/5xx\n  // Returns data directly (no .json() needed)\n  const { data } = await axios.get('/api/users');\n  return data;\n}\n\n// Axios with auth interceptor\naxios.interceptors.request.use(config => {\n  config.headers.Authorization = `Bearer ${localStorage.getItem('token')}`;\n  return config;\n});",
                        "expected_output": "Both return the same user data, but axios requires less boilerplate",
                        "flowchart": None,
                        "key_points": "fetch is built-in; axios needs npm install\naxios auto-parses JSON; fetch requires .json()\naxios throws on error status; fetch requires response.ok check\naxios supports interceptors for auth tokens\nFor simple projects fetch is fine; for large projects use axios",
                        "remember_this": "fetch = bare metal API. axios = fetch with superpowers. For production apps, axios saves time and reduces bugs."
                    },
                    {
                        "question_number": 4,
                        "question": "How do you handle loading and error states when fetching?",
                        "quick_answer": "Declare separate loading and error state variables. Show a spinner when loading is true and an error message when error is not empty.",
                        "explanation": "Every API call has three possible states:\n1. Loading: waiting for the response\n2. Success: data received\n3. Error: something went wrong\n\nBest practices:\n- Show a loading indicator (spinner, skeleton, 'Loading...') while fetching\n- Show a meaningful error message if the request fails\n- Always use try/catch/finally — finally resets loading state\n- Optionally add a retry button\n- Consider empty state: when API returns data but it's an empty array",
                        "real_world_example": "YouTube shows a loading skeleton (gray boxes where content will be) while video thumbnails load. This is a sophisticated loading state that avoids layout shift.",
                        "code_example": "import { useState, useEffect } from 'react';\n\nfunction UserList() {\n  const [users, setUsers] = useState([]);\n  const [loading, setLoading] = useState(true);\n  const [error, setError] = useState('');\n\n  const fetchUsers = async () => {\n    try {\n      setLoading(true);\n      setError('');\n      const res = await fetch('/api/users');\n      if (!res.ok) throw new Error(`HTTP ${res.status}`);\n      const data = await res.json();\n      setUsers(data);\n    } catch (err) {\n      setError(err.message);\n    } finally {\n      setLoading(false);\n    }\n  };\n\n  useEffect(() => { fetchUsers(); }, []);\n\n  // Loading state\n  if (loading) return <div className=\"spinner\">Loading...</div>;\n\n  // Error state\n  if (error) return (\n    <div>\n      <p>Error: {error}</p>\n      <button onClick={fetchUsers}>Try Again</button>\n    </div>\n  );\n\n  // Empty state\n  if (users.length === 0) return <p>No users found.</p>;\n\n  // Success state\n  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;\n}",
                        "expected_output": "Loading... → (success) user list OR (error) error message + retry button",
                        "flowchart": "Fetch starts\n    ↓\nloading=true → show spinner\n    ↓\nFetch completes\n    ↙          ↘\nSuccess        Error\n  ↓              ↓\nsetUsers      setError\nloading=false  loading=false\n  ↓              ↓\nRender list   Render error+retry",
                        "key_points": "Always track loading AND error separately\nUse finally to ensure loading always resets\nShow meaningful error messages, not just 'Error'\nAdd retry buttons for recoverable errors\nHandle the empty data case too",
                        "remember_this": "Three states: loading, error, data. Handle all three. Users should never stare at a blank screen wondering what happened."
                    },
                    {
                        "question_number": 5,
                        "question": "How do you pass authentication tokens in API requests from React?",
                        "quick_answer": "Read the token from localStorage and add it as an Authorization: Bearer {token} header in your fetch or axios request.",
                        "explanation": "Most APIs require authentication via JWT (JSON Web Token) or API keys.\n\nFor JWT auth in React:\n1. After login, store the token in localStorage\n2. On every API request, read the token and add it to the Authorization header\n3. If the token expires, redirect to login\n\nSecurity note:\n- localStorage is accessible by JavaScript (XSS risk) but simple to use\n- httpOnly cookies are more secure but require backend configuration\n- For most React SPA projects, localStorage + HTTPS is acceptable",
                        "real_world_example": "After logging into CodeSphere, your JWT token is stored in localStorage. Every API call (get courses, save progress) automatically includes this token in the Authorization header so the backend knows who you are.",
                        "code_example": "// Helper function — used across the app\nfunction getAuthToken() {\n  return localStorage.getItem('access_token');\n}\n\n// Authenticated fetch\nasync function apiFetch(endpoint, options = {}) {\n  const token = getAuthToken();\n\n  const headers = {\n    'Content-Type': 'application/json',\n    ...(options.headers || {}),\n  };\n\n  if (token) {\n    headers.Authorization = `Bearer ${token}`;\n  }\n\n  const response = await fetch(\n    `http://localhost:8000${endpoint}`,\n    { ...options, headers }\n  );\n\n  if (response.status === 401) {\n    // Token expired — redirect to login\n    localStorage.removeItem('access_token');\n    window.location.href = '/login';\n    return;\n  }\n\n  if (!response.ok) throw new Error('Request failed');\n\n  return response.json();\n}\n\n// Usage:\nconst courses = await apiFetch('/learning/courses');\nconst progress = await apiFetch('/progress', {\n  method: 'POST',\n  body: JSON.stringify({ lesson_id: 1, completion_percentage: 100 })\n});",
                        "expected_output": "Authenticated requests succeed\n401 responses automatically redirect to login",
                        "flowchart": "API call needed\n       ↓\nRead token from localStorage\n       ↓\nAdd Authorization header\n       ↓\nSend request\n       ↓\n401? → clear token → redirect to /login\nOK? → return data",
                        "key_points": "Store JWT in localStorage after login\nAdd Authorization: Bearer {token} header to requests\nCreate a shared apiRequest() helper function\nHandle 401 responses by clearing token and redirecting\nUse HTTPS in production to protect the token",
                        "remember_this": "Authentication header = Authorization: Bearer {token}. Build a shared fetch wrapper once, use it everywhere. Never repeat the auth logic in every component."
                    },
                ],
            },
        ],
    },
]


# ======================================================
# SEED FUNCTION
# ======================================================

def seed():
    db = SessionLocal()

    try:
        print("=" * 60)
        print("CodeSphere LMS Seed Script")
        print("=" * 60)

        # ---- Find or validate the course ----
        course = db.query(Course).filter(
            Course.title == COURSE_TITLE
        ).first()

        if course is None:
            print(f"\n[!] Course '{COURSE_TITLE}' not found in database.")
            print("Please create it first via the admin panel, then re-run this script.")
            print("Expected course title (exact match):", COURSE_TITLE)
            return

        print(f"\n[OK] Found course: '{course.title}' (ID: {course.id})")

        # ---- Process each lesson ----
        for lesson_order, lesson_data in enumerate(SEED_DATA, start=1):
            original_title = lesson_data["lesson_title"]
            lesson_title = LESSON_TITLE_MAP.get(original_title, original_title)

            # Try exact match first, then case-insensitive
            lesson = db.query(Lesson).filter(
                Lesson.course_id == course.id,
                Lesson.title == lesson_title
            ).first()

            if lesson is None:
                # Try case-insensitive match
                all_lessons = db.query(Lesson).filter(
                    Lesson.course_id == course.id
                ).all()
                for l in all_lessons:
                    if l.title.strip().upper() == lesson_title.strip().upper():
                        lesson = l
                        break

            if lesson is None:
                # Auto-create the lesson
                lesson = Lesson(
                    course_id=course.id,
                    title=lesson_title,
                    notes=f"Auto-created by seed script for: {original_title}",
                    important_concepts="",
                    youtube_url=None,
                    lesson_order=lesson_order
                )
                db.add(lesson)
                db.flush()
                print(f"\n  [+] Created lesson: '{lesson_title}' (ID: {lesson.id})")
            else:
                print(f"\n  [found] Lesson: '{lesson.title}' (ID: {lesson.id})")

            # ---- Process each topic ----
            for topic_data in lesson_data["topics"]:
                topic_title = topic_data["title"]

                # Check for existing topic (idempotent)
                existing_topic = db.query(Topic).filter(
                    Topic.lesson_id == lesson.id,
                    Topic.title == topic_title
                ).first()

                if existing_topic:
                    print(f"    [exists] Topic '{topic_title}' already exists -- skipping")
                    topic = existing_topic
                else:
                    topic = Topic(
                        lesson_id=lesson.id,
                        title=topic_title,
                        description=topic_data.get("description"),
                        topic_number=topic_data["topic_number"]
                    )
                    db.add(topic)
                    db.flush()  # Get ID without committing
                    print(f"    [+] Created topic: '{topic_title}'")

                # ---- Process each question ----
                for q_data in topic_data["questions"]:
                    q_text = q_data["question"]

                    existing_q = db.query(Question).filter(
                        Question.topic_id == topic.id,
                        Question.question == q_text
                    ).first()

                    if existing_q:
                        print(f"       [exists] Q{q_data['question_number']}: already exists -- skipping")
                    else:
                        q = Question(
                            topic_id=topic.id,
                            question=q_text,
                            quick_answer=q_data.get("quick_answer"),
                            explanation=q_data.get("explanation"),
                            real_world_example=q_data.get("real_world_example"),
                            code_example=q_data.get("code_example"),
                            expected_output=q_data.get("expected_output"),
                            flowchart=q_data.get("flowchart"),
                            key_points=q_data.get("key_points"),
                            remember_this=q_data.get("remember_this"),
                            question_number=q_data["question_number"]
                        )
                        db.add(q)
                        print(f"       [+] Q{q_data['question_number']}: '{q_text[:60]}...'")

        db.commit()
        print("\n" + "=" * 60)
        print("[OK] Seed complete! All topics and questions saved.")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n[FAILED] Seed failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
