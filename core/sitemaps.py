from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        # Aquí colocas los nombres de las rutas (name=) de tus urls.py
        return ["home", "about", "contact"]

    def location(self, item):
        return reverse(item)
