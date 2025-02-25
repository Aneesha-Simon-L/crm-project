from django import template

#  create a class

#  create a library (object must be the name 'register')

register = template.Library()

# @register.simple_tag
# def lowercase(word):

#     return word.lower()

@register.simple_tag
def check_user_roles(request,roles):

    roles = roles.split(',')

    allow = False

    if request.user.role in roles:

        allow = True
    
    return allow
