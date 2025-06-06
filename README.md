# Temporal and Spatial Analysis of Mobile App Data

This repository contains a backup of the **NetMob23 Project**, presented at the **NetMob 2023 Conference** in Spain. The project report and my personal notes are available in this repository.

## About the Challenge

The **NetMob 2023 Data Challenge** aims to extract meaningful insights from large-scale mobile service usage data. The dataset includes:

- Mobile app usage across **20 urban areas in France**
- **68 distinct mobile services**
- **77 consecutive days** of data
- **100 × 100 m²** spatial resolution
- **15-minute** temporal resolution
- Over **400 billion** data points
- Total data size: **2.3+ TB**

## Results:

A full description of the dataset is available on [arXiv](https://arxiv.org/abs/2305.06933).

The project is a collaborative effort between:

- **Spatial analysis**: *Asif Shakeel* and *Jiajie Shi*
- **Temporal analysis**: *Orest Bucicovschi*, *David A. Meyer*, and *David P. Rideout*

We used **Earth Mover’s Distance (EMD)** (see report for details) to approximate the flow of app usage between time snapshots. This enabled us to visualize the movement dynamics on real-world maps.

<img src="https://github.com/sjjgh/Netmob23/blob/main/evp_0.png" width="600" height="400">

By project the resulting flows on real map, we are able to detect some really interesting trends in the real world. An illustrative example involves running the algorithm locally to observe Instagram usage changes around Prince Park Stadium during a football match scheduled for April 3rd. Below are the population flow patterns observed from 8:00-8:15 pm, an hour prior to the start of the match. Both EMDE and NEMD clearly depict the movement of crowds towards the stadium, as indicated by the arrows converging from the periphery towards the center.

<img src="https://github.com/sjjgh/Netmob23/blob/main/Flow_p1.png" width="400" height="400">




