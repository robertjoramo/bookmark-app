from fastapi.templating import Jinja2Templates
from urllib.parse import urlparse


templates = Jinja2Templates(directory="templates")


# URL PARSER #
def get_domain(url):
    domain = ""
    if url:
        domain = urlparse(url).netloc
    return domain

templates.env.filters["domain"] = get_domain

# END URL PARSER #