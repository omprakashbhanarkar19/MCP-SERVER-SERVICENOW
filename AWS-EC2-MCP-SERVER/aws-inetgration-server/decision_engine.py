def should_restart(cpu, memory):
    if cpu > 80 and memory > 75:
        return True
    return False
