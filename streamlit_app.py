import math
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Natural Gas Pipeline Pressure Drop App",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CUSTOM STYLING
# =========================================================
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 1rem;
        }
        .small-note {
            font-size: 0.9rem;
            color: #6b7280;
        }
        .info-box {
            padding: 0.9rem 1rem;
            border-radius: 0.8rem;
            background-color: #f8fafc;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CONSTANTS
# =========================================================
WEYMOUTH_CONSTANT_SCFH = 18.062


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def validate_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero. Got {value}.")


def fahrenheit_to_rankine(temp_f: float) -> float:
    return temp_f + 460.0


def flow_to_scfh(flow_value: float, flow_unit: str) -> float:
    validate_positive(flow_value, "Flow rate")
    flow_unit = flow_unit.strip().upper()

    if flow_unit == "SCFH":
        return flow_value
    if flow_unit == "SCFD":
        return flow_value / 24
    if flow_unit == "MMSCFD":
        return flow_value * 1_000_000 / 24

    raise ValueError("Unsupported flow unit. Use 'SCFH', 'SCFD', or 'MMSCFD'.")


def flow_to_scfd(flow_value: float, flow_unit: str) -> float:
    validate_positive(flow_value, "Flow rate")
    flow_unit = flow_unit.strip().upper()

    if flow_unit == "SCFH":
        return flow_value * 24
    if flow_unit == "SCFD":
        return flow_value
    if flow_unit == "MMSCFD":
        return flow_value * 1_000_000

    raise ValueError("Unsupported flow unit. Use 'SCFH', 'SCFD', or 'MMSCFD'.")


def safe_weymouth_pressure_drop(
    flow_value: float,
    P1: float,
    D: float,
    L: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    Tb_f: float = 60.0,
    Pb: float = 14.7,
):
    try:
        return weymouth_pressure_drop(flow_value, P1, D, L, G, T_f, Z, flow_unit, Tb_f, Pb)
    except Exception:
        return np.nan, np.nan


def safe_panhandle_b_pressure_drop(
    flow_value: float,
    P1: float,
    D: float,
    L: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    E: float = 0.95,
    Tb_f: float = 60.0,
    Pb: float = 14.7,
):
    try:
        return panhandle_b_pressure_drop(flow_value, P1, D, L, G, T_f, Z, flow_unit, E, Tb_f, Pb)
    except Exception:
        return np.nan, np.nan


# =========================================================
# WEYMOUTH FUNCTIONS
# =========================================================
def weymouth_outlet_pressure(
    flow_value: float,
    P1: float,
    D: float,
    L: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    Tb_f: float = 60.0,
    Pb: float = 14.7,
) -> float:
    validate_positive(P1, "Inlet pressure P1")
    validate_positive(D, "Diameter D")
    validate_positive(L, "Length L")
    validate_positive(G, "Gas specific gravity G")
    validate_positive(Z, "Compressibility factor Z")
    validate_positive(Pb, "Base pressure Pb")

    q_h = flow_to_scfh(flow_value, flow_unit)
    T = fahrenheit_to_rankine(T_f)
    Tb = fahrenheit_to_rankine(Tb_f)

    denominator = (WEYMOUTH_CONSTANT_SCFH ** 2) * ((Tb / Pb) ** 2) * (D ** (16 / 3))
    delta_p_squared_term = (q_h ** 2 * G * T * L * Z) / denominator
    P2_squared = P1 ** 2 - delta_p_squared_term

    if P2_squared <= 0:
        raise ValueError(
            "Calculated P2² is zero or negative. "
            "The selected flow may be too high for the given pipeline conditions."
        )

    return math.sqrt(P2_squared)


def weymouth_pressure_drop(
    flow_value: float,
    P1: float,
    D: float,
    L: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    Tb_f: float = 60.0,
    Pb: float = 14.7,
) -> Tuple[float, float]:
    P2 = weymouth_outlet_pressure(
        flow_value=flow_value,
        P1=P1,
        D=D,
        L=L,
        G=G,
        T_f=T_f,
        Z=Z,
        flow_unit=flow_unit,
        Tb_f=Tb_f,
        Pb=Pb,
    )
    delta_p = P1 - P2
    return P2, delta_p


# =========================================================
# PANHANDLE B FUNCTIONS
# =========================================================
def panhandle_b_outlet_pressure(
    flow_value: float,
    P1: float,
    D: float,
    L: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    E: float = 0.95,
    Tb_f: float = 60.0,
    Pb: float = 14.7,
) -> float:
    validate_positive(P1, "Inlet pressure P1")
    validate_positive(D, "Diameter D")
    validate_positive(L, "Length L")
    validate_positive(G, "Gas specific gravity G")
    validate_positive(Z, "Compressibility factor Z")
    validate_positive(E, "Pipeline efficiency E")
    validate_positive(Pb, "Base pressure Pb")

    Q = flow_to_scfd(flow_value, flow_unit)
    T = fahrenheit_to_rankine(T_f)
    Tb = fahrenheit_to_rankine(Tb_f)

    coefficient = 737 * E * ((Tb / Pb) ** 1.02) * (D ** 2.53)
    bracket_term = (Q / coefficient) ** (1 / 0.51)
    delta_p_squared_term = bracket_term * (G ** 0.961) * T * L * Z
    P2_squared = P1 ** 2 - delta_p_squared_term

    if P2_squared <= 0:
        raise ValueError(
            "Calculated P2² is zero or negative. "
            "The selected flow may be too high for the given pipeline conditions."
        )

    return math.sqrt(P2_squared)


def panhandle_b_pressure_drop(
    flow_value: float,
    P1: float,
    D: float,
    L: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    E: float = 0.95,
    Tb_f: float = 60.0,
    Pb: float = 14.7,
) -> Tuple[float, float]:
    P2 = panhandle_b_outlet_pressure(
        flow_value=flow_value,
        P1=P1,
        D=D,
        L=L,
        G=G,
        T_f=T_f,
        Z=Z,
        flow_unit=flow_unit,
        E=E,
        Tb_f=Tb_f,
        Pb=Pb,
    )
    delta_p = P1 - P2
    return P2, delta_p


# =========================================================
# NETWORK FUNCTIONS
# =========================================================
def equivalent_parallel_resistance(lengths: List[float], diameters: List[float]) -> float:
    if len(lengths) != len(diameters):
        raise ValueError("Lengths and diameters must have the same number of elements.")

    conductance_sum = 0.0
    for L, D in zip(lengths, diameters):
        validate_positive(L, "Length")
        validate_positive(D, "Diameter")
        conductance_sum += ((D ** (16 / 3)) / L) ** 0.5

    if conductance_sum <= 0:
        raise ValueError("Equivalent conductance sum must be positive.")

    return 1 / (conductance_sum ** 2)


def parallel_branch_factor(L: float, D: float) -> float:
    validate_positive(L, "Length")
    validate_positive(D, "Diameter")
    return ((D ** (16 / 3)) / L) ** 0.5


def split_parallel_flow(total_flow: float, lengths: List[float], diameters: List[float]) -> Tuple[List[float], List[float]]:
    if len(lengths) != len(diameters):
        raise ValueError("Lengths and diameters must have the same number of elements.")

    factors = [parallel_branch_factor(L, D) for L, D in zip(lengths, diameters)]
    factor_sum = sum(factors)
    flows = [total_flow * f / factor_sum for f in factors]
    return factors, flows


def weymouth_pressure_squared_drop(
    flow_value: float,
    resistance_term: float,
    G: float,
    T_f: float,
    Z: float,
    flow_unit: str = "MMSCFD",
    Tb_f: float = 60.0,
    Pb: float = 14.7,
) -> float:
    q_h = flow_to_scfh(flow_value, flow_unit)
    T = fahrenheit_to_rankine(T_f)
    Tb = fahrenheit_to_rankine(Tb_f)
    denominator = (WEYMOUTH_CONSTANT_SCFH ** 2) * ((Tb / Pb) ** 2)
    return (q_h ** 2 * G * T * Z * resistance_term) / denominator


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("App Guide")
    st.markdown(
        """
- **Single Pipeline Calculator**: compute outlet pressure and pressure drop  
- **Model Comparison**: compare Weymouth and Panhandle B  
- **Network Case Study**: solve the series-parallel pipeline system  
- **Sensitivity Analysis**: study parameter effects visually  
"""
    )
    st.markdown(
        '<div class="small-note">Tip: use MMSCFD for a cleaner engineering workflow.</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="main-title">⛽ Natural Gas Pipeline Pressure Drop Analysis App</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Interactive pipeline analysis using Weymouth and Panhandle B correlations, plus a network case study and sensitivity analysis.</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Single Pipeline Calculator", "Model Comparison", "Network Case Study", "Sensitivity Analysis"]
)

# =========================================================
# TAB 1: SINGLE PIPELINE CALCULATOR
# =========================================================
with tab1:
    st.subheader("Single Pipeline Calculator")

    left, right = st.columns(2)

    with left:
        model = st.selectbox("Select Model", ["Weymouth", "Panhandle B"])
        flow_value = st.number_input("Flow Rate", min_value=0.001, value=50.0)
        flow_unit = st.selectbox("Flow Unit", ["MMSCFD", "SCFD", "SCFH"])
        P1 = st.number_input("Inlet Pressure, P1 (psia)", min_value=0.001, value=1000.0)
        D = st.number_input("Diameter, D (inches)", min_value=0.001, value=12.0)

    with right:
        L = st.number_input("Length, L (miles)", min_value=0.001, value=20.0)
        G = st.number_input("Gas Specific Gravity, G", min_value=0.001, value=0.60)
        T_f = st.number_input("Temperature (°F)", value=60.0)
        Z = st.number_input("Compressibility Factor, Z", min_value=0.001, value=0.90)
        E = st.number_input("Pipeline Efficiency, E (Panhandle B only)", min_value=0.001, max_value=1.0, value=0.95)

    if st.button("Calculate Pressure Drop", use_container_width=True):
        try:
            if model == "Weymouth":
                P2, dP = weymouth_pressure_drop(flow_value, P1, D, L, G, T_f, Z, flow_unit)
            else:
                P2, dP = panhandle_b_pressure_drop(flow_value, P1, D, L, G, T_f, Z, flow_unit, E)

            m1, m2 = st.columns(2)
            m1.metric("Outlet Pressure (psia)", f"{P2:,.3f}")
            m2.metric("Pressure Drop (psi)", f"{dP:,.3f}")

            results_df = pd.DataFrame({
                "Quantity": ["Outlet Pressure, P2", "Pressure Drop, ΔP"],
                "Value": [P2, dP],
                "Unit": ["psia", "psi"],
            })
            st.dataframe(results_df, use_container_width=True)

            # Local mini sensitivity around chosen flow
            flow_min = max(1.0, flow_value * 0.5)
            flow_max = max(flow_min + 1.0, flow_value * 1.5)
            local_flow = np.linspace(flow_min, flow_max, 10)
            local_dP = []

            for q in local_flow:
                if model == "Weymouth":
                    _, dP_temp = safe_weymouth_pressure_drop(q, P1, D, L, G, T_f, Z, flow_unit)
                else:
                    _, dP_temp = safe_panhandle_b_pressure_drop(q, P1, D, L, G, T_f, Z, flow_unit, E)
                local_dP.append(dP_temp)

            local_df = pd.DataFrame({
                "Flow Rate": local_flow,
                "Pressure Drop": local_dP,
            }).dropna()

            if not local_df.empty:
                fig, ax = plt.subplots(figsize=(8, 4.5))
                ax.plot(local_df["Flow Rate"], local_df["Pressure Drop"], marker="o")
                ax.set_title("Local Flow Sensitivity")
                ax.set_xlabel(f"Flow Rate ({flow_unit})")
                ax.set_ylabel("Pressure Drop (psi)")
                ax.grid(True)
                st.pyplot(fig)

        except Exception as exc:
            st.error(str(exc))


# =========================================================
# TAB 2: MODEL COMPARISON
# =========================================================
with tab2:
    st.subheader("Weymouth vs Panhandle B Comparison")

    c1, c2, c3 = st.columns(3)
    with c1:
        comp_flow_min = st.number_input("Minimum Flow Rate (MMSCFD)", min_value=1.0, value=10.0, key="cmp_fmin")
    with c2:
        comp_flow_max = st.number_input("Maximum Flow Rate (MMSCFD)", min_value=2.0, value=100.0, key="cmp_fmax")
    with c3:
        comp_points = st.number_input("Number of Points", min_value=3, value=10, key="cmp_pts")

    c4, c5, c6 = st.columns(3)
    with c4:
        comp_P1 = st.number_input("Inlet Pressure (psia)", min_value=0.001, value=1000.0, key="cmp_p1")
        comp_D = st.number_input("Diameter (inches)", min_value=0.001, value=12.0, key="cmp_d")
    with c5:
        comp_L = st.number_input("Length (miles)", min_value=0.001, value=20.0, key="cmp_l")
        comp_G = st.number_input("Gas Specific Gravity", min_value=0.001, value=0.60, key="cmp_g")
    with c6:
        comp_T = st.number_input("Temperature (°F)", value=60.0, key="cmp_t")
        comp_Z = st.number_input("Compressibility Factor", min_value=0.001, value=0.90, key="cmp_z")
        comp_E = st.number_input("Panhandle B Efficiency", min_value=0.001, max_value=1.0, value=0.95, key="cmp_e")

    if st.button("Generate Comparison", use_container_width=True):
        try:
            flow_rates = np.linspace(comp_flow_min, comp_flow_max, int(comp_points))
            rows = []

            for q in flow_rates:
                _, dP_w = safe_weymouth_pressure_drop(q, comp_P1, comp_D, comp_L, comp_G, comp_T, comp_Z, "MMSCFD")
                _, dP_pb = safe_panhandle_b_pressure_drop(q, comp_P1, comp_D, comp_L, comp_G, comp_T, comp_Z, "MMSCFD", comp_E)

                rows.append({
                    "Flow Rate (MMSCFD)": q,
                    "Weymouth Pressure Drop (psi)": dP_w,
                    "Panhandle B Pressure Drop (psi)": dP_pb,
                })

            comp_df = pd.DataFrame(rows).dropna()
            st.dataframe(comp_df, use_container_width=True)

            col_plot1, col_plot2 = st.columns(2)

            with col_plot1:
                fig1, ax1 = plt.subplots(figsize=(7, 4.5))
                ax1.plot(comp_df["Flow Rate (MMSCFD)"], comp_df["Weymouth Pressure Drop (psi)"], marker="o", label="Weymouth")
                ax1.plot(comp_df["Flow Rate (MMSCFD)"], comp_df["Panhandle B Pressure Drop (psi)"], marker="s", label="Panhandle B")
                ax1.set_xlabel("Flow Rate (MMSCFD)")
                ax1.set_ylabel("Pressure Drop (psi)")
                ax1.set_title("Pressure Drop Comparison")
                ax1.grid(True)
                ax1.legend()
                st.pyplot(fig1)

            with col_plot2:
                difference = comp_df["Weymouth Pressure Drop (psi)"] - comp_df["Panhandle B Pressure Drop (psi)"]
                fig2, ax2 = plt.subplots(figsize=(7, 4.5))
                ax2.plot(comp_df["Flow Rate (MMSCFD)"], difference, marker="d")
                ax2.set_xlabel("Flow Rate (MMSCFD)")
                ax2.set_ylabel("Difference in Pressure Drop (psi)")
                ax2.set_title("Weymouth − Panhandle B")
                ax2.grid(True)
                st.pyplot(fig2)

            csv = comp_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Comparison Results (CSV)",
                data=csv,
                file_name="weymouth_panhandle_comparison.csv",
                mime="text/csv",
                use_container_width=True,
            )

        except Exception as exc:
            st.error(str(exc))


# =========================================================
# TAB 3: NETWORK CASE STUDY
# =========================================================
with tab3:
    st.subheader("Series-Parallel Network Case Study")

    st.markdown(
        """
This case uses the same network structure from the notebook:
- two parallel lines in section **AB**
- three parallel lines in section **BC**
"""
    )

    n1, n2, n3 = st.columns(3)
    with n1:
        total_flow = st.number_input("Total Flow (MMSCFD)", min_value=0.001, value=50.0, key="net_flow")
    with n2:
        P_C = st.number_input("Pressure at Node C (psia)", min_value=0.001, value=50.0, key="net_pc")
    with n3:
        G_case = st.number_input("Gas Specific Gravity", min_value=0.001, value=0.60, key="net_g")

    n4, n5 = st.columns(2)
    with n4:
        T_case = st.number_input("Temperature (°F)", value=60.0, key="net_t")
    with n5:
        Z_case = st.number_input("Compressibility Factor", min_value=0.001, value=0.90, key="net_z")

    if st.button("Solve Network Case", use_container_width=True):
        try:
            AB_lengths = [20.0, 25.0]
            AB_diameters = [8.0, 10.0]
            BC_lengths = [30.0, 35.0, 40.0]
            BC_diameters = [12.0, 8.0, 10.0]

            AB_labels = ["20-mile, 8-in", "25-mile, 10-in"]
            BC_labels = ["30-mile, 12-in", "35-mile, 8-in", "40-mile, 10-in"]

            AB_factors, AB_flows = split_parallel_flow(total_flow, AB_lengths, AB_diameters)
            BC_factors, BC_flows = split_parallel_flow(total_flow, BC_lengths, BC_diameters)

            R_AB = equivalent_parallel_resistance(AB_lengths, AB_diameters)
            R_BC = equivalent_parallel_resistance(BC_lengths, BC_diameters)
            R_AC = R_AB + R_BC

            delta_AB = weymouth_pressure_squared_drop(total_flow, R_AB, G_case, T_case, Z_case, "MMSCFD")
            delta_BC = weymouth_pressure_squared_drop(total_flow, R_BC, G_case, T_case, Z_case, "MMSCFD")
            delta_AC = delta_AB + delta_BC

            P_B = math.sqrt(P_C ** 2 + delta_BC)
            P_A = math.sqrt(P_C ** 2 + delta_AC)

            m1, m2, m3 = st.columns(3)
            m1.metric("Pressure at A (psia)", f"{P_A:,.3f}")
            m2.metric("Pressure at B (psia)", f"{P_B:,.3f}")
            m3.metric("Pressure at C (psia)", f"{P_C:,.3f}")

            node_df = pd.DataFrame({
                "Node": ["A", "B", "C"],
                "Pressure (psia)": [P_A, P_B, P_C],
            })

            ab_df = pd.DataFrame({
                "AB Branch": AB_labels,
                "Branch Factor": AB_factors,
                "Flow Split (MMSCFD)": AB_flows,
            })

            bc_df = pd.DataFrame({
                "BC Branch": BC_labels,
                "Branch Factor": BC_factors,
                "Flow Split (MMSCFD)": BC_flows,
            })

            st.markdown("### Node Pressures")
            st.dataframe(node_df, use_container_width=True)

            left_df, right_df = st.columns(2)
            with left_df:
                st.markdown("### Flow Split in Section AB")
                st.dataframe(ab_df, use_container_width=True)

            with right_df:
                st.markdown("### Flow Split in Section BC")
                st.dataframe(bc_df, use_container_width=True)

            fig3, ax3 = plt.subplots(figsize=(8, 4.5))
            ax3.bar(node_df["Node"], node_df["Pressure (psia)"])
            ax3.set_xlabel("Node")
            ax3.set_ylabel("Pressure (psia)")
            ax3.set_title("Node Pressures in the Network")
            ax3.grid(axis="y")
            st.pyplot(fig3)

        except Exception as exc:
            st.error(str(exc))


# =========================================================
# TAB 4: SENSITIVITY ANALYSIS
# =========================================================
with tab4:
    st.subheader("Sensitivity Analysis")

    st.markdown("Explore how pressure drop changes with flow rate, diameter, and length.")

    s1, s2 = st.columns(2)
    with s1:
        sens_model = st.selectbox("Model for Sensitivity", ["Weymouth", "Panhandle B"])
        sens_P1 = st.number_input("Inlet Pressure (psia)", value=1000.0, key="sens_p1")
        sens_D = st.number_input("Base Diameter (inches)", value=12.0, key="sens_d")
        sens_L = st.number_input("Base Length (miles)", value=20.0, key="sens_l")

    with s2:
        sens_G = st.number_input("Gas Specific Gravity", value=0.60, key="sens_g")
        sens_T = st.number_input("Temperature (°F)", value=60.0, key="sens_t")
        sens_Z = st.number_input("Compressibility Factor", value=0.90, key="sens_z")
        sens_E = st.number_input("Panhandle B Efficiency", min_value=0.001, max_value=1.0, value=0.95, key="sens_e")

    if st.button("Generate Sensitivity Plots", use_container_width=True):
        try:
            # Flow sensitivity
            flow_range = np.linspace(10, 100, 10)
            flow_rows = []
            for q in flow_range:
                if sens_model == "Weymouth":
                    P2, dP = safe_weymouth_pressure_drop(q, sens_P1, sens_D, sens_L, sens_G, sens_T, sens_Z, "MMSCFD")
                else:
                    P2, dP = safe_panhandle_b_pressure_drop(q, sens_P1, sens_D, sens_L, sens_G, sens_T, sens_Z, "MMSCFD", sens_E)

                flow_rows.append({
                    "Flow Rate (MMSCFD)": q,
                    "Outlet Pressure (psia)": P2,
                    "Pressure Drop (psi)": dP,
                })
            flow_df = pd.DataFrame(flow_rows).dropna()

            # Diameter sensitivity
            diameter_range = np.linspace(8, 24, 9)
            diameter_rows = []
            for d in diameter_range:
                if sens_model == "Weymouth":
                    P2, dP = safe_weymouth_pressure_drop(50.0, sens_P1, d, sens_L, sens_G, sens_T, sens_Z, "MMSCFD")
                else:
                    P2, dP = safe_panhandle_b_pressure_drop(50.0, sens_P1, d, sens_L, sens_G, sens_T, sens_Z, "MMSCFD", sens_E)

                diameter_rows.append({
                    "Diameter (inches)": d,
                    "Outlet Pressure (psia)": P2,
                    "Pressure Drop (psi)": dP,
                })
            diameter_df = pd.DataFrame(diameter_rows).dropna()

            # Length sensitivity
            length_range = np.linspace(5, 60, 12)
            length_rows = []
            for l in length_range:
                if sens_model == "Weymouth":
                    P2, dP = safe_weymouth_pressure_drop(50.0, sens_P1, sens_D, l, sens_G, sens_T, sens_Z, "MMSCFD")
                else:
                    P2, dP = safe_panhandle_b_pressure_drop(50.0, sens_P1, sens_D, l, sens_G, sens_T, sens_Z, "MMSCFD", sens_E)

                length_rows.append({
                    "Length (miles)": l,
                    "Outlet Pressure (psia)": P2,
                    "Pressure Drop (psi)": dP,
                })
            length_df = pd.DataFrame(length_rows).dropna()

            pcol1, pcol2 = st.columns(2)

            with pcol1:
                fig1, ax1 = plt.subplots(figsize=(7, 4.5))
                ax1.plot(flow_df["Flow Rate (MMSCFD)"], flow_df["Pressure Drop (psi)"], marker="o")
                ax1.set_xlabel("Flow Rate (MMSCFD)")
                ax1.set_ylabel("Pressure Drop (psi)")
                ax1.set_title(f"{sens_model}: Sensitivity to Flow Rate")
                ax1.grid(True)
                st.pyplot(fig1)

            with pcol2:
                fig2, ax2 = plt.subplots(figsize=(7, 4.5))
                ax2.plot(diameter_df["Diameter (inches)"], diameter_df["Pressure Drop (psi)"], marker="s")
                ax2.set_xlabel("Diameter (inches)")
                ax2.set_ylabel("Pressure Drop (psi)")
                ax2.set_title(f"{sens_model}: Sensitivity to Diameter")
                ax2.grid(True)
                st.pyplot(fig2)

            fig3, ax3 = plt.subplots(figsize=(8, 4.5))
            ax3.plot(length_df["Length (miles)"], length_df["Pressure Drop (psi)"], marker="^")
            ax3.set_xlabel("Length (miles)")
            ax3.set_ylabel("Pressure Drop (psi)")
            ax3.set_title(f"{sens_model}: Sensitivity to Length")
            ax3.grid(True)
            st.pyplot(fig3)

            st.markdown("### Sensitivity Data Tables")
            st.dataframe(flow_df, use_container_width=True)
            st.dataframe(diameter_df, use_container_width=True)
            st.dataframe(length_df, use_container_width=True)

        except Exception as exc:
            st.error(str(exc))