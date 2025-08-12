from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class TemplateManager:
    """Shared Jinja2 environment for adapter templates."""

    def __init__(self) -> None:
        templates_dir = Path(__file__).parent / "templates"
        # Use StrictUndefined so undefined variables raise an error during rendering
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            undefined=StrictUndefined,
        )

    def render(
        self,
        template_name: str,
        context: dict[str, Any],
        required_fields: Iterable[str] | None = None,
    ) -> str:
        """Render a template with a context and required-field validation.

        Args:
            template_name: Name of the template file.
            context: Variables to pass into the template.
            required_fields: Iterable of keys that must exist and be truthy in the context.

        Raises:
            ValueError: If any required field is missing or falsy.
            jinja2.TemplateNotFound: If the template is not found.
        """
        required_fields = required_fields or []
        missing = [f for f in required_fields if not context.get(f)]
        if missing:
            raise ValueError(
                f"Missing required fields for template '{template_name}': {', '.join(missing)}"
            )
        template = self.env.get_template(template_name)
        return template.render(**context)


# Singleton manager instance for module-level convenience
_manager = TemplateManager()


def render(
    template_name: str, context: dict[str, Any], required_fields: Iterable[str] | None = None
) -> str:
    """Convenience function to render templates using the shared manager."""
    return _manager.render(template_name, context, required_fields)
