import pulp as pl

# ── ข้อมูลลูกค้า ──────────────────────────────────────────────────────────────
G3_NAMES   = ["A05", "A09", "A11"]
G3_WEIGHTS = [11352.3, 10422.7, 9477.8]
G3_DIST    = [208, 59, 35]

G1_NAMES   = ["A01", "A06", "A08", "A10", "A16", "A17"]
G1_WEIGHTS = [3207.6, 5370.4, 4827.3, 2935.8, 5220.6, 5028.2]
G1_DIST    = [38, 10, 45, 50, 15, 12]

G2_NAMES   = ["A03", "A04", "A07", "A12", "A13", "A15", "A19"]
G2_WEIGHTS = [3426.7, 6798.0, 2103.5, 3569.9, 3877.1, 3219.4, 1821.4]
G2_DIST    = [25, 101, 30, 20, 28, 33, 40]

COST_RATE  = 23.5   # บาท/กม.

# ── Fleet ─────────────────────────────────────────────────────────────────────
TRUCKS = [1, 2, 3, 4]
CAPACITY = {
    1: 20_000,   # Trailer 20 ตัน
    2: 20_000,   # Trailer 20 ตัน
    3: 10_000,   # รถเพิ่มเติม 10 ตัน
    4: 10_000,   # รถเพิ่มเติม 10 ตัน
}
MAX_DROPS  = 4
MAX_DIST   = 400    # กม. — ระยะจุดไกลสุดต่อคัน
MAX_BUDGET = 5_000  # บาท — คำนวณจากจุดไกลสุด ไม่บวกทุกจุด


def get_customers_for_day(day: str):
    day = day.strip().capitalize()
    names   = list(G3_NAMES)
    weights = list(G3_WEIGHTS)
    dists   = list(G3_DIST)
    if day in ["Monday", "Wednesday", "Friday"]:
        names += G1_NAMES;  weights += G1_WEIGHTS;  dists += G1_DIST
    elif day in ["Tuesday", "Thursday"]:
        names += G2_NAMES;  weights += G2_WEIGHTS;  dists += G2_DIST
    return names, weights, dists


def solve_logistics_by_group(selected_day: str):
    """
    Objective : Maximize น้ำหนักรวมที่ส่งได้
    Constraint: ส่งครบทุกลูกค้า (== 1)
    Fleet     : 4 คัน (20t×2 + 10t×2)

    Distance/Budget ใช้ระยะจุดไกลสุดในเส้นทางรถแต่ละคัน
    แทนการบวกระยะทางทุกจุด (สมจริงกว่า เพราะรถวิ่งเส้นทางเดียว)

    Linearize max() ด้วย auxiliary variable M_i:
        M_i >= D_j * X_ij    ∀i, ∀j   (M_i ≥ ระยะของทุกจุดที่รับ)
        M_i <= MAX_DIST                (distance constraint)
        M_i * COST_RATE <= MAX_BUDGET  (budget constraint)
    → M_i จะถูก ILP ดึงให้เท่ากับ max(D_j : X_ij=1)
    """
    names, weights, dists = get_customers_for_day(selected_day)
    n         = len(names)
    Customers = range(n)
    BIG_M     = max(dists) + 1  # Big-M สำหรับ linearization

    prob = pl.LpProblem("Logistics_MaxWeight_MaxDist", pl.LpMaximize)

    # ── ตัวแปรหลัก: X[i,j] ∈ {0,1} ─────────────────────────────────────────
    X = pl.LpVariable.dicts(
        "X",
        [(i, j) for i in TRUCKS for j in Customers],
        cat="Binary"
    )

    # ── Auxiliary variable: M[i] = ระยะทางจุดไกลสุดของรถคัน i ──────────────
    # M_i ∈ [0, MAX_DIST] — continuous
    M = pl.LpVariable.dicts(
        "M",
        TRUCKS,
        lowBound=0,
        upBound=MAX_DIST,
        cat="Continuous"
    )

    # ── Objective: Maximize total weight ─────────────────────────────────────
    prob += pl.lpSum(
        weights[j] * X[(i, j)]
        for i in TRUCKS for j in Customers
    )

    for i in TRUCKS:
        # 1) Capacity
        prob += (
            pl.lpSum(weights[j] * X[(i, j)] for j in Customers) <= CAPACITY[i],
            f"Cap_{i}"
        )

        # 2) Drop points
        prob += (
            pl.lpSum(X[(i, j)] for j in Customers) <= MAX_DROPS,
            f"Drop_{i}"
        )

        # 3) Distance constraint — ใช้จุดไกลสุด M_i แทน Σ D_j
        prob += (M[i] <= MAX_DIST, f"Dist_{i}")

        # 4) Budget constraint — คำนวณจากจุดไกลสุด M_i
        prob += (M[i] * COST_RATE <= MAX_BUDGET, f"Budget_{i}")

        # 5) Auxiliary linearization: M_i >= D_j * X_ij  ∀j
        #    ถ้า X_ij = 1 → M_i >= D_j  (บังคับให้ M_i ≥ ระยะจุดนั้น)
        #    ถ้า X_ij = 0 → constraint = M_i >= 0 (ไม่มีผล)
        for j in Customers:
            prob += (
                M[i] >= dists[j] * X[(i, j)],
                f"MaxDist_{i}_{j}"
            )

    # 6) Must serve every customer exactly once
    for j in Customers:
        prob += (
            pl.lpSum(X[(i, j)] for i in TRUCKS) == 1,
            f"MustServe_{j}"
        )

    prob.solve(pl.PULP_CBC_CMD(msg=0))

    return prob, X, M, TRUCKS, Customers, names, weights, dists, COST_RATE, CAPACITY