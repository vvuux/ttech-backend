from django import template

register = template.Library()

@register.filter(name='price')
def price_display(price):
    price = str(price).split('.')[0][::-1]
    new_price = ''
    for i in range(0,len(price),3):
        if i+3 >= len(price):
            return (new_price + price[i::])[::-1]
        new_price += price[i:i+3]
        new_price += '.'

@register.filter(name='make_list')
def make_list(number):
    return range(1,number+1)

@register.filter(name='limit_page')
def limit_page(page,max,display_page=5):
    """
    if display_page is odd => display_page+1
    """
    if max <= display_page:
        return range(1,max+1)

    limit_range = int(display_page/2)
    start_num = page - limit_range
    end_num = page + limit_range

    if start_num <= 0:
        start_num = 1
        end_num = end_num + limit_range - (page - start_num)
        return range(start_num,end_num+1)
    if end_num > max:
        start_num = start_num - (end_num - max)
        end_num = max
        return range(start_num,end_num+1)
    else:
        return range(start_num,end_num+1)

@register.filter(name='devide_into_two')
def devide_into_two(num):
    return num/2