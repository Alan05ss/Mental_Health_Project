def run_registration(num_students, registration_failure_rate=0.0):
    registered = []
    num_failed = 0
    for i in range(num_students):
        if random.random() > registration_failure_rate:
            registered.append(i)
        else:
            num_failed += 1
    return registered, len(registered), num_failed
