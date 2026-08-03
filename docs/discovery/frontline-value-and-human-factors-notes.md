# Frontline value and human-factors research notes

> **Status:** Unverified stakeholder-value hypothesis. This note preserves ideas supplied during
> product development on 3 August 2026. It does not describe implemented functionality, validated
> benefits, clinical requirements, or an approved future workflow.

## Why this note exists

The supplied discussion explored what the OSNA Pathway Pipeline might eventually mean to theatre
staff, surgeons, laboratory scientists, and technicians. It proposed benefits such as reduced
uncertainty, fewer status calls, clearer handoffs, more complete audit evidence, visibility of
bottlenecks, and less blame directed at individuals when a system-level problem occurs.

Those ideas are valuable for user discovery. Some claims, however, describe a real-time clinical
tracking and alerting application rather than the current retrospective integration and evidence
pipeline. They must not be presented as existing or proven benefits.

The supplied conversation ended mid-sentence while discussing which theatre alarms should be
limited to active patient threats. This note does not infer or complete the missing text.

## Grounded value proposition

The current product could support frontline staff indirectly by helping authorised analysts and
service leads reconstruct the recorded OSNA pathway more consistently. It may help a service:

- identify where records are commonly missing or difficult to link;
- quantify how often communication or acknowledgement evidence is available;
- understand repeat assays and failed-QC run histories;
- identify recorded delays and recurring handoff problems for investigation;
- reduce manual reconstruction during audit and service-improvement work; and
- discuss process problems using reproducible evidence rather than individual recollection.

This is different from providing live specimen tracking, clinical alerts, or an authoritative
result screen during surgery.

## Potential value to theatre staff

The supplied discussion suggested that theatre nurses and scrub teams might benefit from less
uncertainty about specimen receipt, processing, result communication, and acknowledgement.

This benefit would require more than the current pipeline. A future theatre-facing view would need:

- sufficiently current data from authoritative systems;
- confirmed identifiers at every handoff;
- a validated definition of each displayed status;
- clear stale-data and missing-data behaviour;
- an approved acknowledgement workflow;
- usability testing under theatre conditions; and
- downtime procedures that do not interfere with the existing communication pathway.

Until those controls exist, the pipeline can report only that a matching extract record was or was
not available. It cannot provide absolute confirmation that a physical specimen arrived or that an
unrecorded real-world action did not occur.

## Potential value to surgeons

The supplied discussion proposed fewer communication distractions and a trustworthy, auditable
timeline. Audit evidence may eventually support service review, but the current product must not be
used by a surgeon to make an intraoperative decision.

A future surgeon-facing status or alert function would be a materially different clinical product.
It would require an explicit intended purpose, authoritative data source, latency and availability
requirements, human-factors work, clinical risk management, operational support, and assessment
against applicable NHS and medical-device requirements.

The project must not promise legal protection. An analytical timeline may contribute evidence, but
its meaning, completeness, provenance, governance, and admissibility would require expert review.

## Potential value to laboratory staff

The supplied discussion suggested fewer status-check calls, better visibility of bottlenecks, and
clearer repeat and QC histories. These are useful discovery hypotheses.

The current pipeline can preserve recorded QC status and detect contradictions or missing fields in
the received data. It cannot detect analyser calibration drift, independently validate the assay,
or prevent a faulty result from reaching the clinical record. Those responsibilities belong to the
approved analyser, laboratory quality-management system, LIMS, verification process, and staff.

Timing data may show recurring patterns or workload pressure, but it cannot by itself prove that
the laboratory is understaffed. Staffing conclusions require workload, rota, case-mix, capacity,
process, and contextual evidence.

## Claims that must not be made without evidence

| Claim from the supplied discussion | Grounded position |
| --- | --- |
| The pipeline eliminates lost specimens | It currently detects missing or orphaned records in supplied data; it does not physically track specimens. |
| Staff receive absolute confirmation that every sample arrived | A definitive status would require validated, timely, authoritative receipt data and reliable specimen identifiers. |
| Acknowledgement takes less than two seconds | No acknowledgement interface or human-factors study exists. |
| Surgeons can rely on the pipeline for intraoperative decisions | Prohibited by the current product and safety boundary. |
| The pipeline supplies automated reliable alerts | No alerting system is implemented or approved. |
| The audit trail provides legal protection | Legal effects cannot be promised and would depend on the system's validated purpose and evidence. |
| The pipeline detects analyser calibration drift | Not implemented; calibration and assay quality remain laboratory and analyser responsibilities. |
| The pipeline prevents faulty data reaching the patient record | Not implemented; it is not in the result-reporting path. |
| Bottleneck timing proves understaffing | Timings can inform investigation but cannot establish cause alone. |
| The pipeline removes the need for laboratory telephone communication | It must not replace the approved time-critical telephone pathway. |
| RFID or barcode automation is required | This is an untested design option, not a confirmed requirement. |
| Missing specimens commonly cause reoperation or litigation | Frequency and consequences require authoritative evidence and local context. |

## Alert-fatigue and workflow risks

The supplied discussion correctly raised alert fatigue, data-entry burden, and software
fragmentation as important risks. These should be treated as discovery and design constraints:

- do not create an alert merely because a field is absent from an extract;
- keep technical data-quality findings away from clinical users unless a validated action is
  required;
- avoid duplicate alerts already produced by LIMS, EPR, analyser middleware, or theatre systems;
- prefer passive data reuse over new manual entry;
- never require acknowledgement clicks that distract from patient care without demonstrated value;
- show data freshness, source, uncertainty, and downtime state clearly;
- define ownership and escalation for every alert before enabling it; and
- measure false alerts, ignored alerts, workload, and unintended consequences during evaluation.

## Frontline discovery questions

### Theatre nurses and scrub teams

1. At which points are staff uncertain about specimen location, laboratory receipt, result status,
   or acknowledgement?
2. How often do they call the laboratory for status, and what triggers the call?
3. What does the theatre-board "OSNA time" mean, and who records it?
4. Which information would help during the case, and which belongs only in retrospective review?
5. Would another screen, acknowledgement, barcode scan, or alert reduce or increase workload?

### Surgeons

1. Which source is currently treated as authoritative for the intraoperative result?
2. What information is required beyond the telephone communication, if any?
3. Is the unmet need intraoperative, retrospective, educational, operational, or medico-legal?
4. What delay, missingness, or stale-data behaviour would make a digital view unsafe?
5. Would a retrospective audit report answer the need without a live interface?

### Laboratory scientists and technicians

1. Which status calls interrupt laboratory work, and can existing systems already answer them?
2. Which analyser, LIMS, QC, repeat, verification, and communication records are retained?
3. Which delays are actionable by the laboratory and which occur elsewhere in the pathway?
4. Which technical findings should remain inside laboratory or informatics workflows?
5. Who would own correction, replay, reconciliation, downtime, and support for a new integration?

## Product phases implied by this research

### Phase A: Retrospective evidence product

The current direction. It supports authorised audit and service-improvement users. Frontline
benefit is indirect, and there is no live interface or alert.

### Phase B: Read-only operational visibility

Possible only if retrospective evidence shows a current-status need and the source data is timely
and authoritative enough. A minimal view could show recorded status, source, freshness, and
exceptions without replacing the result call.

### Phase C: Acknowledgement or alerting workflow

This would make the product part of frontline clinical operations. It requires separate approval,
clinical-safety work, human-factors testing, resilience, monitoring, ownership, and support. It
must not be treated as an automatic extension of the analytical pipeline.

## Current conclusion

The strongest near-term frontline benefit is not "one more screen." It is better evidence for
improving the system around frontline staff. A dashboard, acknowledgement function, or alert should
be added only if user research demonstrates that it solves a specific problem more safely and with
less burden than the existing workflow.
