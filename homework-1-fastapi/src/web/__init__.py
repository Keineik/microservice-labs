"""BT3 web client — a server-rendered (Jinja2 + HTMX) student course-registration
UI. It is a *separate* FastAPI service that talks to the JSON API over HTTP
(``httpx``); it never touches the database directly. This mirrors a real
distributed setup (browser -> web/BFF -> API -> DB) for the UDPT course.
"""
