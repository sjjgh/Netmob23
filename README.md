# Temporal-and-spatial-analysis-of-mobile-app-data
This is a backup of the Netmob23 Project.
The Result is presented in Netmob 2023 conference in Spain. The report of the project and my notes can be found in this reop.

The NetMob 2023 Data Challenge is a competition aiming at deriving and exploiting insights from massive mobile service consumption information.
The Data consist app usage of:
20 urban areas in France;\\
68 mobile services;\\
77 days continuous days;\\
100 x 100 m^2 spatial resolution;\\
15 minute temporal resolution;\\
400+ billion data points;\\
2.3+ TB of data.\\
A full description of the dataset is available at https://arxiv.org/abs/2305.06933.

Asif Shakeel and Jiajie Shi are the main investigator of the spatial analysis of this data. Orest Bucicovschi, David A. Meyer and David P. Rideout are in charge of the temporal analysis. We use earth movers' distance (detailed in report) to approximate the flow between each snapshots.
By using the method, we are able to visulize the flows on real map:

<img src="https://github.com/sjjgh/Netmob23/blob/main/evp_0.png" width="600" height="400">

By project our result on real map, we are able to detect some really interesting trend in the flow pattern. An illustrative example involves running the algorithm locally to observe Instagram usage changes around Prince Park Stadium during a football match scheduled for April 3rd. Below are the population flow patterns observed from 8:00-8:15 pm, an hour prior to the start of the match. Both EMDE and NEMD clearly depict the movement of crowds towards the stadium, as indicated by the arrows converging from the periphery towards the center.

<img src="https://github.com/sjjgh/Netmob23/blob/main/Flow_p1.png" width="400" height="400">




