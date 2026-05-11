# ASDS_DataVisualization_Project

## Running the app
===!!!For the sake of the assignment processed_dogs.csv is also pushed to the github repository!!!===

Make sure the virtual environment is activated and dependencies are installed (see below), then run:

```bash
python src/app.py
```

The terminal will print the local URL. Open it in your browser:

http://127.0.0.1:8050/

## Virtual Environment Setup

Create a virtual environment (if you don't have one):

```bash
python -m venv venv
```

Activate it:

**PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt**

```cmd
venv\Scripts\activate
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

## Dataset

The dataset used in this project was obtained from Kaggle:

https://www.kaggle.com/datasets/jmolitoris/adoptable-dogs

Due to licensing and repository size considerations, the dataset is **not included in this repository**.

### Setup

1. Download the dataset from the Kaggle link above.
2. Place all dataset files inside the `_data` folder.

## Codes

All the codes are located in the folder `src`

### EDA
Aside from EDA this .ipynb file will also output a processed file (in the `_output` folder)

### Dashboard

The interactive dashboard is built with [Plotly Dash](https://dash.plotly.com/) and consists of 3 pages.