
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def log_search(request, city):
    from weather.models import SearchHistory
    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

    if user:
        obj, created = SearchHistory.objects.get_or_create(user=user, city=city)
    else:
        ip = get_client_ip(request)
        obj, created = SearchHistory.objects.get_or_create(user_ip=ip, city=city)

    if not created:
        obj.count += 1
        obj.save()
