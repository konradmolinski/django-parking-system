from django.db.models import Q
from parking.models import Subscription

def client_has_subscription_in_requested_range(client, start_date, end_date):
    pre_date_query = Subscription.objects.filter(
        Q(client_id=client),
        Q(start_date__gt=start_date),
        Q(start_date__lt=end_date)
    )

    post_date_query = Subscription.objects.filter(
        Q(client_id=client),
        Q(start_date__lt=start_date),
        Q(end_date__gt=start_date)
    )

    exact_date_query = Subscription.objects.filter(
        Q(client_id=client),
        Q(start_date=start_date) | Q(end_date=end_date)
    )
    return not (pre_date_query or post_date_query or exact_date_query)
