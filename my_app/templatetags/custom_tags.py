

from django import template
import os

register = template.Library()

@register.filter
def check_file_exist(booking_seq):
    file_path = f'my_app/static/contract/{str(booking_seq)}.pdf'
    return os.path.exists(file_path)
