from datetime import date


def year(request):
    year = date.today().year
    return {
        'year': year,
    }
