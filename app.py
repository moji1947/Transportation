import streamlit as st
import pulp as pl
from model_logic import (solve_logistics_by_group, CAPACITY, COST_RATE,
                         MAX_BUDGET, MAX_DIST, get_customers_for_day)

st.set_page_config(page_title="Logistics Optimizer", page_icon="🚛",
                   layout="wide", initial_sidebar_state="expanded")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html,body,[class*="css"]{ font-family:'IBM Plex Sans Thai',sans-serif; }
.stApp{ background:#080E1A; color:#E2E8F0; }
header[data-testid="stHeader"]{ display:none; }
.block-container{ padding-top:28px !important; max-width:1200px; }

[data-testid="stSidebar"]{ background:#0D1B2A !important; border-right:1px solid #1A3050; }
[data-testid="stSidebar"] label{ color:#94A3B8 !important; font-size:0.75rem !important;
    text-transform:uppercase; letter-spacing:1px; }

.hero{ background:linear-gradient(135deg,#0D1B2A 0%,#0A2540 60%,#0D1B2A 100%);
    border:1px solid #1E3A5F; border-radius:18px;
    padding:30px 40px; margin-bottom:20px; position:relative; overflow:hidden; }
.hero::after{ content:"🚛"; position:absolute; right:36px; top:50%;
    transform:translateY(-50%); font-size:5.5rem; opacity:0.05; }
.hero-badge{ display:inline-block; background:rgba(0,200,255,0.1);
    border:1px solid rgba(0,200,255,0.25); color:#00C8FF;
    padding:3px 12px; border-radius:20px; font-size:0.68rem;
    font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:10px; }
.hero-title{ font-size:1.9rem; font-weight:700; color:#FFF; margin:0 0 5px; }
.hero-sub{ font-size:0.88rem; color:#5B9BD5; margin:0; }

.ctrl{ background:#0D1B2A; border:1px solid #1A3050;
    border-radius:14px; padding:20px 28px; margin-bottom:20px; }
div[data-testid="stSelectbox"] label{ color:#94A3B8 !important;
    font-size:0.75rem !important; text-transform:uppercase; letter-spacing:1px; }
div[data-testid="stSelectbox"]>div>div{ background:#112030 !important;
    border:1px solid #1E3A5F !important; border-radius:10px !important; color:#E2E8F0 !important; }
.stButton>button{ background:linear-gradient(135deg,#0077B6,#00A8CC) !important;
    color:#FFF !important; border:none !important; border-radius:10px !important;
    padding:13px 0 !important; font-size:1rem !important; font-weight:600 !important;
    font-family:'IBM Plex Sans Thai',sans-serif !important; width:100% !important;
    margin-top:20px !important; box-shadow:0 4px 18px rgba(0,168,204,0.3) !important;
    transition:all .2s !important; }
.stButton>button:hover{ box-shadow:0 6px 26px rgba(0,168,204,0.5) !important;
    transform:translateY(-2px) !important; }

.fleet-row{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:16px; }
.fleet-badge{ display:flex; align-items:center; gap:7px; background:#0D1B2A;
    border:1px solid #1A3050; border-radius:8px;
    padding:7px 13px; font-size:0.75rem; color:#94A3B8; }
.dot{ width:9px; height:9px; border-radius:50%; flex-shrink:0; }

.tcard{ border-radius:14px; padding:20px 22px; margin-bottom:4px; }
.t1{ background:#0D1F35; border:1px solid #1E4060; border-top:3px solid #00C8FF; }
.t2{ background:#0E1E30; border:1px solid #1B3A5A; border-top:3px solid #38BDF8; }
.t3{ background:#1A1208; border:1px solid #3D2808; border-top:3px solid #F97316; }
.t4{ background:#18100A; border:1px solid #361E0A; border-top:3px solid #FBBF24; }
.ttitle{ font-size:1rem; font-weight:700; color:#FFF; margin-bottom:2px; }
.tsub{ font-size:0.7rem; color:#475569; text-transform:uppercase; letter-spacing:.8px; margin-bottom:12px; }

.ci{ display:flex; align-items:center; gap:10px; padding:7px 9px;
    background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.035);
    border-radius:7px; margin:4px 0; }
.ci-far{ border:1px solid rgba(251,191,36,0.25); background:rgba(251,191,36,0.04); }
.cc{ font-family:'IBM Plex Mono',monospace; font-size:0.82rem; font-weight:600; min-width:36px; }
.ck{ font-size:0.78rem; color:#94A3B8; min-width:100px; }
.bw{ flex:1; background:rgba(255,255,255,0.05); border-radius:4px; height:5px; overflow:hidden; }
.bf{ height:5px; border-radius:4px; }
.cd{ font-size:0.72rem; color:#64748B; min-width:52px; text-align:right; }
.cd-far{ color:#FBBF24 !important; font-weight:600; }
.far-pin{ font-size:0.65rem; color:#FBBF24; margin-left:2px; }

.ac1{color:#00C8FF;} .af1{background:linear-gradient(90deg,#0077B6,#00C8FF);}
.ac2{color:#38BDF8;} .af2{background:linear-gradient(90deg,#0369A1,#38BDF8);}
.ac3{color:#F97316;} .af3{background:linear-gradient(90deg,#C2410C,#F97316);}
.ac4{color:#FBBF24;} .af4{background:linear-gradient(90deg,#B45309,#FBBF24);}

.caprow{ display:flex; justify-content:space-between; font-size:0.7rem;
    color:#64748B; margin:11px 0 4px; }
.capbg{ background:rgba(255,255,255,0.05); border-radius:6px; height:7px; overflow:hidden; }
.capfill{ height:7px; border-radius:6px; }

/* Max-dist callout per truck */
.maxdist-box{ display:flex; align-items:center; gap:10px;
    background:rgba(251,191,36,0.06); border:1px solid rgba(251,191,36,0.2);
    border-radius:8px; padding:8px 12px; margin:10px 0; font-size:0.78rem; }
.maxdist-label{ color:#94A3B8; }
.maxdist-val{ color:#FBBF24; font-weight:700; font-family:'IBM Plex Mono',monospace; }
.maxdist-cost{ color:#94A3B8; }

.chips{ display:flex; gap:7px; margin-top:12px; flex-wrap:wrap; }
.chip{ flex:1; min-width:68px; background:rgba(0,0,0,0.22);
    border:1px solid rgba(255,255,255,0.05); border-radius:9px;
    padding:8px 9px; text-align:center; }
.cv{ font-size:0.95rem; font-weight:700; color:#FFF; }
.cl{ font-size:0.62rem; color:#475569; text-transform:uppercase; letter-spacing:.4px; margin-top:2px; }

.summary{ background:linear-gradient(135deg,#082032,#0A2E4A);
    border:1px solid #1E4D6B; border-radius:16px;
    padding:26px 34px; margin-top:12px; text-align:center; }
.slbl{ font-size:0.68rem; color:#5B9BD5; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px; }
.sbig{ font-size:2.6rem; font-weight:700; color:#FFF; line-height:1; }
.sunit{ font-size:0.86rem; color:#94A3B8; margin-top:4px; }
.sgrid{ display:flex; gap:12px; margin-top:16px; justify-content:center; flex-wrap:wrap; }
.scell{ background:rgba(255,255,255,0.04); border-radius:10px; padding:10px 20px; }
.scv{ font-size:1.15rem; font-weight:700; color:#00C8FF; }
.scl{ font-size:0.65rem; color:#475569; margin-top:2px; }

/* Model info box */
.model-info{ background:rgba(0,200,255,0.05); border:1px solid rgba(0,200,255,0.15);
    border-radius:10px; padding:14px 18px; margin-bottom:14px; font-size:0.8rem; }
.model-info b{ color:#00C8FF; }

.badge-ok{ display:inline-block; background:rgba(34,197,94,0.1);
    border:1px solid rgba(34,197,94,0.3); color:#4ADE80;
    padding:2px 12px; border-radius:20px; font-size:0.7rem; font-weight:600; letter-spacing:1px; }
.badge-fail{ display:inline-block; background:rgba(239,68,68,0.1);
    border:1px solid rgba(239,68,68,0.3); color:#F87171;
    padding:2px 12px; border-radius:20px; font-size:0.7rem; font-weight:600; }

.infeas{ background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.25);
    border-radius:12px; padding:22px 26px; text-align:center; margin-top:8px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
DAY_TH = {
    "Monday":"วันจันทร์","Tuesday":"วันอังคาร","Wednesday":"วันพุธ",
    "Thursday":"วันพฤหัสบดี","Friday":"วันศุกร์",
}
DAY_GROUP = {
    "Monday":"กลุ่ม 3 + กลุ่ม 1","Tuesday":"กลุ่ม 3 + กลุ่ม 2",
    "Wednesday":"กลุ่ม 3 + กลุ่ม 1","Thursday":"กลุ่ม 3 + กลุ่ม 2",
    "Friday":"กลุ่ม 3 + กลุ่ม 1",
}
TRUCK_STYLE = {
    1:("t1","ac1","af1","#00C8FF","20 ตัน"),
    2:("t2","ac2","af2","#38BDF8","20 ตัน"),
    3:("t3","ac3","af3","#F97316","10 ตัน"),
    4:("t4","ac4","af4","#FBBF24","10 ตัน"),
}
def pct(v, total): return min(int(v / total * 100), 100)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Constraints")
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.75rem;color:#64748B;line-height:2;">
    🏋️ <b style="color:#94A3B8">Capacity</b><br>
    &nbsp;&nbsp;รถ 1-2: 20,000 กก.<br>
    &nbsp;&nbsp;รถ 3-4: 10,000 กก.<br><br>
    📍 <b style="color:#94A3B8">Drop Points</b><br>
    &nbsp;&nbsp;≤ 4 จุด/คัน<br><br>
    🛣️ <b style="color:#94A3B8">Distance (Max Point)</b><br>
    &nbsp;&nbsp;≤ 400 กม./คัน<br><br>
    💰 <b style="color:#94A3B8">Budget (Max Point)</b><br>
    &nbsp;&nbsp;≤ 5,000 บาท/คัน<br><br>
    📦 <b style="color:#94A3B8">Must Serve All</b><br>
    &nbsp;&nbsp;ส่งครบทุกลูกค้า
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#475569;line-height:1.9;">
    <b style="color:#00C8FF;">✦ Max-Distance Model</b><br>
    Distance/Budget คำนวณจาก<br>
    <b style="color:#FBBF24;">จุดไกลสุด</b> ในเส้นทางแต่ละคัน<br>
    ไม่ใช่การบวกทุกจุด<br><br>
    Linearize ด้วย auxiliary var<br>
    <span style="font-family:monospace;color:#94A3B8">M_i ≥ D_j·X_ij  ∀j</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">OR · ILP · Max-Distance Model · 4 Trucks</div>
  <div class="hero-title">🚛 Logistics Optimizer</div>
  <div class="hero-sub">Maximize น้ำหนัก · ส่งครบทุกลูกค้า · Budget จากจุดไกลสุด · ชลบุรี</div>
</div>
""", unsafe_allow_html=True)


# ─── Control ──────────────────────────────────────────────────────────────────
st.markdown('<div class="ctrl">', unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])
with c1:
    day = st.selectbox("เลือกวันจัดส่ง",
        ["Monday","Tuesday","Wednesday","Thursday","Friday"],
        format_func=lambda d: f"{DAY_TH[d]}  —  {d}")
with c2:
    run = st.button("⚡  คำนวณ Optimal")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="fleet-row">
  <div class="fleet-badge"><div class="dot" style="background:#00C8FF"></div>รถคันที่ 1 — Trailer 20t</div>
  <div class="fleet-badge"><div class="dot" style="background:#38BDF8"></div>รถคันที่ 2 — Trailer 20t</div>
  <div class="fleet-badge"><div class="dot" style="background:#F97316"></div>รถคันที่ 3 — 10t</div>
  <div class="fleet-badge"><div class="dot" style="background:#FBBF24"></div>รถคันที่ 4 — 10t</div>
</div>
""", unsafe_allow_html=True)

# ─── Solve ────────────────────────────────────────────────────────────────────
if run:
    with st.spinner("กำลังประมวลผล ILP..."):
        prob, X, M_vars, TRUCKS, Customers, names, weights, dists, rate, cap = \
            solve_logistics_by_group(day)

    status = pl.LpStatus[prob.status]

    if status == "Infeasible":
        st.markdown("""
        <div class="infeas">
          <div style="font-size:2rem;margin-bottom:10px;">⚠️</div>
          <div style="font-size:1rem;font-weight:700;color:#F87171;">Infeasible</div>
          <div style="font-size:0.82rem;color:#94A3B8;margin-top:6px;">
            ลูกค้าบางรายมีระยะทาง > 400 กม. หรือน้ำหนักรวมเกินพิกัดรถทั้ง 4 คัน
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── Collect results ────────────────────────────────────────────────────
    truck_data = {}
    for i in TRUCKS:
        assigned  = [j for j in Customers if pl.value(X[(i, j)]) == 1]
        w         = sum(weights[j] for j in assigned)
        max_d     = pl.value(M_vars[i]) or 0          # จุดไกลสุด (auxiliary var)
        real_cost = max_d * rate                        # cost จากจุดไกลสุด
        truck_data[i] = {
            "assigned": assigned,
            "weight":   w,
            "max_dist": max_d,
            "cost":     real_cost,
        }

    total_w        = sum(td["weight"] for td in truck_data.values())
    total_c        = sum(td["cost"]   for td in truck_data.values())
    total_assigned = sum(len(td["assigned"]) for td in truck_data.values())
    all_served     = (total_assigned == len(Customers))

    served_badge = '<span class="badge-ok">✓ ส่งครบทุกราย</span>' if all_served \
                   else '<span class="badge-fail">⚠ ส่งไม่ครบ</span>'
    st.markdown(f"""
    <p style="font-size:.7rem;text-transform:uppercase;letter-spacing:2px;
              color:#334155;margin:4px 0 14px;">
      ผลลัพธ์ · {DAY_TH[day]} · {DAY_GROUP[day]} &nbsp; {served_badge}
    </p>""", unsafe_allow_html=True)

    # ── 2×2 grid ──────────────────────────────────────────────────────────
    r1c1, r1c2 = st.columns(2, gap="medium")
    r2c1, r2c2 = st.columns(2, gap="medium")
    col_map = {1:r1c1, 2:r1c2, 3:r2c1, 4:r2c2}

    for i in TRUCKS:
        td       = truck_data[i]
        assigned = td["assigned"]
        card_cls, acc, fill, color, tonnage = TRUCK_STYLE[i]
        cap_pct  = pct(td["weight"], cap[i])
        max_w    = max((weights[j] for j in assigned), default=1)
        # which customer is the farthest
        far_j    = max(assigned, key=lambda j: dists[j]) if assigned else None
        budget_pct = pct(td["cost"], MAX_BUDGET)
        budget_color = "#F87171" if budget_pct > 90 else ("#FBBF24" if budget_pct > 70 else color)

        with col_map[i]:
            st.markdown(f"""
            <div class="tcard {card_cls}">
              <div class="ttitle">🚛 รถคันที่ {i}
                <span style="font-size:.72rem;color:{color};font-weight:500;">({tonnage})</span>
              </div>
              <div class="tsub">พิกัด {cap[i]//1000} ตัน · จุดแวะ {len(assigned)}/4</div>
            """, unsafe_allow_html=True)

            if assigned:
                for j in assigned:
                    bar_w   = pct(weights[j], max_w)
                    is_far  = (j == far_j)
                    row_cls = "ci ci-far" if is_far else "ci"
                    dist_cls= "cd cd-far" if is_far else "cd"
                    pin     = '<span class="far-pin">📍max</span>' if is_far else ""
                    st.markdown(f"""
                    <div class="{row_cls}">
                      <span class="cc {acc}">{names[j]}</span>
                      <span class="ck">{weights[j]:,.1f} กก.</span>
                      <div class="bw"><div class="bf {fill}" style="width:{bar_w}%"></div></div>
                      <span class="{dist_cls}">{dists[j]} กม.{pin}</span>
                    </div>""", unsafe_allow_html=True)

                # Max-dist callout
                st.markdown(f"""
                <div class="maxdist-box">
                  <span class="maxdist-label">📍 จุดไกลสุด (M_{i}):</span>
                  <span class="maxdist-val">{td['max_dist']:.0f} กม.</span>
                  <span class="maxdist-cost">→ ค่าขนส่ง {td['cost']:,.0f} บาท</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#334155;font-size:.8rem;padding:6px 0;">— ไม่ถูกใช้งาน —</p>',
                            unsafe_allow_html=True)

            st.markdown(f"""
              <div class="caprow">
                <span>น้ำหนักบรรทุก</span>
                <span style="color:{color};font-weight:600;">{cap_pct}% · {td['weight']:,.0f}/{cap[i]:,} กก.</span>
              </div>
              <div class="capbg"><div class="capfill {fill}" style="width:{cap_pct}%"></div></div>

              <div class="caprow" style="margin-top:8px;">
                <span>Budget (จากจุดไกลสุด)</span>
                <span style="color:{budget_color};font-weight:600;">{td['cost']:,.0f}/{MAX_BUDGET:,} บาท</span>
              </div>
              <div class="capbg">
                <div class="capfill" style="width:{budget_pct}%;
                  background:{budget_color};height:7px;border-radius:6px;"></div>
              </div>

              <div class="chips">
                <div class="chip"><div class="cv">{td['weight']:,.0f}</div><div class="cl">กก.</div></div>
                <div class="chip"><div class="cv">{td['max_dist']:.0f}</div><div class="cl">กม.max</div></div>
                <div class="chip"><div class="cv">{td['cost']:,.0f}</div><div class="cl">บาท</div></div>
                <div class="chip"><div class="cv">{len(assigned)}</div><div class="cl">จุดแวะ</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Summary ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="summary">
      <div class="slbl">สรุปยอดรวมทั้งหมด · {DAY_TH[day]}</div>
      <div class="sbig">{total_w:,.0f}</div>
      <div class="sunit">กิโลกรัม รวมที่ส่งได้ (Maximized)</div>
      <div class="sgrid">
        <div class="scell"><div class="scv">{total_c:,.0f}</div><div class="scl">บาท ต้นทุนรวม</div></div>
        <div class="scell"><div class="scv">{total_assigned}/{len(Customers)}</div><div class="scl">ลูกค้าที่ส่งแล้ว</div></div>
        <div class="scell"><div class="scv">4</div><div class="scl">คัน รถที่ใช้</div></div>
        <div class="scell"><div class="scv">Optimal</div><div class="scl">ILP Status</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="background:#0D1B2A;border:1px dashed #1E3A5F;
         border-radius:16px;padding:56px 40px;text-align:center;margin-top:4px;">
      <div style="font-size:3rem;margin-bottom:12px;">📦</div>
      <div style="font-size:1rem;color:#334155;font-weight:500;">
        เลือกวัน → กด <strong style="color:#00C8FF;">คำนวณ Optimal</strong>
      </div>
      <div style="font-size:0.78rem;color:#1A3050;margin-top:8px;">
        Max-Distance Model · Budget จากจุดไกลสุด · ส่งครบทุกลูกค้า
      </div>
    </div>
    """, unsafe_allow_html=True)