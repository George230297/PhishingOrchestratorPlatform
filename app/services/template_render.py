from jinja2 import Template

class TemplateRenderService:
    @staticmethod
    def render_template(html_content: str, context: dict) -> str:
        """
        Renders an HTML template with values from the context dictionary.
        Safe for basic string replacement.
        """
        try:
            template = Template(html_content)
            return template.render(**context)
        except Exception as e:
            # Fallback or log error
            print(f"Error rendering template: {e}")
            return html_content
