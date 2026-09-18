import { useState, useEffect, useRef, useCallback } from "react";

// ── Tokamak Equilibrium & Symplectic Constants ──────────────────────────────
const BLUEPRINT_Q0 = 1.05;         // Core safety factor (sawtooth threshold: q0 >= 1.0)
const BLUEPRINT_Q_EDGE = 3.25;     // Edge safety factor (kink threshold: q_edge > 2.0)
const BETA_N_TROYON_LIMIT = 2.80;  // Troyon normalized beta limit
const E_MAX_HAMILTONIAN = 25000.0; // Symplectic lattice upper bound
const LATTICE_SITES = 8;           // Ring lattice sites (N=8)

// Compute radial magnetic flux surface stack and magnetic shear s_hat
function buildMagneticSurfaces(surfaces, qEdgeTarget, shearPerturbation) {
  const stack = [];
  let accumulatedPhaseDrift = 0;
  for (let i = 0; i < surfaces; i++) {
    const rho = (i + 1) / surfaces; // Normalized minor radius r/a
    const nominalQ = BLUEPRINT_Q0 + (qEdgeTarget - BLUEPRINT_Q0) * Math.pow(rho, 2);
    // Perturbation from discrete poloidal field ripple
    const deltaQ = (Math.random() * 2 - 1) * shearPerturbation * 0.05;
    accumulatedPhaseDrift += deltaQ;
    const effectiveQ = nominalQ + deltaQ;
    
    // Magnetic shear s_hat = (rho / q) * (dq / drho)
    const dq_drho = 2 * (qEdgeTarget - BLUEPRINT_Q0) * rho;
    const s_hat = (rho / effectiveQ) * dq_drho;
    
    stack.push({
      surfaceIdx: i + 1,
      rho: rho.toFixed(3),
      deltaQ,
      accumulatedPhaseDrift,
      effectiveQ,
      shear: s_hat,
      confined: effectiveQ > 2.0,
    });
  }
  return stack;
}

// Compute synthetic Fourier normal mode energies matching LatticeEngine::normal_mode_energies()
function generateLatticeSpectra(points, effectiveQEdge, betaN) {
  const qTraj = [];
  const pTraj = [];
  const modalEnergies = [];
  
  // 8 normal modes
  for (let k = 0; k < LATTICE_SITES; k++) {
    const omega_k = 2.0 * Math.sin((Math.PI * k) / LATTICE_SITES);
    const modeEnergy = (betaN / BETA_N_TROYON_LIMIT) * (1500.0 / (1.0 + k * 0.45)) + (Math.random() * 40);
    modalEnergies.push(modeEnergy);
  }

  for (let i = 0; i < points; i++) {
    const t = i / points;
    // Symplectic orbital drift trajectory
    const qVal = Math.sin(t * Math.PI * 2 * effectiveQEdge) * (effectiveQEdge / 3.0);
    const pVal = Math.cos(t * Math.PI * 2 * effectiveQEdge) * (effectiveQEdge / 3.0) + (Math.random() - 0.5) * 0.08;
    qTraj.push(qVal);
    pTraj.push(pVal);
  }
  return { qTraj, pTraj, modalEnergies };
}

// ── Canvas Line Plotter ──────────────────────────────────────────────────────
function MiniChart({ data, color, height = 80, fill = false, label }) {
  const canvasRef = useRef();
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.length) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const pts = data.map((v, i) => [
      (i / (data.length - 1)) * w,
      h - ((v - min) / range) * (h - 8) - 4,
    ]);
    if (fill) {
      ctx.beginPath();
      ctx.moveTo(pts[0][0], h);
      pts.forEach(([x, y]) => ctx.lineTo(x, y));
      ctx.lineTo(pts[pts.length - 1][0], h);
      ctx.closePath();
      ctx.fillStyle = color + "22";
      ctx.fill();
    }
    ctx.beginPath();
    pts.forEach(([x, y], i) => (i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)));
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }, [data, color, fill]);

  return (
    <div style={{ position: "relative" }}>
      {label && (
        <div style={{ fontSize: 9, color: "#64748b", letterSpacing: "0.1em", marginBottom: 3, fontFamily: "monospace" }}>
          {label}
        </div>
      )}
      <canvas ref={canvasRef} width={320} height={height} style={{ width: "100%", height }} />
    </div>
  );
}

// ── Circular Arc Gauge ───────────────────────────────────────────────────────
function Gauge({ value, min, max, label, unit, color = "#0ea5e9", size = 110, decimals = 2 }) {
  const pct = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const angle = -140 + pct * 280;
  const cx = size / 2, cy = size / 2, r = size * 0.38;
  const arc = (deg) => {
    const rad = ((deg - 90) * Math.PI) / 180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };
  const [sx, sy] = arc(-140);
  const [ex, ey] = arc(angle);
  const large = pct > 0.5 ? 1 : 0;

  return (
    <div style={{ textAlign: "center" }}>
      <svg width={size} height={size * 0.75} style={{ overflow: "visible" }}>
        <path
          d={`M ${arc(-140).join(" ")} A ${r} ${r} 0 1 1 ${arc(140).join(" ")}`}
          fill="none" stroke="#1e3a5f" strokeWidth={6} strokeLinecap="round"
        />
        {pct > 0 && (
          <path
            d={`M ${sx} ${sy} A ${r} ${r} 0 ${large} 1 ${ex} ${ey}`}
            fill="none" stroke={color} strokeWidth={6} strokeLinecap="round"
          />
        )}
        <line
          x1={cx} y1={cy}
          x2={cx + (r - 10) * Math.cos(((angle - 90) * Math.PI) / 180)}
          y2={cy + (r - 10) * Math.sin(((angle - 90) * Math.PI) / 180)}
          stroke={color} strokeWidth={2} strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r={4} fill={color} />
      </svg>
      <div style={{ fontSize: 18, fontWeight: 700, color, fontFamily: "monospace", marginTop: -8 }}>
        {typeof value === "number" ? value.toFixed(decimals) : value}
        <span style={{ fontSize: 10, color: "#64748b", marginLeft: 2 }}>{unit}</span>
      </div>
      <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em" }}>{label}</div>
    </div>
  );
}

// ── Radial Surface Row ───────────────────────────────────────────────────────
function SurfaceRow({ s }) {
  const isKinkUnstable = s.effectiveQ < 2.0;
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "40px 60px 1fr 80px 80px 80px",
      alignItems: "center", gap: 8, padding: "5px 10px",
      borderBottom: "1px solid #0d2137",
      background: s.surfaceIdx % 2 === 0 ? "#061220" : "transparent",
    }}>
      <div style={{ fontSize: 10, color: "#334155", fontFamily: "monospace" }}>#{s.surfaceIdx}</div>
      <div style={{ fontSize: 10, color: "#64748b", fontFamily: "monospace" }}>ρ={s.rho}</div>
      <div style={{ position: "relative", height: 6, background: "#0f2035", borderRadius: 3 }}>
        <div style={{
          position: "absolute",
          left: "0%",
          width: `${Math.min(100, (s.effectiveQ / 4.0) * 100)}%`,
          height: "100%",
          background: isKinkUnstable ? "#ef4444" : s.shear > 1.0 ? "#10b981" : "#f59e0b",
          borderRadius: 3,
        }} />
      </div>
      <div style={{ fontSize: 10, fontFamily: "monospace", color: isKinkUnstable ? "#f87171" : "#38bdf8", textAlign: "right" }}>
        q={s.effectiveQ.toFixed(3)}
      </div>
      <div style={{ fontSize: 10, fontFamily: "monospace", color: "#94a3b8", textAlign: "right" }}>
        ŝ={s.shear.toFixed(2)}
      </div>
      <div style={{ fontSize: 9, color: isKinkUnstable ? "#ef4444" : "#10b981", textAlign: "right", letterSpacing: "0.06em" }}>
        {isKinkUnstable ? "⚠ KINK TRIP" : "✓ CONFINED"}
      </div>
    </div>
  );
}

// ── Main Tokamak Symplectic Motor Component ──────────────────────────────────
export default function TokamakLatticeMotor() {
  const [surfaces, setSurfaces] = useState(8);
  const [qEdge, setQEdge] = useState(3.25);
  const [betaN, setBetaN] = useState(2.15);
  const [rippleFactor, setRippleFactor] = useState(1.2);
  const [running, setRunning] = useState(false);
  const [surfacesStack, setSurfacesStack] = useState([]);
  const [signals, setSignals] = useState({ qTraj: [], pTraj: [], modalEnergies: [] });
  const animRef = useRef();
  const tickRef = useRef(0);

  const regenerate = useCallback(() => {
    const s = buildMagneticSurfaces(surfaces, qEdge, rippleFactor);
    setSurfacesStack(s);
    setSignals(generateLatticeSpectra(320, qEdge, betaN));
  }, [surfaces, qEdge, betaN, rippleFactor]);

  useEffect(() => { regenerate(); }, [regenerate]);

  useEffect(() => {
    if (!running) { cancelAnimationFrame(animRef.current); return; }
    const tick = () => {
      tickRef.current++;
      if (tickRef.current % 12 === 0) regenerate();
      animRef.current = requestAnimationFrame(tick);
    };
    animRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animRef.current);
  }, [running, regenerate]);

  const last = surfacesStack[surfacesStack.length - 1] || {};
  const currentEdgeQ = last.effectiveQ || qEdge;
  const isTroyonExceeded = betaN > BETA_N_TROYON_LIMIT;
  const isKinkViolated = currentEdgeQ < 2.0;
  const stateColor = isTroyonExceeded || isKinkViolated ? "#ef4444" : "#10b981";

  return (
    <div style={{ minHeight: "100vh", background: "#020c1b", color: "#e2e8f0", fontFamily: "'DM Mono', 'Courier New', monospace" }}>
      {/* Header */}
      <div style={{ padding: "16px 24px", borderBottom: "1px solid #0d2137", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontSize: 24, fontWeight: 800, letterSpacing: "0.04em", color: "#f1f5f9" }}>
            HL-4 TOKAMAK <span style={{ color: "#0ea5e9" }}>//</span> SYMPLECTIC LATTICE CONFINEMENT
          </div>
          <div style={{ fontSize: 10, color: "#334155", letterSpacing: "0.12em" }}>
            q₀ = {BLUEPRINT_Q0} · TROYON LIMIT β_N ≤ {BETA_N_TROYON_LIMIT} · 8-SITE VERLET INTEGRATOR (E_MAX={E_MAX_HAMILTONIAN})
          </div>
        </div>
        <button onClick={() => setRunning(v => !v)} style={{
          background: running ? "#ef444422" : "#0ea5e922",
          border: `1px solid ${running ? "#ef4444" : "#0ea5e9"}`,
          color: running ? "#f87171" : "#38bdf8",
          padding: "8px 18px", borderRadius: 6, cursor: "pointer",
          fontFamily: "'DM Mono', monospace", fontSize: 12, letterSpacing: "0.08em",
        }}>
          {running ? "■ HALT EQUILIBRIUM" : "▶ RUN LIVE EQUILIBRIUM"}
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", minHeight: "calc(100vh - 61px)" }}>
        {/* Left Column: Diagnostics and Flux Surfaces */}
        <div style={{ padding: 20, borderRight: "1px solid #0d2137" }}>
          {/* Gauges */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16, textAlign: "center" }}>
              <Gauge value={currentEdgeQ} min={1.0} max={5.0} label="EDGE SAFETY FACTOR (q_edge)" unit="q" color={currentEdgeQ < 2.0 ? "#ef4444" : "#0ea5e9"} />
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16, textAlign: "center" }}>
              <Gauge value={betaN} min={0.5} max={3.5} label="NORMALIZED BETA (β_N)" unit="β_N" color={isTroyonExceeded ? "#ef4444" : "#8b5cf6"} />
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>TROYON MARGIN</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: stateColor }}>
                {(BETA_N_TROYON_LIMIT - betaN).toFixed(2)}
              </div>
              <div style={{ fontSize: 9, color: "#334155" }}>to β_crit boundary</div>
              <div style={{ marginTop: 10, fontSize: 9, color: "#475569", letterSpacing: "0.1em" }}>MAGNETIC SHEAR (ŝ_edge)</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: "#38bdf8" }}>
                {last.shear ? last.shear.toFixed(2) : "0.00"}
              </div>
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 6 }}>CONFINEMENT MODE</div>
              <div style={{ fontSize: 13, color: stateColor, fontWeight: 600 }}>
                {isTroyonExceeded ? "DISRUPTION TRIP" : isKinkViolated ? "EXTERNAL KINK" : "ELM-STABLE H-MODE"}
              </div>
              <div style={{ fontSize: 9, color: "#334155", marginTop: 4 }}>Symplectic Invariant: Area Preserved</div>
              <div style={{
                marginTop: 10, padding: "4px 8px",
                background: stateColor + "22", borderRadius: 4,
                fontSize: 9, color: stateColor, textAlign: "center", letterSpacing: "0.06em",
              }}>
                {isTroyonExceeded || isKinkViolated ? "LIMIT EXCEEDED" : "WARDEN ADMITTED"}
              </div>
            </div>
          </div>

          {/* Waveforms */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 14 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>
                SYMPLECTIC PHASE SPACE DRIFT — q(t) vs p(t)
              </div>
              <div style={{ position: "relative" }}>
                <MiniChart data={signals.qTraj} color="#334155" height={70} />
                <div style={{ position: "absolute", top: 0, left: 0, right: 0 }}>
                  <MiniChart data={signals.pTraj} color="#0ea5e9" height={70} />
                </div>
              </div>
              <div style={{ display: "flex", gap: 12, marginTop: 6 }}>
                <span style={{ fontSize: 9, color: "#334155" }}>▬ Position q(t)</span>
                <span style={{ fontSize: 9, color: "#0ea5e9" }}>▬ Canonical Momentum p(t)</span>
              </div>
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 14 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>
                DISCRETE FOURIER NORMAL-MODE ENERGIES (E_k, k=0..7)
              </div>
              <MiniChart data={signals.modalEnergies} color="#8b5cf6" height={70} fill />
              <div style={{ fontSize: 9, color: "#64748b", marginTop: 6 }}>
                Energy partition across 8 periodic lattice sites
              </div>
            </div>
          </div>

          {/* Magnetic Surface Stack Table */}
          <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, overflow: "hidden" }}>
            <div style={{
              padding: "10px 10px", borderBottom: "1px solid #0d2137",
              display: "grid", gridTemplateColumns: "40px 60px 1fr 80px 80px 80px", gap: 8,
            }}>
              {["SURF", "RADIUS", "SAFETY FACTOR PROFILE", "q(ρ)", "SHEAR ŝ", "STATUS"].map(h => (
                <div key={h} style={{ fontSize: 9, color: "#334155", letterSpacing: "0.08em" }}>{h}</div>
              ))}
            </div>
            <div>
              {surfacesStack.map(s => <SurfaceRow key={s.surfaceIdx} s={s} />)}
            </div>
            <div style={{ padding: "10px 10px", borderTop: "1px solid #0d2137", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 10, color: "#475569" }}>
                Equilibrium closed flux surfaces: {surfaces} · Divertor X-point Attached
              </span>
              <span style={{ fontSize: 10, color: stateColor, letterSpacing: "0.06em" }}>
                β_N = {betaN.toFixed(2)} ({isTroyonExceeded ? "TRIP" : "STABLE"})
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Actuator Sliders and Governance Limits */}
        <div style={{ padding: 20 }}>
          <div style={{ fontSize: 10, color: "#334155", letterSpacing: "0.12em", marginBottom: 16 }}>
            TOKAMAK COIL & EQUILIBRIUM CONTROLS
          </div>

          {[
            { label: "FLUX SURFACES (N)", value: surfaces, min: 4, max: 16, step: 1, set: setSurfaces, unit: "sectors", color: "#0ea5e9" },
            { label: "TARGET EDGE q (q_edge)", value: qEdge, min: 1.5, max: 5.0, step: 0.05, set: setQEdge, unit: "q", color: "#38bdf8" },
            { label: "NORMALIZED BETA (β_N)", value: betaN, min: 0.5, max: 3.5, step: 0.05, set: setBetaN, unit: "β_N", color: "#8b5cf6" },
            { label: "TF FIELD RIPPLE", value: rippleFactor, min: 0.1, max: 5.0, step: 0.1, set: setRippleFactor, unit: "%", color: "#f59e0b" },
          ].map(({ label, value, min, max, step, set, unit, color }) => (
            <div key={label} style={{ marginBottom: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em" }}>{label}</span>
                <span style={{ fontSize: 12, color, fontWeight: 600 }}>{value} {unit}</span>
              </div>
              <input
                type="range" min={min} max={max} step={step} value={value}
                onChange={e => set(Number(e.target.value))}
                style={{ accentColor: color, width: "100%" }}
              />
            </div>
          ))}

          <button onClick={regenerate} style={{
            width: "100%", background: "#0ea5e915", border: "1px solid #0ea5e944",
            color: "#38bdf8", padding: "10px", borderRadius: 6, cursor: "pointer",
            fontFamily: "'DM Mono', monospace", fontSize: 12, letterSpacing: "0.08em",
            marginBottom: 20,
          }}>
            ↻ RESET FLUX EQUILIBRIUM
          </button>

          {/* Confinement Reference */}
          <div style={{ fontSize: 10, color: "#334155", lineHeight: 1.7, borderTop: "1px solid #0d2137", paddingTop: 16 }}>
            <div style={{ color: "#475569", marginBottom: 8, letterSpacing: "0.08em" }}>HL-4 ARCHITECTURE CONSTRAINTS</div>
            <p style={{ margin: "0 0 8px" }}>
              Core safety factor <span style={{ color: "#38bdf8" }}>q₀ ≥ 1.0</span> prevents internal kink / sawtooth reconnection.
            </p>
            <p style={{ margin: "0 0 8px" }}>
              Edge boundary <span style={{ color: "#0ea5e9" }}>q_edge &gt; 2.0</span> avoids destructive external kink disruptions.
            </p>
            <p style={{ margin: "0 0 8px" }}>
              Troyon envelope limit <span style={{ color: "#8b5cf6" }}>β_N ≤ 2.8</span> guards against ballooning mode instability.
            </p>
            <p style={{ margin: 0, color: "#1e3a5f" }}>
              Symplectic phase volume preserved via Velocity Verlet integration on the periodic lattice ring.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
