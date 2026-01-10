# ParamTech QA Automation (Online Exam System UI)

This repository is a Java-based UI test automation project built with **Selenium WebDriver + Cucumber (BDD) + JUnit Platform Suite**.

It is configured to test the **Exam System v2** (FastAPI web UI) locally.

---

## Prerequisites

- Java **17+**
- Maven
- The **exam_systemv2** web app running locally (seeded demo data)

### Start the Exam System v2 (example)

In the exam_systemv2 project:

```bash
cd /Users/<yourusername>/Desktop/exam_systemv2
source venv/bin/activate
bash ./scripts/init_db.sh
bash ./scripts/run_dev.sh

```

The UI should be available at:
- `http://0.0.0.0:8000` or `http://127.0.0.1:8000`

---

## Tech Stack

- **Java**: 17+
- **Build tool**: Maven
- **Test stack**:
  - Selenium WebDriver
  - Cucumber (cucumber-java + cucumber-junit-platform-engine)
  - JUnit Platform / Suite
  - WebDriverManager (auto driver management)

---

## Configuration

Runtime config is here:

`src/test/resources/config/test.properties`

Key fields:
- `baseUrl` (default: `http://127.0.0.1:8000`)
- `browser` (`chrome` / `firefox`)
- `headless` (`true` / `false`)
- demo users:
  - `admin.username` / `admin.password`
  - `teacher.username` / `teacher.password`
  - `student.username` / `student.password`

Default demo users (seeded by exam_systemv2):
- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher` / `teacher123`
- **Student**: `student1` / `student123`

---

## Project Structure

- `src/test/java/com/paramtech/`
  - `driver/` -> WebDriver factory
  - `hooks/` -> Cucumber hooks (setup/teardown)
  - `locators/` -> centralized Selenium `By` locators
  - `pages/` -> Page Objects (`BasePage` + feature pages)
  - `steps/` -> Cucumber step definitions
  - `utils/` -> config + wait helpers
- `src/test/resources/`
  - `features/exam_system/` -> Cucumber feature files
  - `config/test.properties` -> runtime config
  - `cucumber.properties` -> Cucumber engine configuration

---

## Running Tests

### IntelliJ

Run:
- `src/test/java/com/paramtech/runner/RunCucumberTest.java`

### Terminal

```bash
mvn test
```

---

## Scenarios Covered

- Login (admin / teacher / student)
- Invalid login
- Logout (session should end)
- Navigation and access control (protected pages redirect to login)
- Teacher dashboard (key navigation cards)
- Student dashboard (assignments table)
- Teacher question creation (MCQ + True/False + validation)
- Teacher exam creation (create + validation)

