import math
from .config import RULES
from .utils import ceil_units


# Light Dues
def calculate_light_dues(gt: float) -> float:
    """
    Calculate light dues based on gross tonnage
    
    Args:
        gt: Gross tonnage of vessel
        
    Returns:
        Light dues in ZAR
    """
    units = ceil_units(gt, 100)
    rate = RULES["tariffs"]["light_dues"]["calculation"]["formula_rate"]
    return round(units * rate, 2)


# Port Dues
def calculate_port_dues(gt: float, days: float) -> float:
    """
    Calculate port dues based on gross tonnage and days alongside
    
    Args:
        gt: Gross tonnage of vessel
        days: Days alongside
        
    Returns:
        Port dues in ZAR
    """
    entry_units = ceil_units(gt, 100)
    entry_fee = entry_units * RULES["tariffs"]["port_dues"]["calculation"]["entry_fee"]
    day_units = math.ceil(days)
    daily_fee = entry_units * RULES["tariffs"]["port_dues"]["calculation"]["daily_fee"] * day_units
    return round(entry_fee + daily_fee, 2)


# VTS Dues
def calculate_vts_dues(gt: float, port: str) -> float:
    """
    Calculate VTS dues based on gross tonnage and port
    
    Args:
        gt: Gross tonnage of vessel
        port: Port name
        
    Returns:
        VTS dues in ZAR
    """
    port_key = "Durban_Saldanha" if port in ["Durban", "Saldanha"] else "other_ports"
    rate = RULES["tariffs"]["vts_dues"]["calculation"][port_key]["rate_per_gt"]
    amount = gt * rate
    return round(max(amount, RULES["tariffs"]["vts_dues"]["calculation"]["minimum_fee"]), 2)


# Pilotage Dues
def calculate_pilotage_dues(gt: float, port: str) -> float:
    """
    Calculate pilotage dues based on gross tonnage and port
    
    Args:
        gt: Gross tonnage of vessel
        port: Port name
        
    Returns:
        Pilotage dues in ZAR
    """
    p = RULES["tariffs"]["pilotage_dues"]["calculation"][port]
    units = ceil_units(gt, 100)
    return round(p["base_fee"] + units * p["per_100_gt"], 2)


# Towage Dues
def calculate_towage_dues(gt: float, port: str) -> float:
    """
    Calculate towage dues based on gross tonnage and port
    
    Args:
        gt: Gross tonnage of vessel
        port: Port name
        
    Returns:
        Towage dues in ZAR
    """
    t = RULES["tariffs"]["towage_dues"]["calculation"][port]
    # Determine bracket allocations (standard implementation: two tugs for GT>10000)
    num_tugs = 2 if gt > 10000 else (1 if gt > 2000 else 0.5)
    base = t["base_fee_2001_to_10000"]
    inc = 0
    
    if gt > 10000 and gt <= 50000:
        inc_units = ceil_units(gt - 10000, 100)
        inc = inc_units * t["increment_per_100_gt_10001+"]
    elif gt > 50000 and gt <= 100000:
        inc_units_10k_to_50k = 400  # (50000 - 10000) / 100
        inc_units_50k_plus = ceil_units(gt - 50000, 100)
        inc = (inc_units_10k_to_50k * t["increment_per_100_gt_10001+"]) + (inc_units_50k_plus * t["increment_per_100_gt_50001+"])
    elif gt > 100000:
        inc_units_10k_to_50k = 400  # (50000 - 10000) / 100
        inc_units_50k_to_100k = 500  # (100000 - 50000) / 100
        inc_units_100k_plus = ceil_units(gt - 100000, 100)
        inc = (inc_units_10k_to_50k * t["increment_per_100_gt_10001+"]) + \
              (inc_units_50k_to_100k * t["increment_per_100_gt_50001+"]) + \
              (inc_units_100k_plus * t["increment_per_100_gt_100001+"])
    
    return round((base + inc) * num_tugs, 2)


# Running of Vessel Lines
def calculate_line_running_dues(port: str) -> float:
    """
    Calculate line running dues based on port
    
    Args:
        port: Port name
        
    Returns:
        Line running dues in ZAR
    """
    return round(RULES["tariffs"]["running_of_vessel_lines_dues"]["calculation"][port]["flat_fee"], 2)


# Aggregate
def calculate_all(params: dict) -> dict:
    """
    Calculate all dues based on vessel parameters
    
    Args:
        params: Dictionary with vessel parameters
        
    Returns:
        Dictionary with all calculated dues
    """
    gt = params['gt']
    port = params['port']
    days = params['days_alongside']
    
    light = calculate_light_dues(gt)
    port_due = calculate_port_dues(gt, days)
    vts = calculate_vts_dues(gt, port)
    pilot = calculate_pilotage_dues(gt, port)
    tow = calculate_towage_dues(gt, port)
    line = calculate_line_running_dues(port)
    
    total = round(light + port_due + vts + pilot + tow + line, 2)
    
    return {
        "light_dues": light,
        "port_dues": port_due,
        "vts_dues": vts,
        "pilotage_dues": pilot,
        "towage_dues": tow,
        "line_running_dues": line,
        "total": total
    }