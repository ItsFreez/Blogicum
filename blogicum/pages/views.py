from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """Отображает страницу о сайте."""
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Отображает страницу с правилами сайта."""
    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """Кастомная ошибка 403."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Кастомная ошибка 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Кастомная ошибка 500."""
    return render(request, 'pages/500.html', status=500)
