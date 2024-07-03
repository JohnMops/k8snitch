def convert_cpu_to_cores(cpu: str) -> float:
    """
    Converts cpu millicores to cores

    Args:
        cpu (str): CPU ammount for a pod

    Returns:
        float: Returns a float with the CPU cores value
    """
    if cpu.endswith('n'):
        return int(cpu[:-1]) / 1e9  # Convert nanocores to cores
    if cpu.endswith('u'):
        return int(cpu[:-1]) / 1e6  # Convert microcores to cores
    if cpu.endswith('m'):
        return int(cpu[:-1]) / 1000  # Convert millicores to cores
    return float(cpu)  # Assume the value is in cores if no unit

def convert_memory_to_mb(memory: str) -> int:
    """
    Converts Memory value to Mi

    Args:
        memory (str): Memory value for each pod

    Returns:
        int: Returns a Memory value in Mi
    """
    units: dict = {'Ki': 1 / 1024, 'Mi': 1, 'Gi': 1024, 'Ti': 1024 ** 2, 'Pi': 1024 ** 3, 'Ei': 1024 ** 4}
    for unit, factor in units.items():
        if memory.endswith(unit):
            return int(memory[:-len(unit)]) * factor
    return int(memory) / (1024 ** 2) 