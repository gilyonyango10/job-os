# Engineering Principles

## Architecture

Frontend:
- React
- TypeScript
- Tailwind CSS

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy

Database:
- PostgreSQL

## Development Principles

1. Keep the architecture simple.
2. Build small vertical slices.
3. Do not introduce infrastructure before it is necessary.
4. Do not create abstractions without a concrete use case.
5. Keep business logic separate from UI code.
6. Validate data at system boundaries.
7. Use typed interfaces between frontend and backend.
8. Keep AI functionality modular.
9. Store AI-generated analysis so it does not need to be regenerated unnecessarily.
10. Never hard-code secrets or API keys.

## AI Architecture

AI functionality should eventually be separated into focused services:

- JobParser
- RequirementExtractor
- CandidateMatcher
- GapAnalyzer
- CVOptimizer
- CoverLetterGenerator
- ApplicationQuestionGenerator

Do not implement these all at once.

This iteration implements `RequirementExtractor` only. It writes structured `JobRequirement` rows from a job description. Candidate matching stays in the deterministic engine and is never decided by the model.

## MVP Rule

Every feature must answer:

"Does this help the user move a job closer to an interview?"

If not, it should not be prioritized for the MVP.
