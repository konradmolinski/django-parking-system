from django.conf import settings

def calculate_sub_cost(start_date, end_date):

    price_list = settings.PRICE_LIST
    hour_price = sum([price_list[x]['price'] for x in price_list])/len(price_list) * 0.8
    parking_time = end_date - start_date
    return int(parking_time.days * 24 * hour_price)