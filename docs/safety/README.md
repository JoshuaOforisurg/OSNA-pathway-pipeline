# Clinical safety

## Current status

This repository is an early technical prototype. It is not a medical device, clinical record,
validated health IT system, or approved component of an intraoperative pathway.

## Current restrictions

- Synthetic data only.
- No connection to clinical systems or devices.
- No use during patient care.
- No diagnosis, prognosis, or treatment recommendation.
- No use as the sole or authoritative source of an OSNA result.
- No automated communication of time-critical clinical information.

## Initial hazards to track

- Incorrect patient, procedure, or specimen linkage
- Loss or duplication of a pathway event
- Displaying an unverified or invalid result as verified
- Incorrect timestamp ordering or duration calculation
- Failure to distinguish a repeat assay from a separate specimen
- Stale information appearing current
- Derived metrics being mistaken for clinical facts
- Inappropriate inclusion of identifiable patient data

## Safety work before real-world use

Future work will require an explicit intended-purpose statement, clinical workflow validation,
hazard analysis, risk controls, human-factors review, information governance, security assurance,
and assessment against applicable NHS clinical-safety and medical-device requirements.

A qualified Clinical Safety Officer and the relevant healthcare organisation must be involved
before deployment into a real clinical environment.
