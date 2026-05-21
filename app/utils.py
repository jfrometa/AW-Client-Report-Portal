from flask import render_template
import os

def generate_pdf(template_name, context, output_path=None):
    from weasyprint import HTML
    html_content = render_template(template_name, **context)

    base_url = os.path.dirname(os.path.dirname(__file__))
    html = HTML(string=html_content, base_url=base_url)

    if output_path:
        html.write_pdf(output_path)
        return output_path
    else:
        return html.write_pdf()
