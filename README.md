# eSim OpenROAD Design Flow Plugin

The **eSim OpenROAD Design Flow Plugin** integrates the **eSim** schematic capture and simulation environment with the **OpenROAD** physical design flow. It enables users to generate physical layouts (**GDSII**) from supported SPICE netlists (`.cir`) and RTL designs (`.v`/`.vhdl`) through a unified workflow powered by open-source EDA tools.

This project is designed for the FOSSEE eSim ecosystem and provides seamless integration with OpenROAD on Ubuntu-based systems.

## Features

- Integrates **eSim** with the **OpenROAD Flow Scripts (ORFS)** for digital ASIC design.
- Converts supported **`.cir`** netlists into **Verilog (`.v`)** automatically.
- Generates **GDSII (`.gds`)** layouts from **Verilog (`.v`)**, **VHDL (`.vhdl`)**, and **SDC (`.sdc`)** files using OpenROAD.
- Supports multiple OpenROAD-compatible **PDKs**, including **Sky130**, **IHP130**, **GF180**, and other supported technologies.
- Launches the **OpenROAD GUI** directly from the eSim interface.
- Opens generated or existing **GDSII (`.gds`)** files directly in **KLayout**.
- Provides an integrated GUI for managing the complete RTL-to-GDSII workflow.
- Supports opening and switching between multiple projects without restarting eSim.
- Includes **Start**, **Stop**, and **Clear** controls for managing OpenROAD execution and terminal logs.
- Displays real-time OpenROAD execution logs within the application.
- Provides Docker support for simplified installation and reproducible environments.
- Includes automated installation scripts for Ubuntu-based systems.
- Ships with example projects such as **Half Adder**, **Full Adder**.
- Includes helper scripts for OpenROAD setup, project generation, and plugin integration.

## Repository Structure

| Path | Description |
|------|-------------|
| `Examples/` | Sample eSim circuits and OpenROAD design examples. |
| `docker-launcher/` | Docker configuration and launcher scripts for eSim and OpenROAD. |
| `images/` | Images and screenshots used in the documentation. |
| `install-eSim-scripts/` | Supporting installation and dependency setup scripts. |
| `library/` | Device models, subcircuits, manuals, and bundled reference files. |
| `orfs/` | OpenROAD Flow Scripts (ORFS) and related resources. |
| `src/` | Python source code for eSim modules and OpenROAD integration. |
| `LICENSE` | Project license. |
| `README.md` | Project documentation and usage guide. |
| `contribution.md` | Contribution guidelines for developers. |
| `install-eSim.sh` | Main installation and uninstallation script. |
| `install.md` | Installation instructions and setup documentation. |
| `nghdl.zip` | NGHDL installation package and related resources. |

## Documentation

 For the complete installation and setup guide, see [`install.md`](install.md).

 For Docker installation and usage, see [`docker.md`](docker-launcher/README.md)

For contribution guidelines, see [`contribution.md`](contribution.md).

## License

This project is licensed under the terms of the [`GPL-3.0`](LICENSE).
