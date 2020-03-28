from django import template
from follow_system.models import FollowSystem
register = template.Library()



@register.filter()
def status(me,other):
    value = FollowSystem.follow_status(me,other)
    if value:
        return "UNFOLLOW"
    else:
        return "FOLLOW"
