import math

def evaluate_investment(name, c0, cf, d, phi, n, epsilon, cf_is_before_tax=True):
    """
    Evaluates an investment based on NPV, IRR, and DPP.
    
    :param name: Name of the investment
    :param c0: Initial investment cost
    :param cf: Annual cash flow
    :param d: Discount rate
    :param phi: Marginal tax rate
    :param n: Duration of economic life (years)
    :param epsilon: Subsidy of initial investment cost
    :param cf_is_before_tax: If True, treats 'cf' as before-tax cash flow and applies tax + depreciation tax shield.
    """
    # Calculate effective initial investment after subsidy
    effective_c0 = c0 * (1 - epsilon)
    
    # Calculate straight-line depreciation (assuming salvage value is 0)
    depreciation = c0 / n
    
    # Calculate After-Tax Cash Flow (ATCF)
    if cf_is_before_tax:
        # ATCF = (CF - Depreciation) * (1 - phi) + Depreciation
        # Which simplifies to: CF * (1 - phi) + Depreciation * phi
        atcf = cf * (1 - phi) + depreciation * phi
    else:
        # If CF is already assumed to be net (after tax), we just use it directly.
        # However, typically the tax rate is provided to allow calculating taxes.
        atcf = cf
        
    # 1. Net Present Value (NPV)
    # Formula: NPV = -C0_eff + ATCF * [ (1 - (1 + d)^(-n)) / d ]
    pvifa = (1 - (1 + d)**(-n)) / d
    npv = -effective_c0 + atcf * pvifa
    
    # 2. Internal Rate of Return (IRR)
    # Find r such that NPV = 0
    def npv_at_r(r):
        if r == 0:
            return -effective_c0 + atcf * n
        return -effective_c0 + atcf * (1 - (1 + r)**(-n)) / r

    low, high = -0.99, 100.0
    irr = None
    # We use a simple bisection method to find IRR
    if npv_at_r(low) > 0 and npv_at_r(high) < 0:
        for _ in range(100):
            mid = (low + high) / 2
            if npv_at_r(mid) > 0:
                low = mid
            else:
                high = mid
        irr = (low + high) / 2

    # 3. Discounted Payback Period (DPP)
    dpp = None
    # We solve for t: effective_c0 = atcf * [ (1 - (1 + d)^(-t)) / d ]
    # (1 + d)**(-t) = 1 - (effective_c0 * d) / atcf
    ratio = 1 - (effective_c0 * d) / atcf
    if ratio > 0:
        dpp = -math.log(ratio) / math.log(1 + d)
    
    return {
        "Name": name,
        "Initial Cost": c0,
        "Effective Cost": effective_c0,
        "ATCF": atcf,
        "NPV": npv,
        "IRR": irr,
        "DPP": dpp
    }

def main():
    print("=== Investment Evaluation Tool ===")
    
    # Input Common Parameters
    try:
        d = float(input("Enter discount rate (e.g., 0.05 for 5%): "))
        phi = float(input("Enter marginal tax rate (e.g., 0.35 for 35%): "))
        n = int(input("Enter duration of economic life (years, e.g., 20): "))
        epsilon = float(input("Enter subsidy of initial investment cost (e.g., 0.0 for 0%): "))
        
        num_investments = int(input("\nEnter the number of investments to evaluate: "))
        
        investments = []
        for i in range(num_investments):
            print(f"\n--- Investment {i+1} ---")
            name = input("Name of investment: ")
            c0 = float(input("Initial Cost (€): "))
            cf = float(input("Annual Net Cash Flow before tax (€): "))
            investments.append({"name": name, "c0": c0, "cf": cf})
            
    except ValueError:
        print("Invalid input. Please enter numbers correctly.")
        return

    # Evaluate investments
    results = []
    for inv in investments:
        res = evaluate_investment(inv["name"], inv["c0"], inv["cf"], d, phi, n, epsilon, cf_is_before_tax=True)
        results.append(res)

    if not results:
        print("No investments evaluated.")
        return

    # Print results
    print("\n=== Investment Evaluation Results ===")
    print(f"{'Investment':<15} | {'NPV (€)':<12} | {'IRR (%)':<10} | {'DPP (Years)':<15}")
    print("-" * 60)
    
    for res in results:
        name = res['Name']
        npv_str = f"{res['NPV']:,.2f}"
        irr_str = f"{res['IRR']*100:.2f}%" if res['IRR'] is not None else "N/A"
        dpp_str = f"{res['DPP']:.2f}" if res['DPP'] is not None else "No payback"
        
        print(f"{name[:15]:<15} | {npv_str:<12} | {irr_str:<10} | {dpp_str:<15}")

    print("\n=== Optimal Investment Decision ===")
    # The optimal investment based on standard economic criteria is the one with the highest NPV
    optimal = max(results, key=lambda x: x['NPV'])
    print(f"Based on the Net Present Value (NPV) criterion, the optimal investment is {optimal['Name']}")
    print(f"with an NPV of €{optimal['NPV']:,.2f}.")

if __name__ == "__main__":
    main()
