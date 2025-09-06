# 💧 Sprinkler Distribution Evaluator

A PyQt5-based tool to **visualize, evaluate, and analyze sprinkler distribution** over irrigation zones. It provides 3D surface plots, uniformity metrics, and CSV export for detailed evaluation.

---

## Features

- Define **zone dimensions** and **sprinkler configurations** (triangle or rectangle).
- Import **measured Pr values** from CSV files of **x, y, Pr** columns.
- View and modify **measured Pr values** in an **interactive grid**, providing a more intuitive interface than standard CSV tables for quick adjustments and visualization.
- **3D visualization** of sprinkler distribution using Matplotlib.
- **Metrics calculation**:
  - Christiansen Uniformity (CU)
  - Distribution Uniformity (DU)
- Export configuration and Pr tables as CSV.
- Keyboard-controlled **3D plot rotation** (W/A/S/D + Shift for finer control).
- Adjustable **resolution** for simulations.

---

## Screenshots

*(Interactive 3D sprinkler distribution)*

![Screenshot](https://github.com/m-behery/sprinkler-distribution-evaluator/blob/main/gui/screenshots/screenshot.png)

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/m-behery/sprinkler-distribution-evaluator.git
cd sprinkler-distribution-evaluator
````

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate   # Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

*Dependencies may include: `PyQt5`, `numpy`, `pandas`, `matplotlib`.*

---

## Usage

```bash
python main.py
```

1. Set **zone dimensions** (width and height in meters).
2. Select **sprinkler configuration** (triangle or rectangle) and define dimensions.
3. Adjust **resolution** for finer or coarser evaluation.
4. **Import CSV** of Pr measurements (if available).
5. The **3D plots** update automatically with metrics.
6. Export the **configuration** or **Pr table** using the provided buttons.

**3D Plot Controls:**

* `W` / `S` → rotate elevation
* `A` / `D` → rotate azimuth
* Hold `Shift` → fine rotation (1° step)

---

## File Structure

```
root/
├── gui/                 # GUI source code and related assets
│   │
│   ├── config.ini       # Configuration file storing default parameters
│   ├── constants.py     # Global constants and themes for the GUI
│   ├── main.py          # Entry point of the application
│   ├── model.py         # MVVM's Model
│   ├── utils.py         # Utilities (read/write, Namespace comparison functions, Custom config parser)
│   ├── view.py          # MVVM's View
│   ├── viewmodel.py     # MVVM's ViewModel
│   ├── widgets.py       # Custom widgets (custom spinboxes, headers, 3D canvas)
│   └── screenshots/     # Folder to store screenshots for documentation
│
├── sprinklers.ipynb     # Experimentation Jupyter notebook
├── README.md            # Project description and instructions
├── requirements.txt     # Python dependencies for the project
├── van 18.csv           # Example measured Pr table
└── van.csv              # Dummy Pr table
```
---

## Project Structure

* **UI Panel**

  * General: Resolution slider
  * Zone: Width & Height
  * Sprinklers: Configuration and dimensions
  * Measurements: CSV import and step size
* **Plot Panel**

  * Zone 3D surface
  * Homogeneous distribution plot
* **Metrics Panel**

  * CU and DU values displayed
  * Export buttons for CSV/config

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/m-behery/sprinkler-distribution-evaluator/blob/main/LICENSE) file for details.

---

## Contact

Developed by **Mohamed Behery**
For questions or contributions: \[[mohamed.i.behery@proton.me](mailto:mohamed.i.behery@proton.me)]
