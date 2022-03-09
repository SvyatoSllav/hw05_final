from django.views.generic.base import TemplateView


class AuthorStaticPage(TemplateView):
    template_name = 'about/author.html'


class TechStaticPage(TemplateView):
    template_name = 'about/tech.html'
