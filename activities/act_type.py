from models import Activity, ActivityType

act = Activity.objects.all()

for a in act:
    at, created = ActivityType.objects.get_or_create(type=a.type)
    print(at.type)
    a.activity_type = at
    a.save()
