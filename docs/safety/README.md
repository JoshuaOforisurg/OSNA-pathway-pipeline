# Clinical safety

## Current status

This repository is an early technical prototype. It is not a medical device, clinical record,
validated health IT system, or approved component of an intraoperative pathway.

## Current restrictions

- Full pathway processing and analytical outputs use synthetic data only.
- Clinical extracts are limited to approved, governed, validation-only work.
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
- A technical quality-gate exit code being mistaken for a clinical decision
- Incorrect local column or code mapping creating a false canonical event
- Inappropriate inclusion of identifiable patient data

The optional command-line quality gate is solely for automation and review workflow. It does not
validate or authorise a clinical result and must not delay, replace, or control the
laboratory-to-surgeon communication pathway.

Mappings declared `governed_clinical` are restricted to validation-only mode. The mode reports
aggregate structural findings and creates no pathway outputs. This restriction neither confirms
the mapping's clinical meaning nor grants permission to access or process clinical data.
The readiness report excludes row identifiers and source values but includes internal column
metadata and unsuppressed counts, which must still be treated as potentially sensitive.

## Safety work before real-world use

Future work will require an explicit intended-purpose statement, clinical workflow validation,
hazard analysis, risk controls, human-factors review, information governance, security assurance,
and assessment against applicable NHS clinical-safety and medical-device requirements.

A qualified Clinical Safety Officer and the relevant healthcare organisation must be involved
before deployment into a real clinical environment.
