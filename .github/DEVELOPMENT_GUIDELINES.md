# Development Guidelines (applies to all projects)

These guidelines are repository-wide and should be followed for all code and documentation.

- Keep all files under 150 lines. Split large files into smaller feature-focused modules and folders.
- Always follow best practices for files and folder structure (separate concerns, group by feature, prefer small files over monoliths).

Why:
- Smaller files are easier to review, test, and maintain.
- Feature folders improve discoverability and reduce merge conflicts.

Enforcement / Suggestions:
- When a file exceeds ~150 lines, refactor into multiple files under a feature folder.
- Name folders by feature (e.g., `auth/`, `render/`, `ui/`) and keep tests next to implementation (e.g., `auth/test_*.py`).

