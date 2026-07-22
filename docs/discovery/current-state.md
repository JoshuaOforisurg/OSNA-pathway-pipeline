# Current-state discovery

**Status:** Working discovery record, not a validated local workflow description.

This document separates direct practitioner observations from assumptions and unanswered
questions. It must be reviewed with the relevant theatre, laboratory, pathology IT, breast,
cancer-services, and clinical-safety teams before it informs a real implementation.

## Currently observed

- OSNA is used during breast surgery in the practitioner's current setting.
- An "OSNA time" is recorded on the theatre board.
- The organisation uses Millennium as an electronic patient record.
- Laboratory staff telephone the surgeon with the OSNA result.
- The result is communicated verbally as positive or negative in the observed workflow.
- The practitioner is not aware of barcode scanning for the OSNA specimen within theatre.

These observations establish that a manual, time-sensitive communication step exists. They do not
establish that the result or its timestamps are absent from the LIMS, analyser, EPR, or another
system.

## Important unknowns

| Area | Question to answer | Suggested owner |
| --- | --- | --- |
| Theatre timestamp | What exact event does the board's "OSNA time" represent? | Theatre digital lead or breast theatre lead |
| Board | Is the board electronic, physical, or both, and is the value retained? | Theatre digital lead |
| Booking/readiness | How is an OSNA case booked and how does theatre know the laboratory is ready? | Breast service and molecular laboratory leads |
| LIMS | Which LIMS is used and which OSNA events and results does it store? | Pathology IT/LIMS manager |
| Analyser | Does the OSNA analyser send results to the LIMS or support an approved export? | OSNA biomedical scientist and pathology IT |
| Result verification | What constitutes a verified result and who performs it? | Laboratory clinical lead |
| Communication | Are call time, recipient, read-back, and acknowledgement recorded anywhere? | Laboratory and theatre leads |
| Identifiers | Which case and specimen identifiers are present at each handoff? | Laboratory and theatre informatics |
| Tracking | Are labels or barcodes applied or scanned after the specimen leaves theatre? | Specimen reception/laboratory lead |
| EPR | Where do the order and final result appear in Millennium, and when? | Millennium analyst |
| Cancer pathway | Which system contains MDT and cancer outcomes? | Cancer-services data manager |
| Audit | Which OSNA measures are currently reported and how are they assembled? | Service manager or audit lead |

## Working product hypothesis

The project will test whether events already generated across the pathway can be safely linked
into an auditable timeline. It will not assume that a new operational interface is needed.

## Discovery rule

No unknown in this document should be converted into a product requirement merely because it is
convenient for the prototype. Synthetic source contracts are test instruments until a system owner
confirms the corresponding real field and its permitted use.
