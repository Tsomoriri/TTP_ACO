def max_value(items, maximum):
    sort_items = sorted(
        items, key=lambda x: x['PROFIT']/x['WEIGHT'], reverse=True)
    weight = 0
    for i in sort_items:
        weight += i['WEIGHT']
        if weight > maximum:
            return i['PROFIT']/i['WEIGHT']
