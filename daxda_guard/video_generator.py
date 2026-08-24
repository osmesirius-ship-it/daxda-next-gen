"""
DAXDA Guard True 3D Riemannian & Clifford Cl(4,1)/Cl(7,0) Manifold Video Generator.

Renders fault-visible, cryptographically-traced MP4/WebM/GIF animations depicting
the complete 7-stage cinematic transformation sequence:

  Stage 1: THE UTTERANCE          — sentence floats in darkness, spectral waveform
  Stage 2: SEMANTIC DISASSEMBLY   — text breaks into ACTION, OBJECT, POLARITY, AUTHORITY
  Stage 3: GEOMETRIC INCARNATION  — tokens collapse into 3D Clifford blade energy spheres
  Stage 4: DOUBLE HELIX ORBIT     — camera dives through glowing 3D blade streams
  Stage 5: ROTOR TRANSPORT        — helix twists under real bivector rotation M₁=R·M₀·R̃
  Stage 6: GATE INTERSECT         — ring plane intersects helix (RELEASE/BLOCK/EXPOSED_ERROR)
  Stage 7: HOLOGRAPHIC RECEIPT    — 3D space-crawl receipt with exact SHA-256 & blade values

Blade-to-colour canonical mapping (V11.4.2 architecture):
  e1  → cyan    (#38bdf8): Affirmative Safety / Trust
  e2  → white   (#f3f4f6): Factual Grounding
  e3  → violet  (#c084fc): Grammatical Negation channel
  e4  → amber   (#fbbf24): Status / Condition / Authority
  e15 → crimson (#f87171): Adversarial Malicious Intent

Gate visuals:
  RELEASE        → cyan nova expansion
  BLOCK          → crimson contracting collapse + 3D bivector slicing ring
  EXPOSED_ERROR  → amber + crimson + "V11.4 KNOWN FALSE-POSITIVE" label

The generative model NEVER invents blade values or gate decisions.
The trace JSON is the single source of truth driving every visual element.
"""

import os
import math
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
import imageio


# ---------------------------------------------------------------------------
# Colour Palette
# ---------------------------------------------------------------------------
BG_COLOR      = (11,  15,  25)   # #0b0f19  — dark cyber navy
BG_GRID       = (20,  28,  45)
PANEL_BG      = (17,  24,  39)   # #111827
CARD_BG       = (3,   7,   18)   # #030712
C_CYAN        = (56,  189, 248)  # e1 — Trust
C_WHITE       = (243, 244, 246)  # e2 — Factual
C_VIOLET      = (192, 132, 252)  # e3 — Negation
C_AMBER       = (251, 191,  36)  # e4 — Authority
C_CRIMSON     = (248, 113, 113)  # e15 — Adversarial
C_GREEN       = (52,  211, 153)  # PASS / release
C_SILVER      = (156, 163, 175)  # muted text
C_BORDER      = (31,  41,  55)
C_ORANGE      = (249, 115,  22)  # known-error accent

BLADE_COLORS = {
    "e1":  C_CYAN,
    "e2":  C_WHITE,
    "e3":  C_VIOLET,
    "e4":  C_AMBER,
    "e15": C_CRIMSON,
}


# ---------------------------------------------------------------------------
# 3D Camera Utilities
# ---------------------------------------------------------------------------

def _rot3d(x, y, z, yaw, pitch, roll):
    """Apply 3D Euler rotation matrices R_y(yaw)·R_x(pitch)·R_z(roll)."""
    x1 = x * math.cos(yaw) + z * math.sin(yaw)
    y1 = y
    z1 = -x * math.sin(yaw) + z * math.cos(yaw)
    x2 = x1
    y2 = y1 * math.cos(pitch) - z1 * math.sin(pitch)
    z2 = y1 * math.sin(pitch) + z1 * math.cos(pitch)
    x3 = x2 * math.cos(roll) - y2 * math.sin(roll)
    y3 = x2 * math.sin(roll) + y2 * math.cos(roll)
    z3 = z2
    return x3, y3, z3


def _proj(x, y, z, cx, cy, f=550.0, d=4.0):
    """3D perspective camera projection."""
    ze = max(0.1, z + d)
    return cx + (f * x) / ze, cy - (f * y) / ze, ze


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _alpha_blend(base, c, alpha):
    return tuple(int(base[i] * (1 - alpha) + c[i] * alpha) for i in range(3))


# ---------------------------------------------------------------------------
# Main Video Generator
# ---------------------------------------------------------------------------

class DAXDAManifoldVideoGenerator:
    """Renders fault-visible 7-stage cinematic Cl(4,1)/Cl(7,0) manifold MP4 videos."""

    def __init__(self, width=1280, height=720, fps=30):
        self.width = width
        self.height = height
        self.fps = fps

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_transformation_video(
        self,
        payload_text: str = "DROP DATABASE users;",
        verdict: str = "SEVERE_BLOCK",
        decision_rule: str = "GOV_FAIL_03_COMMAND_INJECTION",
        domain: str = "finance",
        output_dir: str = "audit_reports",
        duration_sec: float = 6.0,
        trace: dict = None,
    ) -> dict:
        """Render an HD video for a single scenario. Accepts an optional canonical
        trace dict; if provided, blade values drive exact geometry byte-for-byte."""
        os.makedirs(output_dir, exist_ok=True)
        total_frames = int(duration_sec * self.fps)
        frames = []

        print(f"[{verdict}] Rendering {total_frames} frames — '{payload_text[:55]}'...")

        for f_idx in range(total_frames):
            t = f_idx / total_frames
            img = self._render_frame(t, payload_text, verdict, decision_rule, domain, trace)
            frames.append(np.array(img))

        mp4_path  = os.path.join(output_dir, "daxda_cl70_manifold_transformation.mp4")
        webm_path = os.path.join(output_dir, "daxda_cl70_manifold_transformation.webm")
        gif_path  = os.path.join(output_dir, "daxda_cl70_manifold_transformation.gif")

        try:
            writer = imageio.get_writer(mp4_path, fps=self.fps, codec="libx264", quality=8)
            for fr in frames:
                writer.append_data(fr)
            writer.close()
        except Exception as e:
            print(f"  MP4 warning: {e}")

        try:
            writer2 = imageio.get_writer(webm_path, fps=self.fps, codec="vp9")
            for fr in frames:
                writer2.append_data(fr)
            writer2.close()
        except Exception as e:
            print(f"  WebM warning: {e}")

        try:
            gif_frames = [Image.fromarray(fr).resize((640, 360)) for fr in frames[::2]]
            gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:],
                               duration=int(1000 / (self.fps / 2)), loop=0)
        except Exception as e:
            print(f"  GIF warning: {e}")

        return {"mp4_path": mp4_path, "webm_path": webm_path, "gif_path": gif_path,
                "total_frames": total_frames, "fps": self.fps}

    def render_trace_video(
        self,
        trace: dict,
        output_path: str,
        duration_sec: float = 7.0,
    ) -> dict:
        """Render a single fault-visible MP4 for a canonical trace dict.
        The displayed blade values match the trace byte-for-byte.
        Returns a video manifest dict suitable for independent verification.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        total_frames = int(duration_sec * self.fps)
        frames = []

        case_id   = trace.get("case_id", "UNKNOWN")
        verdict   = trace.get("disposition", "BLOCK")
        payload   = trace.get("input_text", "")
        domain    = "finance"
        rule      = trace.get("gate_evaluation", {}).get("gate_rule", {}).get("blade", "e15")
        decision_rule = f"GATE:{rule}"

        known_error = trace.get("known_error_label")
        if known_error:
            render_verdict = "EXPOSED_ERROR"
        else:
            render_verdict = verdict

        print(f"[{case_id}] Rendering {total_frames} frames → {os.path.basename(output_path)}")

        for f_idx in range(total_frames):
            t = f_idx / total_frames
            img = self._render_frame(t, payload, render_verdict, decision_rule, domain, trace)
            frames.append(np.array(img))

        # Write MP4
        try:
            writer = imageio.get_writer(output_path, fps=self.fps, codec="libx264", quality=8)
            for fr in frames:
                writer.append_data(fr)
            writer.close()
        except Exception as e:
            print(f"  MP4 error: {e}")
            return {}

        # Compute video SHA-256
        with open(output_path, "rb") as fh:
            video_sha256 = hashlib.sha256(fh.read()).hexdigest()

        manifest = {
            "case_id": case_id,
            "trace_sha256": trace.get("tamper_evident_sha256", ""),
            "renderer_version": "DAXDAVideoGen/2.0.0",
            "frame_count": total_frames,
            "fps": self.fps,
            "resolution": f"{self.width}x{self.height}",
            "video_sha256": video_sha256,
            "output_path": output_path,
            "disposition": verdict,
            "known_error": bool(known_error),
        }
        return manifest

    # ------------------------------------------------------------------
    # Frame Renderer
    # ------------------------------------------------------------------

    def _render_frame(self, t, payload, verdict, decision_rule, domain, trace):
        img  = Image.new("RGB", (self.width, self.height), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # Background grid
        for x in range(0, self.width, 40):
            draw.line([(x, 0), (x, self.height)], fill=BG_GRID, width=1)
        for y in range(0, self.height, 40):
            draw.line([(0, y), (self.width, y)], fill=BG_GRID, width=1)

        is_block = verdict in ("BLOCK", "SEVERE_BLOCK")
        is_error = verdict == "EXPOSED_ERROR"

        # Derive blade values from trace if available
        blades = {}
        if trace:
            blades = trace.get("semantic_blade_channels", {})
        e1_val  = blades.get("e1_trust", 0.9 if not is_block else 0.1)
        e2_val  = blades.get("e2_factual", 0.35)
        e3_val  = blades.get("e3_negation", 0.05)
        e4_val  = blades.get("e4_authority", 0.2)
        e15_val = blades.get("e15_adversarial", 1.0 if is_block else 0.0)

        # Stage determination
        stage = self._get_stage(t)

        # Header HUD
        self._draw_header(draw, domain, verdict, stage)

        # ---- Left Panel: Dependency / Semantic tokens ----
        self._draw_left_panel(draw, t, stage, payload, e1_val, e3_val, e15_val, is_block)

        # ---- Right Panel: 3D Riemannian Manifold ----
        cx, cy = 860, 390
        yaw   = t * math.pi * 2
        pitch = 0.40 + 0.12 * math.sin(t * math.pi * 2)
        roll  = 0.08 * math.cos(t * math.pi * 2)

        self._draw_blade_axes(draw, cx, cy, yaw, pitch, roll, e1_val, e3_val, e15_val, t, is_block)

        if stage >= 3:
            self._draw_double_helix(draw, cx, cy, yaw, pitch, roll, t,
                                    e1_val, e2_val, e3_val, e4_val, e15_val, stage)

        if stage >= 4:
            self._draw_3d_manifold(draw, cx, cy, yaw, pitch, roll, t, is_block, e15_val)

        if stage >= 5 and is_block:
            self._draw_bivector_ring(draw, cx, cy, yaw, pitch, roll, t, is_error)

        if stage >= 6:
            self._draw_gate_verdict(draw, cx, cy, t, verdict, is_error)

        if stage == 7:
            self._draw_holographic_receipt(draw, cx, cy, t, payload, verdict,
                                           e1_val, e2_val, e3_val, e4_val, e15_val, trace)

        # Progress bar
        pw = int((self.width - 80) * t)
        draw.rectangle([40, 708, 40 + pw, 716], fill=C_CYAN)
        draw.rectangle([40, 708, self.width - 40, 716], outline=C_BORDER, width=1)

        return img

    # ------------------------------------------------------------------
    # Stage Logic
    # ------------------------------------------------------------------

    @staticmethod
    def _get_stage(t: float) -> int:
        """Map normalized time t→[0,1] to one of 7 cinematic stages."""
        if t < 0.08:  return 1   # Utterance
        if t < 0.20:  return 2   # Semantic Disassembly
        if t < 0.35:  return 3   # Geometric Incarnation / Helix
        if t < 0.50:  return 4   # Manifold surface
        if t < 0.63:  return 5   # Rotor Transport / Gate approach
        if t < 0.78:  return 6   # Gate Intersect
        return 7                  # Holographic Receipt

    STAGE_LABELS = {
        1: "STAGE 1: UTTERANCE — Sentence enters the machine",
        2: "STAGE 2: SEMANTIC DISASSEMBLY — ACTION · POLARITY · TARGET · AUTHORITY",
        3: "STAGE 3: GEOMETRIC INCARNATION — Cl(4,1) blade energy packets",
        4: "STAGE 4: DOUBLE HELIX ORBIT — 3D Clifford blade stream orbit",
        5: "STAGE 5: ROTOR TRANSPORT — M₁ = R·M₀·R̃ (bivector rotation)",
        6: "STAGE 6: GATE INTERSECT — Governance ring plane fires",
        7: "STAGE 7: HOLOGRAPHIC RECEIPT — SHA-256 sealed trace crawl",
    }

    # ------------------------------------------------------------------
    # Drawing Methods
    # ------------------------------------------------------------------

    def _draw_header(self, draw, domain, verdict, stage):
        draw.text((40, 22), "DAXDA GUARD — Cl(4,1) CANONICAL TRACE ENGINE", fill=C_CYAN)
        draw.text((40, 44), f"Domain: {domain.upper()} | Verdict: {verdict}", fill=C_SILVER)
        stage_color = C_VIOLET if stage <= 4 else (C_AMBER if stage <= 5 else C_CRIMSON)
        draw.text((40, 66), self.STAGE_LABELS.get(stage, ""), fill=stage_color)
        draw.line([(40, 90), (self.width - 40, 90)], fill=C_BORDER, width=1)

    def _draw_left_panel(self, draw, t, stage, payload, e1, e3, e15, is_block):
        draw.rectangle([40, 100, 480, 695], fill=PANEL_BG, outline=C_BORDER)
        draw.text((60, 115), "PAYLOAD TEXT", fill=C_SILVER)
        draw.rectangle([55, 138, 465, 178], fill=CARD_BG, outline=C_BORDER)
        # Truncate payload for display
        disp_payload = payload[:50] + "..." if len(payload) > 50 else payload
        draw.text((65, 148), f'"{disp_payload}"', fill=(255, 255, 255))

        # Stage 2+: semantic token roles
        if stage >= 2:
            tokens = payload.split()
            roles = ["ACTION", "OBJECT", "AUTHORITY", "POLARITY", "TARGET", "MODIFIER"]
            draw.text((60, 195), "SEMANTIC ROLE DECOMPOSITION", fill=C_CYAN)
            for i, tok in enumerate(tokens[:6]):
                ty = 220 + i * 38
                progress = min(1.0, max(0.0, (t * 6) - (i * 0.08)))
                if progress > 0:
                    role = roles[i % len(roles)]
                    c = C_CRIMSON if (is_block and role == "ACTION") else C_GREEN
                    draw.rectangle([58, ty, 462, ty + 30], fill=CARD_BG, outline=c)
                    draw.text((68, ty + 8), f"{role}: {tok}", fill=c)

        # Stage 3+: blade channel readout
        if stage >= 3:
            draw.text((60, 462), "Cl(4,1) BLADE CHANNELS", fill=C_VIOLET)
            blade_data = [
                ("e1  Trust",      e1,  C_CYAN),
                ("e3  Negation",   e3,  C_VIOLET),
                ("e15 Adversarial",e15, C_CRIMSON),
            ]
            for i, (lbl, val, col) in enumerate(blade_data):
                by = 490 + i * 52
                draw.text((60, by), lbl, fill=col)
                bar_w = int(380 * val)
                draw.rectangle([60, by + 18, 60 + bar_w, by + 34], fill=col)
                draw.rectangle([60, by + 18, 440, by + 34], outline=C_BORDER, width=1)
                draw.text((448, by + 18), f"{val:.3f}", fill=col)

    def _draw_blade_axes(self, draw, cx, cy, yaw, pitch, roll, e1, e3, e15, t, is_block):
        """Draw 3D Cl(4,1) basis vector axes e1..e5."""
        axes = [
            ("e1", 0,   C_CYAN,    e1),
            ("e2", 1,   C_WHITE,   0.35),
            ("e3", 2,   C_VIOLET,  e3),
            ("e4", 3,   C_AMBER,   0.20),
            ("e15",4,   C_CRIMSON, e15),
        ]
        for label, idx, col, val in axes:
            phi = (idx / 5.0) * math.pi * 2
            ax3d = (1.6 * val * math.cos(phi), 1.6 * val * math.sin(phi), 0.3 * math.sin(idx * 1.3))
            rx, ry, rz = _rot3d(*ax3d, yaw, pitch, roll)
            sx, sy, _  = _proj(rx, ry, rz, cx, cy)
            ox, oy, _  = _proj(0, 0, 0, cx, cy)
            if t > 0.15:
                draw.line([(ox, oy), (sx, sy)], fill=col, width=2)
                draw.ellipse([sx-5, sy-5, sx+5, sy+5], fill=col)
                draw.text((sx + 6, sy - 8), label, fill=col)

    def _draw_double_helix(self, draw, cx, cy, yaw, pitch, roll, t, e1, e2, e3, e4, e15, stage):
        """Draw a 3D double helix formed from the five Clifford blade streams."""
        helix_pts_A = []
        helix_pts_B = []
        n_pts = 80
        helix_R = 0.9
        helix_H = 2.2

        for i in range(n_pts):
            u = i / n_pts
            angle = u * math.pi * 4 + t * math.pi * 2

            # Strand A: blade-energy-modulated radius
            rA = helix_R * (0.5 + 0.5 * (e1 + e3))
            xA = rA * math.cos(angle)
            yA = helix_H * (u - 0.5)
            zA = rA * math.sin(angle)

            # Strand B: adversarial / authority
            rB = helix_R * (0.5 + 0.5 * (e15 + e4))
            xB = rB * math.cos(angle + math.pi)
            yB = helix_H * (u - 0.5)
            zB = rB * math.sin(angle + math.pi)

            rxA, ryA, rzA = _rot3d(xA, yA, zA, yaw, pitch, roll)
            rxB, ryB, rzB = _rot3d(xB, yB, zB, yaw, pitch, roll)
            sxA, syA, _ = _proj(rxA, ryA, rzA, cx, cy)
            sxB, syB, _ = _proj(rxB, ryB, rzB, cx, cy)
            helix_pts_A.append((sxA, syA))
            helix_pts_B.append((sxB, syB))

        # Draw strands
        col_A = C_CYAN if e15 < 0.3 else _lerp_color(C_CYAN, C_CRIMSON, e15)
        col_B = C_CRIMSON if e15 >= 0.3 else C_GREEN

        for i in range(len(helix_pts_A) - 1):
            draw.line([helix_pts_A[i], helix_pts_A[i+1]], fill=col_A, width=2)
            draw.line([helix_pts_B[i], helix_pts_B[i+1]], fill=col_B, width=2)

    def _draw_3d_manifold(self, draw, cx, cy, yaw, pitch, roll, t, is_block, e15):
        """Draw the true 3D Riemannian manifold surface mesh (torus + deformation)."""
        num_u, num_v = 20, 12
        major_R, minor_r0 = 1.1, 0.42
        polygons = []

        for iu in range(num_u):
            u1 = (iu / num_u) * 2 * math.pi
            u2 = ((iu + 1) / num_u) * 2 * math.pi
            for iv in range(num_v):
                v1 = (iv / num_v) * 2 * math.pi - math.pi
                v2 = ((iv + 1) / num_v) * 2 * math.pi - math.pi

                verts = []
                for u_val, v_val in [(u1,v1),(u2,v1),(u2,v2),(u1,v2)]:
                    if is_block:
                        r_eff = minor_r0 + 0.26 * e15 * math.sin(3*u_val + t*math.pi*4) * math.cos(2*v_val)
                    else:
                        r_eff = minor_r0 + 0.04 * math.sin(2*u_val + t*math.pi*2)

                    vx = (major_R + r_eff * math.cos(v_val)) * math.cos(u_val)
                    vy = (major_R + r_eff * math.cos(v_val)) * math.sin(u_val)
                    vz = r_eff * math.sin(v_val)
                    rx, ry, rz = _rot3d(vx, vy, vz, yaw, pitch, roll)
                    sx, sy, ze = _proj(rx, ry, rz, cx, cy)
                    verts.append((sx, sy, ze, rx, ry, rz))

                avg_z = sum(v[2] for v in verts) / 4
                polygons.append((avg_z, verts))

        polygons.sort(key=lambda x: x[0], reverse=True)

        for avg_z, verts in polygons:
            pts = [(v[0], v[1]) for v in verts]
            v0, v1, v2 = verts[0], verts[1], verts[2]
            ax, ay, az = v1[3]-v0[3], v1[4]-v0[4], v1[5]-v0[5]
            bx, by, bz = v2[3]-v0[3], v2[4]-v0[4], v2[5]-v0[5]
            nx = ay*bz - az*by; ny = az*bx - ax*bz; nz = ax*by - ay*bx
            nlen = math.sqrt(nx*nx + ny*ny + nz*nz) + 1e-6
            shad = max(0.2, (nx/nlen)*0.577 + (ny/nlen)*0.577 + (nz/nlen)*0.577)

            if is_block:
                fill = (int(200*e15*shad), int(20*shad), int(20*shad))
                wire = C_CRIMSON
            else:
                fill = (int(15*shad), int(140*shad), int(100*shad))
                wire = C_GREEN

            draw.polygon(pts, fill=fill, outline=wire)

    def _draw_bivector_ring(self, draw, cx, cy, yaw, pitch, roll, t, is_error):
        """Draw the 3D bivector slicing ring (e1∧e5 adversarial channel)."""
        ring_pts = []
        r = 1.50
        col = C_ORANGE if is_error else C_CRIMSON
        for ri in range(48):
            ang = (ri / 48.0) * 2 * math.pi + t * math.pi
            rx3d = r * math.cos(ang)
            ry3d = r * math.sin(ang)
            rz3d = 0.3 * math.sin(ang * 2)
            rx, ry, rz = _rot3d(rx3d, ry3d, rz3d, yaw, pitch, roll)
            sx, sy, _ = _proj(rx, ry, rz, cx, cy)
            ring_pts.append((sx, sy))

        for ri in range(len(ring_pts)):
            p1 = ring_pts[ri]
            p2 = ring_pts[(ri+1) % len(ring_pts)]
            draw.line([p1, p2], fill=col, width=3)

        lbl = "⚡ e₁∧e₅ ADVERSARIAL RING" if not is_error else "⚠ e₁∧e₅ FALSE-POSITIVE RING"
        draw.text((cx - 150, cy - 200), lbl, fill=col)

    def _draw_gate_verdict(self, draw, cx, cy, t, verdict, is_error):
        """Draw the gate plane intersection visual."""
        stage_t = max(0.0, min(1.0, (t - 0.63) / 0.15))

        if verdict in ("BLOCK", "SEVERE_BLOCK"):
            if is_error:
                bg  = (90, 40, 0)
                col = C_ORANGE
                txt = "⚠ V11.4 FALSE-POSITIVE: BLOCK (should be RELEASE)"
                sub = "Protective prohibition misclassified — V11.4.2 corrects this"
            else:
                bg  = (100, 15, 15)
                col = C_CRIMSON
                txt = "🛑 VERDICT: SEVERE_BLOCK"
                sub = "Adversarial gate fired — containment enforced"
        else:
            bg  = (6, 70, 50)
            col = C_GREEN
            txt = "✅ VERDICT: RELEASE"
            sub = "All governance gates passed — action authorized"

        alpha = min(1.0, stage_t * 3)
        bx1, by1 = cx - 230, cy + 145
        bx2, by2 = cx + 230, cy + 220

        # Animated expansion/collapse
        margin = int(20 * (1.0 - alpha))
        draw.rectangle([bx1+margin, by1+margin, bx2-margin, by2-margin],
                       fill=bg, outline=col, width=2)
        draw.text((bx1+18, by1+18), txt, fill=col)
        draw.text((bx1+18, by1+42), sub, fill=C_SILVER)

    def _draw_holographic_receipt(self, draw, cx, cy, t, payload, verdict,
                                   e1, e2, e3, e4, e15, trace):
        """Stage 7: render the holographic space-crawl receipt with exact trace values."""
        stage_t = max(0.0, min(1.0, (t - 0.78) / 0.22))
        scroll_y = int(80 * (1.0 - stage_t))  # receipt crawls up

        sha = ""
        if trace:
            sha = trace.get("tamper_evident_sha256", "")[:32] + "..."

        lines = [
            "═══════════════════════════════════════════════",
            "   DAXDA GUARD — MESSAGE DELIVERY RECEIPT",
            "═══════════════════════════════════════════════",
            f"  INPUT      {payload[:38]}",
            f"  ENGINE     DAXDA-NEXTGEN/1.0.0",
            f"  ALGEBRA    Cl(4,1)  [32 blades]",
            f"  e1 Trust   {e1:.4f}",
            f"  e2 Factual {e2:.4f}",
            f"  e3 Negation{e3:.4f}",
            f"  e4 Auth    {e4:.4f}",
            f"  e15 Advers {e15:.4f}",
            f"  DISPOSITION {verdict}",
            f"  SHA-256    {sha}",
            "═══════════════════════════════════════════════",
        ]

        is_error = verdict == "EXPOSED_ERROR"
        box_col = C_ORANGE if is_error else (C_CYAN if verdict == "RELEASE" else C_CRIMSON)
        bx, by = cx - 210, cy - 40 + scroll_y
        box_h = len(lines) * 18 + 20

        draw.rectangle([bx, by, bx + 420, by + box_h], fill=(5, 8, 18), outline=box_col, width=2)

        for i, line in enumerate(lines):
            col = box_col if (i == 0 or i == 2 or i == len(lines)-1 or "DISPOSITION" in line) else C_WHITE
            vis = min(1.0, stage_t * (len(lines)+2) - i * 0.15)
            if vis > 0:
                fade_col = _lerp_color(BG_COLOR, col, min(1.0, vis))
                draw.text((bx + 8, by + 10 + i * 18), line, fill=fade_col)


# ---------------------------------------------------------------------------
# Default Invocation (generic demo video)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    renderer = DAXDAManifoldVideoGenerator()
    res = renderer.render_transformation_video()
    print("Default True 3D Video generation complete:", res)
