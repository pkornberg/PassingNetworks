# Soccer Passing Networks

This project visualizes passing networks in soccer matches for individual teams by processing match event data and generating network diagrams that highlight player connections and passing patterns throughout a season. All data is from [StatsBomb](https://github.com/statsbomb/open-data.git). 

---
 
## Project Content
 
```
PassingNetworks/
├── Data/                       
├── Examples/
│   └── workflow.ipynb           # Example walkthrough notebook
├── Utils/
│   ├── dataCollection.py        # Fetches and preprocesses match data
│   ├── dataProcessing.py        # Processes data for visualizations
│   └── visualization.py         # Generates passing network visualizations
├── .gitignore
└── README.md
```

## Installation & Setup
 
**Requirements:** Python 3.8+
 
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/PassingNetworks.git
   cd PassingNetworks
   ```
 
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
---
 
## Usage
 
### Running the full workflow
 
The easiest way to get started is with the example notebook:
 
```bash
jupyter notebook Examples/workflow.ipynb
```
 
---
 
## Results

### Passing Network

Below is an example of a passing network generated from an entire season, around 36 matches. However, this repo can be used for individual match analysis as well. For all graphs, a minimum passing threshold can be set to filter out players. 

![PassingNetwork](Images/BarcelonaPassingNetwork.png)

### Passing Heatmap

This repository can also generate passing heatmaps that visualize where a player tends to distribute the ball most frequently, offering insights into their positioning, decision making, and overall influence on the game. These heatmaps can also help identify patterns such as preferred passing zones and areas of high activity.

![Passing Heatmap](Images/passingHeatmap.png)