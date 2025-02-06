from datetime import datetime


def current_year(request):
    # Get the current year
    return {
        'current_year': datetime.now().year
    }
