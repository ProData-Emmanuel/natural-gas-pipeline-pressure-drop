# Natural Gas Pipeline Pressure Drop Analysis Using Python  
### A Computational Study of Gas Pipeline Hydraulics and Network Modeling

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen)

---

## 📌 Overview

This project presents a Python-based engineering framework for analyzing pressure drop in natural gas pipelines using classical gas flow equations. The implementation includes both single-pipeline analysis and complex pipeline network modeling involving series and parallel configurations.

The study integrates the **Weymouth equation** and **Panhandle B equation**, enabling comparative analysis across different pipeline conditions and providing insight into model behavior under transmission-line scenarios.

This project bridges classical gas pipeline engineering theory with modern computational analysis using Python.

---

## 🎯 Objectives

- Develop a computational tool for natural gas pipeline pressure drop analysis  
- Implement the Weymouth equation in field units  
- Extend analysis to pipeline networks (series and parallel systems)  
- Perform sensitivity analysis on key design parameters  
- Compare Weymouth and Panhandle B models  
- Provide engineering interpretation of results  

---

## ⚙️ Key Features

- ✅ Pressure drop calculation using Weymouth equation  
- ✅ Pipeline network modeling (series and parallel)  
- ✅ Flow distribution in parallel pipelines  
- ✅ Sensitivity analysis (flow rate, diameter, length)  
- ✅ Comparative modeling using Panhandle B  
- ✅ Visualization of engineering results  

---

## 🧪 Engineering Assumptions

The analysis is based on the following simplifying assumptions:

- Steady-state, single-phase gas flow  
- Fully turbulent flow regime  
- Isothermal conditions  
- Horizontal pipelines (no elevation effects)  
- Constant gas properties  
- Constant compressibility factor (Z)  

---

## 📐 Unit System

- Flow rate: MMSCFD (input/output)  
- Internal conversions:  
  - SCFH → Weymouth  
  - SCFD → Panhandle B  
- Pressure: psia  
- Diameter: inches  
- Length: miles  
- Temperature: °F (converted to Rankine)  

---

## 🧮 Mathematical Formulation

The analysis is based on the Weymouth equation and its pressure-squared formulation.

### Weymouth Equation

q_h = 18.062 (T_b / P_b) * [ ((P₁² − P₂²) D^(16/3)) / (γ_g T L Z) ]^(1/2)

---

### Pressure-Squared Form

P₁² − P₂² = [q_h² γ_g T Z L] / [(18.062)² (T_b / P_b)² D^(16/3)]

Defining:

R = L / D^(16/3)

Then:

Δ(P²) = [q_h² γ_g T Z R] / [(18.062)² (T_b / P_b)²]

---

### Parallel Pipeline Flow Distribution

q_i ∝ (D_i^(16/3) / L_i)^(1/2)

q_i = q_total × [ (D_i^(16/3) / L_i)^(1/2) ] / Σ [ (D_j^(16/3) / L_j)^(1/2) ]

---

### Series Pipeline Relationship

Δ(P²)_total = Σ Δ(P²)_i

---

## 🆚 Model Comparison

The project includes comparison between:

- **Weymouth Equation**  
- **Panhandle B Equation**

### Key Insight

- Weymouth generally predicts higher pressure drops → more conservative  
- Panhandle B predicts lower pressure losses for transmission conditions  

---

## 📁 Project Structure

```bash
natural-gas-pipeline-pressure-drop/
│
├── .streamlit/
│   └── config.toml
├── notebooks/
│   └── pipeline_pressure_drop.ipynb
├── results/
│   └── plots/
├── README.md
├── requirements.txt
└── streamlit_app.py


## 🧑‍💻 Author

**Emmanuel S. Okeke**  
M.Eng Gas Engineering | Pipeline Hydraulics | Energy Systems  