# eSim–OpenROAD Design Flow Plugin Installation Guide

**Platform:** Ubuntu 22.04

---

# 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/FOSSEE/eSim-to-OpenROAD_Design_Flow_Plugin.git
```

---

# 2. Move to the Project Directory

```bash
cd eSim-to-OpenROAD_Design_Flow_Plugin
```

---

# 3. Install eSim and Required Dependencies

Give execution permission to the installation script and run it:

```bash
chmod +x install-eSim.sh
./install-eSim.sh --install
```

This step installs:

- eSim
- OpenROAD dependencies
- Required tools and libraries

---

# 4. Build OpenROAD Flow Scripts Locally

Run the following command:

```bash
python3 orfs-setup.py
```

This command builds the OpenROAD Flow Scripts required for RTL-to-GDSII generation.

---

# 5. Rebuild OpenROAD Flow Scripts (If Build Fails)

If the build process fails:

1. Delete the existing `OpenROAD-flow-scripts` folder.
2. Run the build command again:

```bash
python3 orfs-setup.py
```

---

# Running the Tools

# 6. Run eSim

## Using Terminal

```bash
esim
```

## Using Desktop Shortcut

Double-click the **eSim** desktop icon.

---

# 7. Run OpenROAD GUI

```bash
cd ~/eSim/OpenROAD-flow-scripts/flow
openroad -gui
```

---

# 8. Run Yosys

```bash
yosys
```

---

# 9. Run KLayout

```bash
klayout
```

---

# 10. Uninstall eSim and All Components

```bash
./install-eSim.sh --uninstall
```

This removes eSim and all installed components from the system.

---

# Viewing Layouts in OpenROAD GUI

Start the OpenROAD GUI:

```bash
cd ~/eSim/OpenROAD-flow-scripts/flow
openroad -gui
```

---

## View Half Adder Layout

```tcl
read_lef platforms/sky130hd/lef/sky130_fd_sc_hd.tlef

read_lef platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef

read_def results/sky130hd/Half_Adder/base/6_final.def

gui::fit
```

---

## View Full Adder Layout

```tcl
read_lef platforms/sky130hd/lef/sky130_fd_sc_hd.tlef

read_lef platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef

read_def results/sky130hd/FullAdder/base/6_final.def

gui::fit
```

---

# Notes

- Recommended Operating System: **Ubuntu 22.04**
- Ensure Python 3 is installed before running the setup script.
- Internet connection is required during installation.
- Use terminal commands carefully with proper permissions.