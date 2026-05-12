# eSim-to-OpenROAD Design Flow Plugin

> A complete integration bridge that connects **eSim** (schematic capture + mixed-signal simulation) with **OpenROAD** (RTL-to-GDSII physical design), enabling an end-to-end open-source EDA flow — from schematic to silicon layout.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Step 1: Install Docker](#step-1-install-docker)
  - [Step 2: Pull eSim Source](#step-2-pull-esim-source)
  - [Step 3: Switch to PR #473](#step-3-switch-to-pr-473)
  - [Step 4: Pull OpenROAD Flow Scripts](#step-4-pull-openroad-flow-scripts)
  - [Step 5: Launch eSim](#step-5-launch-esim)
- [What Was Modified](#what-was-modified)
- [How the Flow Works](#how-the-flow-works)
- [Examples Included](#examples-included)
- [Contributors](#contributors)

---

## Overview

This plugin extends eSim with a physical design pipeline by:

- Converting eSim-generated SPICE netlists (`.cir.out`) into OpenROAD-compatible structural Verilog
- Sanitizing net names to comply with Verilog IEEE 1364-2005 standards
- Generating a `mapping.json` to preserve translation between eSim logical nets and physical Verilog wires
- Adding an **"OpenROAD-GDSII"** button inside the eSim GUI to trigger the RTL-to-GDSII pipeline directly

---

## Prerequisites

Before starting, make sure you have the following installed:

| Tool | Version | Install Guide |
|------|---------|--------------|
| **Docker** | Latest | https://docs.docker.com/get-docker/ |
| **Git** | Any | `sudo apt install git` |
| **Ubuntu** | 22.04 | Recommended OS |

---

## Setup Instructions

### Step 1: Install Docker

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

> ⚠️ Log out and log back in after adding yourself to the docker group.

---

### Step 2: Pull eSim Source

Clone the main eSim repository:

```bash
git clone https://github.com/FOSSEE/eSim.git
cd eSim
```

---

### Step 3: Switch to PR #473

This PR contains the eSim-to-OpenROAD integration code:

```bash
git fetch origin pull/473/head:openroad-bridge
git checkout openroad-bridge
```

> PR #473 link: https://github.com/FOSSEE/eSim/pull/473  
> This branch includes all modified source files for the OpenROAD integration.

---

### Step 4: Pull OpenROAD Flow Scripts

Follow the official OpenROAD tutorial to set up the flow:

```bash
git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git
cd OpenROAD-flow-scripts
./build_openroad.sh --local
```

> 📖 Full tutorial: https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html

---

### Step 5: Launch eSim

After switching to the PR branch, launch eSim using the launcher script:

```bash
cd ~/eSim
bash scripts/launcher-esim.sh
```

This will start eSim with all the OpenROAD integration features enabled, including the **OpenROAD-GDSII** button in the GUI workspace.

---

## What Was Modified

The following files were added or modified as part of this integration:

### Source Files (`src/maker/`)

| File | Change |
|------|--------|
| `Maker.py` | Added OpenROAD flow trigger logic |
| `ModelGeneration.py` | Extended model generation for digital cells |
| `NgVeri.py` | Improved NgVeri to Verilog conversion |
| `createkicad.py` | Updated KiCad integration |
| `netlist_to_verilog.py` | Core script: converts SPICE netlist → OpenROAD Verilog |

### Scripts

| File | Change |
|------|--------|
| `scripts/launcher-esim.sh` | Updated launcher with OpenROAD environment setup |
| `scripts/setup-esim.sh` | Added OpenROAD dependency checks |
| `nghdl/install-nghdl-scripts/install-nghdl-22.04.sh` | Updated for Ubuntu 22.04 compatibility |

### Library Files

| File | Change |
|------|--------|
| `library/kicadLibrary/eSim-symbols/eSim_Ngveri.kicad_sym` | Added new symbols for digital flow |
| `library/modelParamXML/Ngveri/counter.xml` | New counter model |
| `library/modelParamXML/Ngveri/fulladder.xml` | New full adder model |
| `library/modelParamXML/Ngveri/halfwave_rectifier.xml` | New halfwave rectifier model |

### Docker

| File | Change |
|------|--------|
| `docker-launcher/Dockerfile` | Added OpenROAD installation stage |

### Examples

| Folder | Description |
|--------|-------------|
| `Examples/FullAdder/` | Full adder schematic + KiCad project with OpenROAD flow |
| `Examples/Half_Adder/` | Half adder with `.sdc`, `.v`, `config.mk` for OpenROAD |
| `Examples/counter/` | Counter circuit example |

---

## How the Flow Works

```text
eSim Schematic
      ↓
SPICE Netlist (.cir.out)
      ↓
netlist_to_verilog.py
      ↓
Structural Verilog (.v) + mapping.json
      ↓
OpenROAD Flow Scripts
      ↓
GDSII Layout
```

1. Design your circuit in eSim
2. Run simulation to generate the SPICE netlist
3. Click the **"OpenROAD-GDSII"** button in eSim GUI
4. The bridge script converts the netlist to Verilog automatically
5. OpenROAD picks it up and runs the RTL-to-GDSII flow

---

## Examples Included

### Half Adder

Located at `Examples/Half_Adder/`

- `Half_Adder.kicad_sch` — KiCad schematic
- `Half_Adder.v` — Generated Verilog
- `Half_Adder.sdc` — Timing constraints for OpenROAD
- `config.mk` — OpenROAD flow configuration

### Full Adder

Located at `Examples/FullAdder/`

- Complete KiCad project with rescue library
- Ready for OpenROAD physical design flow

---

## Contributors

| Name | Role |
|------|------|
| Adarsh Raj | OpenROAD Integration, Docker Setup, NgVeri modifications |
| Divinesoumyadip | OpenROAD bridge & GUI integration (PR #473) |
| FOSSEE Team, IIT Bombay | eSim core development |

---

## Links

- eSim Repository: https://github.com/FOSSEE/eSim
- PR #473: https://github.com/FOSSEE/eSim/pull/473
- OpenROAD Flow Tutorial: https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html
- Plugin Repository: https://github.com/FOSSEE/eSim-to-OpenROAD_Design_Flow_Plugin
