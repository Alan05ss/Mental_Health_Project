def run_authentication(registered_students, trust_level):
    authenticated = []
    num_failed = 0
    for sid in registered_students:
        if random.random() <= trust_level:
            authenticated.append(sid)
        else:
            num_failed += 1
    return authenticated, len(authenticated), num_failed
