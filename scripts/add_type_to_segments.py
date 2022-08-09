from activities.models import Segment, SegmentEffort, Activity, ActivityType, StaredSegment

se = SegmentEffort.objects.all()

for e in se:
    s = Segment.objects.get(id=e.segment_id)
    s.type = e.activity.type
    s.save()
