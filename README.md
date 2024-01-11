This repository includes all the resources used for the simulation and analysis used for the development of the P-ONE Trigger Mechanism, minus the resources already included in the pone_offline repository.

## Analysis

### 1. Noise Rate Triggers

The first part of the analysis consisted on the estimation of the noise rate triggers expected in the detector. The main sources of noise are potassium-40 decay rates in seawater, that yields a constant decay rate of 10kHz per Photo Multiplier Tubes (PMT). Additionally, bioluminescence effects yielded different rates per PMT getting up to 2MHz from some fraction of time. 

The data recovered from [STRAW](https://arxiv.org/abs/2108.04961) provided the fraction of time each PMT can be at different rates. From these data, a proability model was developed to estimate the average single Digital Optical Module (DOM) rate will read, depending on the number of PMTs in coincidence in a 10ns window.

The following equation estimates the single DOM average rate as a function of number of PMT hits and the rate of the bioluminescence.

$$sdr(n) = \sum_{r=0}^{n} rate^{n-r}  nCr(8,n-r)  (K40)^{r}  nCr(8,r)  (10ns)^{n-1}  (\% t)$$

The fraction of time at each rate is shown by the following data recovered from the [STRAW](https://arxiv.org/abs/2108.04961) paper.

 <img src='https://github.com/SantMiro/P_ONE_Trigger/blob/main/Figures/straw_rates.jpg' width = '650' height = '550'>


## Simulation
Lists the different simulation files used for the analysis.

## Tools
Lists all the modules and utilities used that cannot be found in the pone_offline repository.

