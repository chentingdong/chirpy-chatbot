from illusionist.schema import IncidentSchema


def test_schema():
    related_incidents = {'7442c8194f105640f86723d18110c731': '100.0',
                         '1a307a184f32da003c89afdd0210c745': '80.4',
                         '72f990684fa966802c1d029d0210c7aa': '80.9'}
    sorted_ri = sorted(related_incidents.items(), key=lambda x: float(x[1]), reverse=True)
    answers = [IncidentSchema.encode(sys_id, float(prob) / 100.0) for sys_id, prob in sorted_ri]
    print(answers)
