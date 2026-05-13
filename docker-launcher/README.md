# eSim-to-OpenROAD Design Flow Plugin

> A complete integration bridge that connects **eSim** (schematic capture + mixed-signal simulation) with **OpenROAD** (RTL-to-GDSII physical design), enabling an end-to-end open-source EDA flow — from schematic to silicon layout.

---

## Prerequisites

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

### Step 2: Pull eSim Source
```bash
git clone https://github.com/FOSSEE/eSim.git
cd eSim
```

### Step 3: Switch to PR #473
```bash
git fetch origin pull/473/head:openroad-bridge
git checkout openroad-bridge
```
> PR #473: https://github.com/FOSSEE/eSim/pull/473

### Step 4: Pull OpenROAD Flow Scripts
```bash
git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git
cd OpenROAD-flow-scripts
./build_openroad.sh --local
```
> Full tutorial: https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html

### Step 5: Launch eSim
```bash
cd ~/eSim
bash scripts/launcher-esim.sh
```

### Step 6: Build Docker Image
```bash
cd docker-launcher
docker build -t esim-openroad:latest .
docker run -it esim-openroad:latest
```

---

## What Was Modified

### Source Files (src/maker/)
| File | Change |
|------|--------|
| Maker.py | Added OpenROAD flow trigger logic |
| ModelGeneration.py | Extended model generation for digital cells |
| NgVeri.py | Improved NgVeri to Verilog conversion |
| createkicad.py | Updated KiCad integration |
| netlist_to_verilog.py | Core script: converts SPICE netlist to OpenROAD Verilog |
| OpenROAD.py | OpenROAD bridge module |

### Scripts
| File | Change |
|------|--------|
| scripts/launcher-esim.sh | Updated launcher with OpenROAD environment setup |
| scripts/setup-esim.sh | Added OpenROAD dependency checks |
| nghdl/install-nghdl-scripts/install-nghdl-22.04.sh | Updated for Ubuntu 22.04 |

### Library Files
| File | Change |
|------|--------|
| library/kicadLibrary/eSim-symbols/eSim_Ngveri.kicad_sym | Added new symbols for digital flow |
| library/modelParamXML/Ngveri/counter.xml | New counter model |
| library/modelParamXML/Ngveri/fulladder.xml | New full adder model |
| library/modelParamXML/Ngveri/halfwave_rectifier.xml | New halfwave rectifier model |

### Docker
| File | Change |
|------|--------|
| Dockerfile | Added OpenROAD installation stage |

### Examples
| Folder | Description |
|--------|-------------|
| Examples/FullAdder/ | Full adder schematic + KiCad project with OpenROAD flow |
| Examples/Half_Adder/ | Half adder with .sdc, .v, config.mk for OpenROAD |
| Examples/counter/ | Counter circuit example |

---

## How the Flow Workscat > ~/eSim-to-OpenROAD_Design_Flow_Plugin/docker-launcher/README.md << 'EOF'
# eSim-to-OpenROAD Design Flow Plugin

> A complete integration bridge that connects **eSim** (schematic capture + mixed-signal simulation) with **OpenROAD** (RTL-to-GDSII physical design), enabling an end-to-end open-source EDA flow — from schematic to silicon layout.

---

## Prerequisites

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

### Step 2: Pull eSim Source
```bash
git clone https://github.com/FOSSEE/eSim.git
cd eSim
```

### Step 3: Switch to PR #473
```bash
git fetch origin pull/473/head:openroad-bridge
git checkout openroad-bridge
```
> PR #473: https://github.com/FOSSEE/eSim/pull/473

### Step 4: Pull OpenROAD Flow Scripts
```bash
git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git
cd OpenROAD-flow-scripts
./build_openroad.sh --local
```
> Full tutorial: https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html

### Step 5: Launch eSim
```bash
cd ~/eSim
bash scripts/launcher-esim.sh
```

### Step 6: Build Docker Image
```bash
cd docker-launcher
docker build -t esim-openroad:latest .
docker run -it esim-openroad:latest
```

---

## What Was Modified

### Source Files (src/maker/)
| File | Change |
|------|--------|
| Maker.py | Added OpenROAD flow trigger logic |
| ModelGeneration.py | Extended model generation for digital cells |
| NgVeri.py | Improved NgVeri to Verilog conversion |
| createkicad.py | Updated KiCad integration |
| netlist_to_verilog.py | Core script: converts SPICE netlist to OpenROAD Verilog |
| OpenROAD.py | OpenROAD bridge module |

### Scripts
| File | Change |
|------|--------|
| scripts/launcher-esim.sh | Updated launcher with OpenROAD environment setup |
| scripts/setup-esim.sh | Added OpenROAD dependency checks |
| nghdl/install-nghdl-scripts/install-nghdl-22.04.sh | Updated for Ubuntu 22.04 |

### Library Files
| File | Change |
|------|--------|
| library/kicadLibrary/eSim-symbols/eSim_Ngveri.kicad_sym | Added new symbols for digital flow |
| library/modelParamXML/Ngveri/counter.xml | New counter model |
| library/modelParamXML/Ngveri/fulladder.xml | New full adder model |
| library/modelParamXML/Ngveri/halfwave_rectifier.xml | New halfwave rectifier model |

### Docker
| File | Change |
|------|--------|
| Dockerfile | Added OpenROAD installation stage |

### Examples
| Folder | Description |
|--------|-------------|
| Examples/FullAdder/ | Full adder schematic + KiCad project with OpenROAD flow |
| Examples/Half_Adder/ | Half adder with .sdc, .v, config.mk for OpenROAD |
| Examples/counter/ | Counter circuit example |

---

## How the Flow Works---

## Contributors

| Name | Role |
|------|------|
| Adarsh Raj | Docker Setup, OpenROAD Integration, NgVeri modifications |
| Divinesoumyadip | OpenROAD bridge and GUI integration (PR #473) |
| FOSSEE Team, IIT Bombay | eSim core development |

---

## Links

- eSim Repository: https://github.com/FOSSEE/eSim
- PR #473: https://github.com/FOSSEE/eSim/pull/473
- OpenROAD Flow Tutorial: https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html
- Plugin Repository: https://github.com/FOSSEE/eSim-to-OpenROAD_Design_Flow_Plugin
