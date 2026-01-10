from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse
from fastapi import Request
import os

template_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(template_dir))


def render_template(template_name: str, request: Request = None, **context) -> HTMLResponse:
    """Render a Jinja2 template with flash message support."""
    # Extract flash message from session if available
    if request and "flash_message" in request.session:
        context["flash_message"] = request.session.pop("flash_message")
    
    # Add request to context for template access
    if request:
        context["request"] = request
    
    template = env.get_template(template_name)
    return HTMLResponse(content=template.render(**context))

