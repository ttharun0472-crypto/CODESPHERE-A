"""Safely create or complete the SQL Programming course.

Run from the backend directory with the configured project environment:
    python seed_sql_course.py

The script only creates the target course and its missing lessons. It never
deletes records or changes progress data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config.database import SessionLocal
from app.models import Course, Lesson


COURSE_TITLE = "SQL Programming"
COURSE_DESCRIPTION = (
    "Learn SQL from the fundamentals to practical database operations, "
    "including queries, filtering, joins, aggregate functions, and data "
    "modification."
)

LESSONS = [
    {
        "title": "Introduction to SQL and Databases",
        "important_concepts": (
            "Database; relational database; tables, rows, columns; "
            "primary and foreign keys; PostgreSQL; CREATE TABLE; INSERT; SELECT"
        ),
        "notes": r"""LESSON 1: INTRODUCTION TO SQL AND DATABASES

LEARNING OBJECTIVES

By the end of this lesson, you can:
- Explain what a database, relational database, and SQL are.
- Identify tables, rows, columns, primary keys, and foreign keys.
- Describe PostgreSQL's role as a relational database management system.
- Create a database and table with suitable PostgreSQL data types.
- Insert sample rows and retrieve them with SELECT.

INTRODUCTION

Most applications need to store information after a browser is closed: student profiles, course catalogs, enrollments, and marks are examples. A database organizes that information so it can be stored, searched, updated, and protected. SQL is the language commonly used to define and work with relational databases. We will use one small school example throughout the course.

1. WHAT IS A DATABASE?

A database is an organized collection of data. A database management system (DBMS) is software that stores and manages databases. A DBMS helps applications safely create, read, update, and delete information; supports multiple users; and can enforce rules such as unique identifiers.

Examples of database systems include PostgreSQL, MySQL, SQLite, and Microsoft SQL Server. They share many SQL ideas but are separate products and do not support every feature in exactly the same way.

2. WHAT IS SQL?

SQL means Structured Query Language. It is used to define database structures and work with stored data. Common categories include:

- Data definition: CREATE TABLE, ALTER TABLE.
- Data manipulation: INSERT, UPDATE, DELETE.
- Data querying: SELECT.
- Transaction control: COMMIT, ROLLBACK.

SQL statements usually end with a semicolon. SQL keywords are conventionally written uppercase for readability, but PostgreSQL accepts keywords in either case. Text values use single quotes, for example 'Asha'. Identifiers such as table and column names are not quoted in ordinary examples.

3. RELATIONAL DATABASES: TABLES, ROWS, AND COLUMNS

A relational database organizes related data into tables. A table has columns (named attributes) and rows (individual records). In a Students table:

student_id | name | email | joined_on
-----------+------+-------+----------
1          | Asha | asha@example.test | 2026-01-10

The student_id, name, email, and joined_on are columns. The record for Asha is a row. Each row should describe one student, and each column should contain one kind of value.

Related tables connect through keys. A primary key identifies one row uniquely. A foreign key points to a row in another table. For example, an Enrollments table can store student_id to identify the student and course_id to identify the course. These references help prevent enrollments that refer to nonexistent students or courses.

4. INTRODUCTION TO POSTGRESQL

PostgreSQL (often called Postgres) is an open-source object-relational database system. It implements standard SQL features and offers additional capabilities, including rich data types and transaction support. A PostgreSQL server can host multiple databases; a client such as psql, a graphical database tool, or an application connects to a database on that server.

The following commands are for the psql command-line client, not SQL statements sent inside an ordinary query:

createdb school_db
psql school_db

createdb creates a database using the local PostgreSQL tools and permissions. psql connects to it. On a hosted server, create the database with the provider's approved administration process instead. Do not put database passwords into lesson code or source files.

5. CREATING A TABLE AND CHOOSING DATA TYPES

PostgreSQL data types describe the values a column can store. Common beginner types include:

- INTEGER: whole numbers such as student IDs.
- BIGINT: larger whole numbers.
- VARCHAR(n): text with a maximum length n.
- TEXT: text without a declared length limit.
- BOOLEAN: TRUE or FALSE.
- DATE: a calendar date.
- TIMESTAMP: date and time.
- NUMERIC(8, 2): exact decimal values, useful for amounts or marks that require decimal precision.

Use a type that represents the meaning of the data. A mark such as 87.50 is better represented as NUMERIC than as text. A name is text, not an integer.

CREATE TABLE students (
    student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    joined_on DATE NOT NULL DEFAULT CURRENT_DATE
);

STEP-BY-STEP

1. CREATE TABLE students defines a new table named students.
2. student_id is an integer generated by PostgreSQL for each new row. IDENTITY is PostgreSQL's modern standard-style auto-numbering feature.
3. PRIMARY KEY makes student_id unique and non-null, and designates it as the row identifier.
4. name and email are required because they use NOT NULL.
5. UNIQUE prevents two rows from using the same email.
6. joined_on stores a date. DEFAULT CURRENT_DATE supplies today's date when an INSERT omits the column.

6. INSERTING DATA

Specify the columns you intend to fill, then provide one value for each listed column:

INSERT INTO students (name, email, joined_on)
VALUES ('Asha Rao', 'asha@example.test', DATE '2026-01-10');

INSERT INTO students (name, email, joined_on)
VALUES
    ('Ben Lee', 'ben@example.test', DATE '2026-01-12'),
    ('Chitra Das', 'chitra@example.test', DATE '2026-01-15');

The first statement inserts one row. The second inserts two rows in one statement. PostgreSQL generates student_id values because the INSERT does not supply that identity column. Use fictional .test addresses in practice examples; they are not real contacts.

7. SELECTING DATA

SELECT student_id, name, email, joined_on
FROM students;

This query returns the listed columns for every row in students. If the table has the three sample rows above, the result has three rows; each generated student_id is assigned by the database and is not predictable in a shared database.

SELECT * FROM students;

The asterisk means all columns. It is useful for a quick exploration, but applications should normally name the columns they need so the query is clear and less sensitive to later schema changes.

8. PRACTICAL COMPLETE EXAMPLE

Run the following in an empty practice database. If a table already exists, PostgreSQL reports that it exists; this course avoids DROP TABLE so you do not accidentally destroy data.

CREATE TABLE courses (
    course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE enrollments (
    enrollment_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    enrolled_on DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (student_id, course_id)
);

INSERT INTO courses (title)
VALUES ('SQL Fundamentals'), ('Web Development');

INSERT INTO enrollments (student_id, course_id)
VALUES (1, 1);

The REFERENCES clauses create foreign-key constraints. The enrollment refers to an existing student and course. If the actual generated IDs are different from 1, query those IDs first and use the returned values; generated identity values must not be guessed.

To inspect the rows:

SELECT student_id, name
FROM students
ORDER BY student_id;

SELECT course_id, title
FROM courses
ORDER BY course_id;

Expected: the first query lists each inserted student in ID order; the second lists SQL Fundamentals and Web Development. The exact IDs depend on the database's identity sequence.

COMMON MISTAKES

- Forgetting single quotes around text values.
- Using double quotes for a text value; PostgreSQL uses double quotes for case-sensitive identifiers, not strings.
- Supplying values in the wrong order. Explicitly list INSERT columns to make the mapping clear.
- Storing multiple unrelated values in one column instead of modeling related records.
- Forgetting NOT NULL or key constraints when the data has required rules.
- Assuming a generated ID will always start at 1.
- Running destructive commands such as DROP TABLE on a database that contains data.

IMPORTANT CONCEPTS

- A database stores organized information; a DBMS manages it.
- SQL defines structures and queries or modifies relational data.
- A row is a record; a column describes one attribute.
- A primary key uniquely identifies a row.
- A foreign key refers to a key in another table.
- PostgreSQL is the database system used for this course; SQL details can vary between database products.

LESSON SUMMARY

You learned the purpose of databases and SQL, how relational tables organize rows and columns, and how primary and foreign keys relate records. You used PostgreSQL data types and CREATE TABLE to define students, then inserted and selected sample rows. In the next lesson, you will narrow and sort query results."""
    },
    {
        "title": "SELECT Queries and Filtering Data",
        "important_concepts": (
            "SELECT; DISTINCT; WHERE; comparison operators; AND/OR/NOT; "
            "BETWEEN; IN; LIKE; NULL; ORDER BY; LIMIT"
        ),
        "notes": r"""LESSON 2: SELECT QUERIES AND FILTERING DATA

LEARNING OBJECTIVES

By the end of this lesson, you can select chosen columns, remove duplicate result values, filter rows using comparisons and logical operators, match patterns, handle NULL correctly, sort results, and limit the number of returned rows.

INTRODUCTION AND SAMPLE TABLE

Queries let us ask useful questions without changing stored records. We will use this PostgreSQL table:

CREATE TABLE students (
    student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(80),
    age INTEGER,
    joined_on DATE NOT NULL DEFAULT CURRENT_DATE
);

Practice rows:

INSERT INTO students (name, email, city, age, joined_on)
VALUES
    ('Asha Rao', 'asha@example.test', 'Pune', 20, DATE '2026-01-10'),
    ('Ben Lee', 'ben@example.test', 'Delhi', 22, DATE '2026-01-12'),
    ('Chitra Das', 'chitra@example.test', 'Pune', 19, DATE '2026-01-15'),
    ('Dev Shah', 'dev@example.test', NULL, 21, DATE '2026-02-01'),
    ('Esha Khan', 'esha@example.test', 'Delhi', 22, DATE '2026-02-04');

The identity column supplies student_id values; the examples below use names to make the expected records easy to recognize. If you re-run this sample insert, unique email constraints prevent duplicate rows.

1. SELECT AND CHOOSING COLUMNS

SELECT * FROM students;

This returns every column and row. For a readable result, request only needed columns:

SELECT name, city
FROM students;

Expected: five rows with each student's name and city. Dev's city appears as NULL because it is unknown or missing. SELECT does not change the table.

2. SELECT DISTINCT

SELECT DISTINCT city
FROM students
ORDER BY city;

DISTINCT removes duplicate result rows. The non-NULL values are Delhi and Pune; because SQL treats NULL as one distinct result value, a NULL row also appears. PostgreSQL's default ascending NULL placement is NULLS LAST.

DISTINCT applies to the selected combination of columns. For example, SELECT DISTINCT city, age considers each city-and-age pair, not each city alone.

3. WHERE AND COMPARISON OPERATORS

WHERE keeps only rows whose condition is true. Common comparison operators are =, <>, !=, <, <=, >, and >=. In SQL, comparisons with NULL are not true or false; use IS NULL instead.

SELECT name, age
FROM students
WHERE age >= 21;

Expected: Ben Lee (22), Dev Shah (21), and Esha Khan (22).

SELECT name
FROM students
WHERE city <> 'Pune';

This returns Delhi residents only. Dev's NULL city is not included: city <> 'Pune' evaluates to unknown for NULL, and WHERE keeps only true conditions. Add an IS NULL condition if unknown cities should also be included.

4. AND, OR, AND NOT

SELECT name, city, age
FROM students
WHERE city = 'Pune' AND age >= 20;

Expected: Asha Rao only. Both conditions must be true.

SELECT name
FROM students
WHERE city = 'Pune' OR age = 22;

Expected: Asha, Chitra, Ben, and Esha. At least one condition must be true. Use parentheses when combining AND and OR so the intended logic is explicit:

SELECT name
FROM students
WHERE (city = 'Pune' OR city = 'Delhi') AND age >= 20;

NOT reverses a condition:

SELECT name
FROM students
WHERE NOT (age < 20);

This includes ages 20 and above. A row whose age is NULL would not pass this condition because NOT of unknown remains unknown.

5. BETWEEN AND IN

BETWEEN includes both endpoints:

SELECT name, age
FROM students
WHERE age BETWEEN 20 AND 22
ORDER BY age, name;

Expected: Asha (20), Dev (21), Ben (22), Esha (22), sorted by age then name.

IN tests whether a value matches any item in a list:

SELECT name, city
FROM students
WHERE city IN ('Pune', 'Delhi')
ORDER BY city, name;

Expected: four named students in Pune or Delhi; Dev is excluded because city is NULL. IN is often clearer than repeating many OR comparisons.

6. LIKE AND PATTERN MATCHING

In PostgreSQL, LIKE matches a text pattern. % matches zero or more characters; _ matches exactly one character. LIKE is case-sensitive in PostgreSQL. ILIKE is a PostgreSQL extension for case-insensitive matching.

SELECT name
FROM students
WHERE name LIKE 'A%';

Expected: Asha Rao, because the name starts with A.

SELECT name
FROM students
WHERE email ILIKE '%EXAMPLE.TEST';

Expected: all five sample students; ILIKE ignores case. For user-provided patterns, remember that % and _ are wildcards and may need escaping when the intent is literal matching.

7. IS NULL AND IS NOT NULL

NULL represents missing or unknown data; it is not the same as 0 or an empty string. Test it with IS NULL or IS NOT NULL:

SELECT name
FROM students
WHERE city IS NULL;

Expected: Dev Shah.

SELECT name
FROM students
WHERE city IS NOT NULL;

Expected: Asha, Ben, Chitra, and Esha. Do not write city = NULL; that comparison is not true for NULL values.

8. ORDER BY AND LIMIT

SELECT name, age
FROM students
ORDER BY age DESC, name ASC;

DESC sorts from largest to smallest; ASC sorts from smallest to largest and is the default. Multiple columns break ties. PostgreSQL allows explicit NULL placement with NULLS FIRST or NULLS LAST.

To return the two oldest students:

SELECT name, age
FROM students
ORDER BY age DESC, name ASC
LIMIT 2;

Expected: Ben Lee (22) and Esha Khan (22), ordered by name among the tied ages. Without ORDER BY, row order is not guaranteed, so LIMIT alone does not identify predictable rows.

9. COMPLETE PRACTICE QUERY

Find the first three students aged 20 or older who live in Delhi or Pune:

SELECT student_id, name, city, age
FROM students
WHERE age >= 20
  AND city IN ('Delhi', 'Pune')
ORDER BY age DESC, name
LIMIT 3;

Step by step:
1. FROM chooses the students table.
2. WHERE removes rows under age 20 and rows whose city is not Delhi or Pune.
3. ORDER BY sorts age descending, then name ascending.
4. LIMIT returns at most three of the sorted rows.
Expected sample names: Ben Lee, Esha Khan, then Asha Rao.

COMMON MISTAKES

- Using = NULL instead of IS NULL.
- Forgetting SQL's three-valued logic: a comparison involving NULL is unknown.
- Forgetting that BETWEEN includes its endpoints.
- Assuming LIKE ignores case; PostgreSQL ILIKE is case-insensitive.
- Writing OR and AND combinations without parentheses when precedence is unclear.
- Using LIMIT without ORDER BY and expecting a stable result.
- Confusing DISTINCT over multiple selected columns with distinct values from one column.
- Using quotation marks incorrectly: text literals use single quotes.

IMPORTANT CONCEPTS

- SELECT chooses columns; WHERE filters rows.
- DISTINCT removes duplicate result combinations.
- AND requires all conditions, OR requires at least one, NOT negates a condition.
- BETWEEN is inclusive; IN checks membership in a list.
- LIKE uses % and _ wildcards; ILIKE is PostgreSQL-specific case-insensitive matching.
- NULL needs IS NULL/IS NOT NULL tests.
- ORDER BY defines result order; LIMIT is most useful with an explicit order.

LESSON SUMMARY

You queried a sample Students table with SELECT, DISTINCT, and WHERE. You practiced comparisons, logical operators, ranges, lists, patterns, NULL checks, sorting, and limiting. Combine these clauses in a readable order and always add a deterministic ORDER BY when the result order matters."""
    },
    {
        "title": "SQL Functions and Grouping",
        "important_concepts": (
            "COUNT; SUM; AVG; MIN; MAX; GROUP BY; HAVING; WHERE; aliases; "
            "PostgreSQL string, numeric, and date functions"
        ),
        "notes": r"""LESSON 3: SQL FUNCTIONS AND GROUPING

LEARNING OBJECTIVES

By the end of this lesson, you can summarize rows with aggregate functions, group results, filter groups with HAVING, name output columns with aliases, and use basic PostgreSQL string, numeric, and date functions.

INTRODUCTION AND SAMPLE DATA

Aggregate queries answer questions such as “How many students are in each course?” or “What is the average mark?” We will use these tables and sample rows:

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(80)
);

CREATE TABLE marks (
    mark_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id),
    subject VARCHAR(80) NOT NULL,
    score NUMERIC(5, 2) NOT NULL CHECK (score BETWEEN 0 AND 100),
    taken_on DATE NOT NULL
);

INSERT INTO students (student_id, name, city) VALUES
    (1, 'Asha Rao', 'Pune'),
    (2, 'Ben Lee', 'Delhi'),
    (3, 'Chitra Das', 'Pune');

INSERT INTO marks (student_id, subject, score, taken_on) VALUES
    (1, 'SQL', 90, DATE '2026-02-10'),
    (1, 'Python', 80, DATE '2026-02-12'),
    (2, 'SQL', 70, DATE '2026-02-10'),
    (3, 'SQL', 100, DATE '2026-02-15'),
    (3, 'Python', 90, DATE '2026-02-16');

1. AGGREGATE FUNCTIONS

An aggregate function calculates one value from a set of input rows:

- COUNT(*) counts rows.
- COUNT(column) counts rows where that column is not NULL.
- SUM(column) adds numeric values.
- AVG(column) calculates the arithmetic mean of non-NULL numeric values.
- MIN(column) and MAX(column) return the smallest and largest non-NULL values.

SELECT
    COUNT(*) AS mark_count,
    SUM(score) AS total_points,
    ROUND(AVG(score), 2) AS average_score,
    MIN(score) AS lowest_score,
    MAX(score) AS highest_score
FROM marks;

Expected: mark_count 5, total_points 430, average_score 86.00, lowest_score 70, highest_score 100.

COUNT(*) counts every row. COUNT(score) would count only rows with a non-NULL score. Most PostgreSQL aggregates ignore NULL input values; when no input values exist, aggregates such as SUM and AVG return NULL (COUNT returns zero).

2. GROUP BY

GROUP BY partitions rows into groups with matching values and computes aggregates for each group:

SELECT subject, COUNT(*) AS attempts, ROUND(AVG(score), 1) AS average_score
FROM marks
GROUP BY subject
ORDER BY subject;

Expected:

subject | attempts | average_score
Python  | 2        | 85.0
SQL     | 3        | 86.7

The query makes one group per subject. Each output row describes one group. When using GROUP BY, every selected expression must either be grouped or aggregated (PostgreSQL also recognizes certain functional dependencies, but grouping selected non-aggregated values explicitly is clearest for beginners).

3. WHERE VERSUS HAVING

WHERE filters individual rows before grouping. HAVING filters groups after aggregation.

SELECT subject, COUNT(*) AS attempts, AVG(score) AS average_score
FROM marks
WHERE taken_on >= DATE '2026-02-11'
GROUP BY subject
HAVING AVG(score) >= 85
ORDER BY subject;

Step-by-step:
1. WHERE removes the SQL mark on February 10 and both earlier rows before aggregation.
2. GROUP BY makes a group for each remaining subject.
3. HAVING keeps only groups whose average is at least 85.
4. ORDER BY sorts the surviving groups.
Expected: Python, attempts 2, average 85.0; SQL, attempts 1, average 100.0.

Do not use WHERE AVG(score) >= 85: aggregate results do not exist at the row-filtering stage. Use HAVING for conditions involving aggregate values. Use WHERE for conditions on the original rows.

4. ALIASES USING AS

An alias provides a readable label for an output column or a short name for a table:

SELECT student_id AS learner_id, score AS points
FROM marks;

AS is optional in many SQL alias contexts, but including it makes the meaning explicit. A column alias is useful for reports and API result labels. An alias normally lasts only for this query; it does not rename the stored column.

5. AGGREGATES PER STUDENT

SELECT s.student_id, s.name,
       COUNT(m.mark_id) AS subjects_taken,
       ROUND(AVG(m.score), 2) AS average_score
FROM students AS s
LEFT JOIN marks AS m ON m.student_id = s.student_id
GROUP BY s.student_id, s.name
ORDER BY s.student_id;

Expected: Asha has 2 attempts and average 85; Ben has 1 and average 70; Chitra has 2 and average 95. LEFT JOIN keeps a student even if no mark exists. COUNT(m.mark_id), rather than COUNT(*), returns zero for a student with no matching mark because the joined mark_id is NULL.

6. STRING FUNCTIONS

PostgreSQL provides functions and operators for strings. Examples:

SELECT
    UPPER(name) AS uppercase_name,
    LOWER(city) AS lowercase_city,
    LENGTH(name) AS name_characters,
    TRIM(name) AS trimmed_name,
    CONCAT(name, ' - ', city) AS label
FROM students;

UPPER/LOWER change case, LENGTH returns a character count, TRIM removes surrounding whitespace, and CONCAT joins values. PostgreSQL's CONCAT treats NULL arguments as empty strings. String behavior and available functions can differ by database product.

To replace a substring in PostgreSQL:

SELECT REPLACE('SQL for students', 'students', 'learners') AS message;

Expected: SQL for learners.

7. NUMERIC FUNCTIONS

SELECT
    ROUND(AVG(score), 1) AS rounded_average,
    CEIL(AVG(score)) AS average_rounded_up,
    FLOOR(AVG(score)) AS average_rounded_down,
    ABS(-12.5) AS positive_amount
FROM marks;

ROUND rounds a numeric value, CEIL rounds upward to the next integer, FLOOR rounds downward, and ABS returns a non-negative magnitude. PostgreSQL supports overloads and numeric behavior depending on input type; use NUMERIC for exact decimal calculations where appropriate.

8. POSTGRESQL DATE AND TIME FUNCTIONS

SELECT
    CURRENT_DATE AS today,
    CURRENT_TIMESTAMP AS current_time,
    AGE(DATE '2026-03-01', DATE '2026-02-01') AS elapsed_interval,
    EXTRACT(MONTH FROM DATE '2026-02-10') AS month_number,
    DATE_TRUNC('month', DATE '2026-02-10') AS month_start;

CURRENT_DATE and CURRENT_TIMESTAMP return the current date and timestamp for the transaction context. AGE returns an interval, EXTRACT retrieves a date/time field, and DATE_TRUNC truncates a timestamp or date to a named precision. PostgreSQL-specific functions such as AGE and DATE_TRUNC are not guaranteed to exist with the same syntax in every database.

Find the number of marks recorded per calendar month:

SELECT DATE_TRUNC('month', taken_on)::date AS month_start,
       COUNT(*) AS mark_count
FROM marks
GROUP BY DATE_TRUNC('month', taken_on)::date
ORDER BY month_start;

The cast ::date is PostgreSQL syntax and converts the month-start timestamp to a date for display.

PRACTICE

1. Find the highest and lowest score for each subject.
2. Count distinct students with a mark in each subject using COUNT(DISTINCT student_id).
3. Show only subjects with at least two attempts using HAVING COUNT(*) >= 2.
4. Join students to marks and calculate average score per city. Decide whether students with no marks should appear and choose INNER or LEFT JOIN accordingly.

COMMON MISTAKES

- Selecting a non-aggregated column that is neither grouped nor functionally determined.
- Putting an aggregate condition in WHERE instead of HAVING.
- Confusing COUNT(*) (rows) with COUNT(column) (non-NULL values).
- Expecting AVG or SUM to count NULL as zero; NULL inputs are generally ignored.
- Using an aggregate alias in HAVING in a way unsupported by the SQL expression's evaluation rules; repeat the aggregate expression for portability.
- Assuming PostgreSQL-specific functions work identically in other systems.

IMPORTANT CONCEPTS

- Aggregates summarize multiple input rows.
- GROUP BY creates a result group for each distinct grouping value.
- WHERE filters source rows; HAVING filters aggregated groups.
- Aliases improve output readability but do not change stored schema.
- String, numeric, and date functions transform values; exact function support can vary by database.
- Use meaningful sample data and inspect results to confirm grouping behavior.

LESSON SUMMARY

You learned COUNT, SUM, AVG, MIN, and MAX, then grouped marks by subject and student. You distinguished row filtering with WHERE from group filtering with HAVING, named outputs with AS, and practiced PostgreSQL string, numeric, and date functions. Next, you will combine related tables with joins."""
    },
    {
        "title": "Joins and Relationships",
        "important_concepts": (
            "Primary/foreign keys; INNER, LEFT, RIGHT, FULL OUTER, CROSS, "
            "and self joins; aliases; multi-table joins"
        ),
        "notes": r"""LESSON 4: JOINS AND RELATIONSHIPS

LEARNING OBJECTIVES

By the end of this lesson, you can explain why tables are related by keys, choose a join based on which rows must be retained, join multiple tables, use aliases, and recognize a self join.

INTRODUCTION: WHY JOINS?

Relational databases avoid repeating the same course or student details in every enrollment row. Instead, students, courses, and enrollments are stored separately. A JOIN combines related rows when a query needs information from more than one table.

SAMPLE TABLES

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY,
    title VARCHAR(120) NOT NULL
);

CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id)
);

INSERT INTO students (student_id, name) VALUES
    (1, 'Asha'), (2, 'Ben'), (3, 'Chitra');

INSERT INTO courses (course_id, title) VALUES
    (10, 'SQL'), (20, 'React'), (30, 'Python');

INSERT INTO enrollments (enrollment_id, student_id, course_id) VALUES
    (100, 1, 10), (101, 1, 20), (102, 2, 10);

Asha is enrolled in SQL and React, Ben is enrolled in SQL, and Chitra has no enrollment. Python has no enrollment.

1. PRIMARY KEYS, FOREIGN KEYS, AND JOIN CONDITIONS

student_id is the primary key of students; course_id is the primary key of courses. enrollments.student_id and enrollments.course_id are foreign keys. A join condition matches a foreign key to its referenced primary key:

SELECT s.name, c.title
FROM enrollments AS e
JOIN students AS s ON s.student_id = e.student_id
JOIN courses AS c ON c.course_id = e.course_id
ORDER BY s.name, c.title;

Expected rows:

Asha | React
Asha | SQL
Ben  | SQL

Read from enrollments, then match each row to its student and course. Because these are INNER JOINs, only rows with matching records on both sides appear.

2. INNER JOIN

INNER JOIN returns only rows that satisfy the join condition on both sides:

SELECT s.name, c.title
FROM students AS s
INNER JOIN enrollments AS e ON e.student_id = s.student_id
INNER JOIN courses AS c ON c.course_id = e.course_id;

The keyword INNER is optional; JOIN means INNER JOIN by default. Chitra is absent because there is no enrollment row for her.

3. LEFT JOIN

LEFT JOIN keeps every row from the left table and adds matching right-side values. Where there is no match, right-side columns are NULL:

SELECT s.name, c.title
FROM students AS s
LEFT JOIN enrollments AS e ON e.student_id = s.student_id
LEFT JOIN courses AS c ON c.course_id = e.course_id
ORDER BY s.student_id, c.course_id;

Expected: Asha with React and SQL, Ben with SQL, and Chitra with NULL for course title. The left side here is students, so every student remains.

To find students with no courses:

SELECT s.name
FROM students AS s
LEFT JOIN enrollments AS e ON e.student_id = s.student_id
WHERE e.enrollment_id IS NULL;

Expected: Chitra. Check a non-nullable right-table key such as enrollment_id to identify rows with no match.

4. RIGHT JOIN

RIGHT JOIN keeps every row from the right table and matches rows from the left where possible:

SELECT c.title, e.enrollment_id
FROM enrollments AS e
RIGHT JOIN courses AS c ON c.course_id = e.course_id
ORDER BY c.course_id, e.enrollment_id;

Expected: SQL with enrollments 100 and 102, React with 101, and Python with NULL. This is equivalent in row-preservation to swapping the table order and using LEFT JOIN. LEFT JOIN is often easier to read because it makes the preserved table visually clear.

5. FULL OUTER JOIN

FULL OUTER JOIN keeps all rows from both sides, matching where possible and filling unmatched columns with NULL:

SELECT s.name, e.enrollment_id
FROM students AS s
FULL OUTER JOIN enrollments AS e ON e.student_id = s.student_id
ORDER BY s.student_id NULLS LAST, e.enrollment_id NULLS LAST;

Expected: all three students are represented, all three enrollment rows are represented, and Chitra has NULL enrollment fields. In this dataset every enrollment refers to an existing student due to the foreign key, so there is no unmatched enrollment row; a full join still preserves both sides if unmatched values are allowed.

6. CROSS JOIN

CROSS JOIN returns every combination of left and right rows. Three students crossed with three courses produce 3 x 3 = 9 rows:

SELECT s.name, c.title
FROM students AS s
CROSS JOIN courses AS c
ORDER BY s.student_id, c.course_id;

This is a Cartesian product, not an enrollment list. Use it only when every combination is intended, such as generating all student/course options. Forgetting a join condition in a query can accidentally create a large cross product.

7. SELF JOIN

A self join joins a table to itself. It can represent relationships such as employees and their managers. Here is a separate example:

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id INTEGER REFERENCES employees(employee_id)
);

SELECT worker.name AS employee, manager.name AS manager
FROM employees AS worker
LEFT JOIN employees AS manager
    ON manager.employee_id = worker.manager_id;

The table appears twice with different aliases. The left join keeps employees who do not yet have a manager.

8. TABLE ALIASES AND MULTIPLE TABLES

An alias is a short name for a table in one query. In `students AS s`, `s` can prefix a column such as `s.name`. Aliases reduce repetition and clarify which table owns a column when names repeat. Use aliases that communicate purpose.

A three-table join follows each foreign-key relationship:

SELECT s.name AS student_name,
       c.title AS course_title,
       e.enrollment_id
FROM enrollments AS e
JOIN students AS s ON s.student_id = e.student_id
JOIN courses AS c ON c.course_id = e.course_id
ORDER BY s.name, c.title;

The query joins enrollment to student and course independently. Clear ON conditions are essential; joining on unrelated columns can produce misleading duplicates.

PRACTICE

1. List every course and its enrolled students; include courses with zero students.
2. List each student and the number of enrollments. Include Chitra with a count of zero by using LEFT JOIN and COUNT(e.enrollment_id).
3. Display all students alongside all courses using CROSS JOIN, then explain why these are possibilities rather than actual enrollments.
4. Add a manager to the employees table and query each employee-manager pair.

COMMON MISTAKES

- Joining on columns that do not represent the same relationship.
- Omitting an ON clause and unintentionally producing a Cartesian product.
- Using INNER JOIN when unmatched left-side rows must remain.
- Filtering a right-side column in WHERE after a LEFT JOIN, which can remove NULL-extended rows. If the filter should control matches but preserve left rows, consider placing it in ON.
- Counting * after a LEFT JOIN and counting the placeholder row; use COUNT(right_table.primary_key) for matched rows.
- Forgetting table aliases when a column name is ambiguous.

IMPORTANT CONCEPTS

- Primary keys identify rows; foreign keys connect related rows.
- INNER JOIN returns matches only.
- LEFT JOIN preserves all left rows; RIGHT JOIN preserves all right rows.
- FULL OUTER JOIN preserves rows from both sides.
- CROSS JOIN makes every possible pair.
- A self join uses aliases to refer to one table in two roles.
- Choose a join based on which records the result must keep.

LESSON SUMMARY

You joined Students, Courses, and Enrollments using key relationships. You compared INNER, LEFT, RIGHT, FULL OUTER, and CROSS JOIN results, then used a self join for employees and managers. Think first about which unmatched records should remain, then choose the join and write explicit key-based conditions."""
    },
    {
        "title": "Data Modification and Advanced SQL",
        "important_concepts": (
            "INSERT; UPDATE; DELETE; ALTER TABLE; constraints; subqueries; CASE; "
            "UNION; indexes; transactions; parameterized queries"
        ),
        "notes": r"""LESSON 5: DATA MODIFICATION AND ADVANCED SQL

LEARNING OBJECTIVES

By the end of this lesson, you can safely insert, update, and delete rows; change a table with ALTER TABLE; add constraints; use subqueries, CASE, UNION, and indexes; explain transactions; and describe parameterized queries and basic query optimization.

INTRODUCTION

Data modification statements can permanently change a database. Practice on a development database and inspect the target rows before changing them. The examples use PostgreSQL and a Students table. PostgreSQL supports the core operations in this lesson, but syntax and features can differ across database systems.

1. INSERT

Create a practice table:

CREATE TABLE students (
    student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER CHECK (age BETWEEN 1 AND 120)
);

Insert one row, explicitly listing columns:

INSERT INTO students (name, email, age)
VALUES ('Asha Rao', 'asha@example.test', 20)
RETURNING student_id, name;

PostgreSQL's RETURNING clause displays values from inserted rows, including the generated ID. Do not assume the generated ID is 1. Use the returned ID or query by a unique key.

2. UPDATE: ALWAYS CHECK THE TARGET

First inspect the row:

SELECT student_id, name, age
FROM students
WHERE email = 'asha@example.test';

Then update it with a selective condition:

UPDATE students
SET age = 21
WHERE email = 'asha@example.test'
RETURNING student_id, name, age;

WHERE identifies the row to change. Without WHERE, UPDATE changes every row. Before a production update, run a SELECT using the same WHERE condition and verify the target count and values. Use a primary key or unique key when possible.

3. DELETE: ALWAYS CHECK THE TARGET

Inspect the intended row first:

SELECT student_id, name
FROM students
WHERE email = 'asha@example.test';

Then delete only the intended record:

DELETE FROM students
WHERE email = 'asha@example.test'
RETURNING student_id, name;

Without WHERE, DELETE removes every row from the table. It does not drop the table structure, but the data removal may be difficult or impossible to reverse after commit. Verify the condition and affected rows before committing.

4. ALTER TABLE AND CONSTRAINTS

ALTER TABLE changes a table definition:

ALTER TABLE students
ADD COLUMN city VARCHAR(80);

Adding a required column to a populated table requires an appropriate default or a staged backfill in PostgreSQL; plan schema changes rather than assuming old rows have values.

Constraints make invalid states harder to store:

- NOT NULL requires a value.
- UNIQUE prevents duplicate values (PostgreSQL normally permits multiple NULLs in a unique column).
- CHECK requires a boolean condition to pass or be unknown; pair it with NOT NULL if missing values should also be forbidden.
- PRIMARY KEY uniquely identifies each row and implies NOT NULL.
- FOREIGN KEY requires a referenced row to exist, subject to the configured delete/update behavior.

CREATE TABLE courses (
    course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE enrollments (
    enrollment_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    enrolled_on DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'completed')),
    UNIQUE (student_id, course_id)
);

NOT NULL makes the core values required. UNIQUE on (student_id, course_id) prevents a student from having duplicate enrollment rows for the same course. A foreign key prevents references to nonexistent students or courses.

5. SUBQUERIES

A subquery is a query nested inside another statement. Find students whose age is above the average:

SELECT student_id, name, age
FROM students
WHERE age > (SELECT AVG(age) FROM students);

The inner query computes one average; the outer query returns students older than that value. If age is NULL, the comparison is unknown and the row is not returned.

EXISTS checks whether a related row is present:

SELECT s.student_id, s.name
FROM students AS s
WHERE EXISTS (
    SELECT 1
    FROM enrollments AS e
    WHERE e.student_id = s.student_id
);

This returns students with at least one enrollment. The inner query refers to the outer row's student_id, so it is a correlated subquery.

6. CASE EXPRESSIONS

CASE returns a value based on conditions:

SELECT name, age,
       CASE
           WHEN age < 18 THEN 'Minor'
           WHEN age >= 18 THEN 'Adult'
           ELSE 'Age not recorded'
       END AS age_group
FROM students
ORDER BY name;

Conditions are checked from top to bottom; the first matching branch is returned. ELSE handles values that did not match, including NULL age in this example.

7. UNION AND UNION ALL

UNION combines the rows from compatible SELECT queries and removes duplicate result rows. UNION ALL combines them without removing duplicates, and is often faster:

SELECT city AS location
FROM students
WHERE city IS NOT NULL
UNION
SELECT 'Online' AS location
ORDER BY location;

The output is a set of distinct locations plus Online. With UNION ALL, duplicate city values would remain. Each SELECT must return the same number of columns with compatible types, and the final ORDER BY applies to the combined result. PostgreSQL supports both; use UNION ALL when duplicates are meaningful or should be retained.

8. INDEX FUNDAMENTALS

An index is an additional data structure that can help PostgreSQL find rows without scanning every row. Indexes can improve some reads but use storage and add work to INSERT, UPDATE, and DELETE. Do not index every column automatically.

CREATE INDEX idx_students_city ON students (city);

This may help queries that filter or sort by city when the table and query patterns make the index useful. PostgreSQL's planner chooses whether to use an index. Check real workload and query plans with EXPLAIN:

EXPLAIN
SELECT student_id, name
FROM students
WHERE city = 'Pune';

EXPLAIN describes the planned operations; EXPLAIN ANALYZE executes the query and measures it, so use it carefully with expensive or modifying queries. An index is not a guarantee of a faster query, especially for a small table or a condition that matches most rows.

9. TRANSACTIONS, COMMIT, AND ROLLBACK

A transaction groups statements into one unit. COMMIT saves its changes; ROLLBACK discards uncommitted changes:

BEGIN;

UPDATE students
SET age = age + 1
WHERE student_id = 1;

SELECT student_id, name, age
FROM students
WHERE student_id = 1;

-- If the result is correct:
COMMIT;

-- If the result is not correct, use ROLLBACK instead of COMMIT.

Do not issue both COMMIT and ROLLBACK for one transaction. In an interactive practice session, run BEGIN, inspect results, then choose one ending. PostgreSQL supports transactions for ordinary table operations, though exact transactional behavior differs for some commands and other database products.

10. BASIC QUERY OPTIMIZATION

- Select only columns needed by the application, not SELECT * by habit.
- Filter rows with appropriate conditions.
- Use indexes based on real query patterns, not guesses.
- Avoid functions on indexed columns in filters when a direct range condition can express the same logic.
- Use EXPLAIN to understand a PostgreSQL query plan; use EXPLAIN ANALYZE only when executing the query is safe.
- Keep statistics current; PostgreSQL normally maintains them through autovacuum and ANALYZE.
- Optimize based on measurement while keeping results correct.

11. SQL SECURITY AND PARAMETERIZED QUERIES

Never build SQL by concatenating user-provided text into the query string. A malicious value can change the meaning of a dynamically built query. Use parameterized queries so the database driver treats values as data:

-- Python DB-API style illustration; placeholder syntax depends on the driver.
cursor.execute(
    "SELECT student_id, name FROM students WHERE email = %s",
    (email_from_user,)
)

The placeholder and value are sent separately. In SQLAlchemy, use bound parameters through the ORM or text() bind parameters:

from sqlalchemy import text

statement = text(
    "SELECT student_id, name FROM students WHERE email = :email"
)
result = connection.execute(statement, {"email": email_from_user})

The named :email parameter is bound as a value. Do not interpolate it with an f-string. Parameters are for values, not table or column identifiers; if identifiers must be dynamic, choose them from a strict allowlist.

Use least-privilege database accounts, keep credentials out of source code, and do not expose database errors or secrets to end users. Parameterization prevents injection through values; it does not replace authorization or input validation.

12. POSTGRESQL AND CROSS-DATABASE DIFFERENCES

The core SELECT, INSERT, UPDATE, DELETE, joins, constraints, and transaction ideas are widely shared. Specifics vary:

- PostgreSQL supports ILIKE for case-insensitive pattern matching; not all systems do.
- PostgreSQL supports RETURNING for rows affected by INSERT/UPDATE/DELETE; other products may use different syntax or support.
- Identity column syntax, auto-number types, date functions, string functions, JSON types, and upsert syntax vary.
- PostgreSQL's EXPLAIN tools and planner behavior are product-specific.
- SQL standards define common behavior, but vendors extend and interpret features differently.

Use documentation for the actual database engine before copying vendor-specific SQL into another system.

PRACTICE

1. Insert two fictional students and retrieve their generated IDs with RETURNING.
2. Before updating one student's city, run a SELECT with the exact WHERE condition.
3. Add a CHECK constraint for a score between 0 and 100.
4. Use a subquery to find students above average age.
5. Categorize ages with CASE.
6. Compare UNION and UNION ALL using repeated city values.
7. Create an index only after describing a query that could benefit from it.
8. Run an update in a transaction, inspect it, and choose either COMMIT or ROLLBACK.

COMMON MISTAKES

- Running UPDATE or DELETE without a carefully checked WHERE condition.
- Forgetting to check how many rows a write statement affected.
- Assuming ROLLBACK can undo a transaction after COMMIT.
- Treating an index as free or guaranteed to speed up every query.
- Using string concatenation for SQL values instead of parameter binding.
- Assuming SQL dialect-specific features are portable.
- Using EXPLAIN ANALYZE on a query that should not be executed.

IMPORTANT CONCEPTS

- INSERT adds rows; UPDATE changes selected rows; DELETE removes selected rows.
- ALTER TABLE changes schema; constraints enforce data rules.
- Subqueries can provide values or test whether related data exists.
- CASE maps conditions to result values.
- UNION removes duplicates; UNION ALL preserves them.
- Indexes trade storage and write cost for potentially faster reads.
- Transactions group work; COMMIT saves and ROLLBACK undoes uncommitted changes.
- Parameterized queries keep user values separate from SQL syntax.
- PostgreSQL extensions and vendor syntax may not be portable.

LESSON SUMMARY

You practiced safe data modification, table changes, constraints, subqueries, CASE, set operations, indexes, and transactions. You learned to preview affected rows before writes, use parameter binding for user input, and verify performance with PostgreSQL tools. This completes the SQL Programming course foundations; continue by building and querying a small relational project."""
    },
]


def seed_sql_course():
    db = SessionLocal()
    try:
        courses = (
            db.query(Course)
            .filter(Course.title.ilike(COURSE_TITLE))
            .order_by(Course.id)
            .all()
        )
        if len(courses) > 1:
            raise RuntimeError(
                f"Found {len(courses)} courses titled {COURSE_TITLE!r}; "
                "refusing to choose between duplicates."
            )

        if courses:
            course = courses[0]
            if course.title != COURSE_TITLE:
                raise RuntimeError(
                    f"Matching course title differs: {course.title!r}."
                )
        else:
            course = Course(
                title=COURSE_TITLE,
                description=COURSE_DESCRIPTION,
            )
            db.add(course)
            db.flush()

        lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course.id)
            .order_by(Lesson.lesson_order, Lesson.id)
            .all()
        )
        existing_by_title = {}
        for lesson in lessons:
            key = lesson.title.strip().casefold()
            if key in existing_by_title:
                raise RuntimeError(
                    f"Duplicate lesson title in course {course.id}: "
                    f"{lesson.title!r}."
                )
            existing_by_title[key] = lesson

        for order, lesson_data in enumerate(LESSONS, start=1):
            key = lesson_data["title"].casefold()
            lesson = existing_by_title.get(key)
            if lesson is None:
                lesson = Lesson(
                    course_id=course.id,
                    title=lesson_data["title"],
                    notes=lesson_data["notes"],
                    important_concepts=lesson_data["important_concepts"],
                    lesson_order=order,
                )
                db.add(lesson)
                continue

            if lesson.lesson_order != order:
                raise RuntimeError(
                    f"Existing lesson {lesson.id} ({lesson.title}) is at "
                    f"order {lesson.lesson_order}, expected {order}; "
                    "refusing to reorder existing records."
                )
            if not lesson.notes or len(lesson.notes.strip()) < 1000:
                lesson.notes = lesson_data["notes"]
            if not lesson.important_concepts:
                lesson.important_concepts = lesson_data["important_concepts"]

        db.commit()
        db.refresh(course)

        saved_lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course.id)
            .order_by(Lesson.lesson_order, Lesson.id)
            .all()
        )
        print(f"course_id={course.id} title={course.title}")
        for lesson in saved_lessons:
            print(
                f"lesson_id={lesson.id} order={lesson.lesson_order} "
                f"title={lesson.title} notes_chars={len(lesson.notes or '')}"
            )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_sql_course()
