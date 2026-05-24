def select_lowest_load(counselors):
    available = [i for i,c in enumerate(counselors) if c['available']]
    if not available:
        return None
    return min(available, key=lambda i: counselors[i]['sessions_completed'])

def run_matching(authenticated_students, num_peer_counselors, burnout_threshold, avg_response_time):
    counselors = [{'id': i, 'sessions_completed': 0, 'available': True} for i in range(num_peer_counselors)]
    matched = 0
    unmatched = 0
    for sid in authenticated_students:
        idx = select_lowest_load(counselors)
        if idx is None:
            unmatched += 1
        else:
            counselors[idx]['sessions_completed'] += 1
            matched += 1
            if counselors[idx]['sessions_completed'] >= burnout_threshold:
                counselors[idx]['available'] = False
    loads = [c['sessions_completed'] for c in counselors]
    num_burned = sum(1 for c in counselors if not c['available'])
    avg_load = sum(loads) / len(loads) if loads else 0
    est_rt = avg_response_time * (1 + 2 * (unmatched / max(1, len(authenticated_students))))
    return matched, unmatched, loads, num_burned, avg_load, est_rt
