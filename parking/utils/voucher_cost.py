from django.conf import settings

def get_voucher_cost(hours):

    price_list = settings.PRICE_LIST
    hour_price = sum([price_list[x]['price'] for x in price_list])/len(price_list) * 0.8
    return int(hours * hour_price)