This is a list of modules used during the simulation stages that are not part of the pone_offline repository. If a module is needed that cannot be found here,
should be found in the pone_offline repository.

## Atm_Weighter.py

This module uses LeptonWeighter to weigh the sample of events created with LeptonInjector. The fluxes used in this simulation are Atmospheric and Astrophysical,
generated with nuSQUIDs and nuflux.

## DOMTrigger_miro.py

This module finds PMT coincidences in a single DOM considering a 10ns window. It sorts by time all PMT hits in a DOM in a single event. It looks at 10ns windows
searching for the largest coincidence group, that occurred earlier for the duration of the event. 

## GoodEvent.py

This module filters out events that hit fewer than 5 DOMs.

## MuonEnergy.py

This module filters out muon events that did not satisfy a Minimum Energy at the Point of Closest Approach to the origin of the detector.

## trackgeo.py

This module measures the distance traveled inside the detector volume by a particle knowing it initial coordinates and angular trajectories.

