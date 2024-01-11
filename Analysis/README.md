# Analysis

In this folder you can find the most relevant files used for conducting the analysis on the trigger mechanism. Each file requires a different dataset from the _Simulation_ folder.

## Geometry Selection

Is the file used to estimate the most optimal string separation distance in order to trigger on the highest number of events possible. Simulated dataset: [sim_10tev_10pev](https://github.com/MiroSant/P-ONE/tree/main/Simulations/sim_10tev_10pev).

## Trigger Rates

A class file that estimates the average single DOM rate depending on the PMT rate at that time. Data recovered from [STRAW](https://arxiv.org/pdf/2108.04961.pdf).

## Abolute Analysis

This notebook calculates the efficiency of 10TeV muons injected isotropically into the 10-string detector for the PMT rate cut-off trigger and the Adaptive Trigger. It is also compared to a high-rate trigger. Simulated dataset: [sim_10tev_isotropic](https://github.com/MiroSant/P-ONE/tree/main/Simulations/sim_10tev_isotropic)

## Muon Efficiency vs. Energy

This notebook calculates the trigger efficiency of muon neutrinos as a function of energy from 100GeV to 10PeV. Simulated dataset: [sim_100gev_10pev_muons](https://github.com/MiroSant/P-ONE/tree/main/Simulations/sim_100gev_10pev_muons)

## Electron Efficiency vs. Energy

This notebook calculates the tigger efficiency of electron neutrinos as a function of energy from 100GeV to 10PeV. Simulated dataset: [sim_100gev_10pev_cascades/electron](https://github.com/MiroSant/P-ONE/tree/main/Simulations/sim_100gev_10pev_cascades/electron)

## Tau Efficiency vs. Energy

This notebook calculates the tigger efficiency of tau neutrinos as a function of energy from 100GeV to 10PeV. Simulated dataset: [sim_100gev_10pev_cascades/tau](https://github.com/MiroSant/P-ONE/tree/main/Simulations/sim_100gev_10pev_cascades/tau)

