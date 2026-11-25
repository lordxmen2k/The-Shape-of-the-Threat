# Verified research base — lunar-hosted space situational awareness / early warning

**Status:** M1 seed. NOT a structure, NOT an outline. Collected 24 Nov 2026 to test the
owner's concept before any commitment to a thesis or a table of contents.

**Owner's raw concept (24 Nov 2026):**
"Non satelital interlinked early warning datacenter pods. Positioning Beam to Earth.
Extreme Anomaly Detection Systems" — objects that approach Earth, some closer than
others; dedicated tracking systems exist on Earth; some might be better deployed on the
lunar surface; how it would keep Earth safe by predicting movements and tracking space
objects before it is too late.

Every identifier below was resolved against a registry (arXiv API, Crossref, DataCite,
NASA NTRS citation service) on 24 Nov 2026. Titles were compared with the intended
title before use.

---

## 1. The Earth side — what exists right now

### 1.1 The catalogue is the bottleneck (ESA)

Source: ESA Space Environment Report, 10th edition, published 14 Sep 2026, data to
end 2025; MASTER-8 reference population 1 Feb 2026.
- <https://www.esa.int/articles/esa-space-environment-report-2026>
- <https://www.sdo.esoc.esa.int/environment_report/Space_Environment_Report_I10R1_20260908.pdf>
- Live statistics, updated 17 Nov 2026: <https://sdup.esoc.esa.int/discosweb/statistics/>

| Quantity | Value |
|---|---|
| Objects regularly tracked and catalogued | ~47,380 (live) / 44,964 (report table, 1 Jan 2026) |
| Of which classed **Unidentified (UI)** | 10,963 live / 11,087 report table — **≈23–25 % of the catalogue** |
| Modelled population > 10 cm | 68,450 (incl. ~11,300 active payloads) |
| Modelled debris 1–10 cm | 1.5 million |
| Modelled debris 1 mm – 1 cm | 230 million |
| Total mass in orbit | 17,650 t (live) / 132,483 t incl. LEO? no — 17,650 t is the live table total |

ESA's own framing (report, §2.7): "the number of space objects with unidentified
object class continues to increase"; and from the ESA release: "a growing gap between
detected and catalogued (i.e. detected of known origin) fragments… as technologies
improve, we can observe more objects but many of these detectable objects cannot yet be
linked to a specific source or break-up event."

The report also defines three distinct classes that a book must keep separate:
*catalogued*, *asserted* (known to exist by design but never reported), and
non-catalogued/modelled.

### 1.2 Conjunction assessment — the actual "early warning" machinery

- NASA CA Handbook Vol. 1 (Best Practices), Rev 2, 2026:
  <https://www.nasa.gov/wp-content/uploads/2026/08/ca-handbook-volume1-nasa-sp-20205011318-rev2-vol1.pdf>
- NASA Conjunction Assessment and Best Practices (Global Sentinel CA 2025), NTRS 20250003638
- Conjunction Assessment Screening Volume Sizing and Event Filtering, NTRS 20170007928
- Assessment of Uncertainty-Based Screening Volumes for NASA Robotic LEO and GEO
  Conjunction Risk Assessment, NTRS 20110015239
- NASA CARA Step 1 page: <https://www.nasa.gov/cara/step-1-conjunction-event-prediction/>

Verified operating parameters:
- The **Space Surveillance Network (SSN)** is the DoD/USSF sensor resource (radar +
  optical); the **High Accuracy Catalog (HAC)** is maintained from it by the
  **18th Space Defense Squadron (18 SDS)**, Vandenberg.
- Screenings run **every eight hours**. Lookout: **7 days for LEO, 10 days for GEO/HEO**.
- Screening volumes are ellipsoids sized by CARA for **95 % capture** of relative
  uncertainty on a two-year moving window. Worked example volumes:
  LEO #1 = 1.5 × 69 × 145 km (7 days); LEO #3 = 0.5 × 11 × 9 km; a notional event
  screen used 0.5 × 17 × 20 km and was caught at 6.5 days-to-TCA.
- Trackability thresholds: **> 10 cm reliably trackable in LEO, > 50 cm in GEO.**
- **TLEs are explicitly NOT sufficient for conjunction assessment** (NASA CA policy).
- A 2020 NASA ODPO catalogue for CARA contained **> 300,000 objects > 1 cm** — the
  operational population is far larger than the public one.
- NASA CARA protects ~100 non-HSF Earth-orbiting assets (plus crewed missions).

### 1.3 "Extreme anomaly detection" — the field's real vocabulary

The user's phrase maps onto a crowded, well-defined 2026 literature. Real names:
**uncorrelated track (UCT)**, **loss of custody**, **manoeuvre detection**,
**pattern of life (PoL)**, **data association**, **catalogue maintenance**.

AMOS 2026 (Advanced Maui Optical and Space Surveillance Technologies Conference) program
papers, all verified: <https://amostech.com/wp-content/uploads/2026/09/AMOS-2026-Program.pdf>
- *Anomalous Actor Detection Using Self-Similarity of Multi-Resolution Temporal Sequences*
- *Establishing an Automated Pattern of Life Method for Manoeuvre Anomaly Detection in GEO*
- *SSAPy in the Loop: TLE-Driven Orbit Anomaly Detection with Autoencoders and Isolation Forests*
- *Non-Myopic, Information Driven Sensor Tasking for Distributed Catalogue Maintenance in Space Domain Awareness* (Whipbird Signals)
- *Finding Lost Satellites: An Adaptive Electro-Optical Search Architecture* (InTrack Radar Technologies)
- *Electro-Optical and Passive Radio-Frequency Data Fusion for In-Space Anomaly Detection*
- *Turning Uncorrelated Tracks into Catalogued Objects* (NorthStar Earth & Space) —
  <https://amostech.com/TechnicalPapers/2026/Astrodynamics/Pirovano.pdf>
  Operationally deployed in **Joint Commercial Operations (JCO)**. Five-stage pipeline:
  attributable estimation → adaptive N-CAR sampling → N-CAR clustering → orbit
  determination → ballistic association. Real run: **4,888 tracks screened over a 48 h
  window in ~4.5 min (0.056 s/track)**; only 43 had non-empty admissible regions; 9
  passed the χ² gate; custody of a satellite lost after a GTO→GEO manoeuvre was recovered.
- *MACHINA Tactical Persistent Monitoring: UCT Track, Triage, and Graduation* (Segal &
  Harris) — <https://amostech.com/TechnicalPapers/2026/Poster/Segal.pdf>
  Track / Triage / Graduation; uncorrelated-track *origination* — connecting a UCT back to
  its originating object and attributing the causal manoeuvre.
- *Proactive Satellite Threat Detection Through Physics-Informed Pattern of Life Analysis*
  (Spaceflux) — <https://amostech.com/TechnicalPapers/2026/Poster/Waldmann.pdf>
  Operationally deployed; the database snapshot inspected held **44,652 resident space
  objects** (39,122 LEO, 534 MEO, 1,780 GEO, 3,061 HEO, 155 outside gates).
  Multi-phenomenology: orbital + photometric + relational evidence.

### 1.4 A measured uncorrelated fraction — the single best anchor for the book

**arXiv:2606.30286** — "Streak detection in the VST/OmegaCAM archive using deep learning"
(published 29 Jun 2026). Title and ID verified via the arXiv API.
- **1,246,048** OmegaCAM CCD frames over one year → **25,335** streaks detected.
- **> 20 % of true detections could not be matched to any object in the space-track
  catalogue.** Manual review: **21 %** (December 2023) and **23 %** (January 2023) of
  confirmed detections unmatched.
- Of the correlated set: 16,776 streaks correlated with 2,761 unique catalogue objects,
  while **8,559 traces originated from unidentified sources**.
- 16.9 % of images showed some level of contamination.

This is the cleanest published measurement of the exact gap the book would be about.

### 1.5 Planetary defence from the ground

- Cross-Disciplinary Deep Space Radar Needs Study (2023):
  <https://www.nasa.gov/wp-content/uploads/2023/10/atr-2023-01267.pdf>
  Evaluated DSS-14, the 10-element VLBA, the 27-element VLA and the Green Bank Telescope.
  **"None of today's facilities have the capability to meet the planetary defense mission
  needs, even at the threshold level of performance."** A GBT high-power transmitter paired
  with the ngVLA would *just* meet the threshold needs. Threshold requirements: detect a
  100 m NEA at 50 million km; image a 5 m-resolution NEA at 8 million km.
  Note: pointing near the Moon raises system temperature by ~10× through lunar
  re-radiation — a ground-side instance of the same lunar-brightening problem.
- GBT + VLBA: 650 W at 13.9 GHz, radar images of the Moon and a NEO flyby (NRAO).
- NASA Planetary Defence Rapid Mission Architecture Study — NEOSM at Earth–Sun L1,
  working synergistically with Rubin/LSST.

---

## 2. The Moon side — what exists right now

### 2.1 Communications and navigation: LunaNet / LCRNS (the rail to ride)

- NASA LunaNet page: <https://www.nasa.gov/communicating-with-missions/lunanet/>
- NASA LCRNS project: <https://www.nasa.gov/goddard/esc/lcrns/>
- LCRNS Requirements Document (Aug 2025):
  <https://www.nasa.gov/wp-content/uploads/2025/08/lunar-relay-services-requirements-document-srd.pdf>
- NASA SCaN Lunar Architecture, IAC-24-B3-1-9-x85682, NTRS 20240012244:
  <https://ntrs.nasa.gov/api/citations/20240012244/downloads/IAC%202024%20NASA%20SCaN%20Lunar%20Architecture_FINAL.pdf>
- LCRNS at ICG-IOAG CisLunar PNT Workshop, Feb 2025, NTRS 20250001223
- LCRNS at ICSO, May 2025:
  <https://www.nasa.gov/wp-content/uploads/2026/02/lcrns-esper-257-1.pdf>

Verified:
- LunaNet is an **internationally coordinated interoperability framework** (standards,
  protocols, interface requirements), not a single NASA network. LNIS (LunaNet
  Interoperability Specification) Draft v5; Augmented Forward Signal published Feb 2025.
- NASA LCRNS is NASA's instantiation. **Intuitive Machines** competitively selected in
  2024 under the Near Space Network Services call as the first commercial service provider.
- IOC in three increments — **Alpha, Bravo, Charlie** — with full operational IOC targeted
  **2028**; Enhanced Operational Capability ~2030.
- Coverage: a **single** lunar relay gives **80–86 %** coverage for worst/best-case
  south-pole landing sites; **two additional relays give 100 %**.
- NASA is buying **commercial services**, and providers are responsible end-to-end for
  data return to Earth.
- ESA and Japan have LunaNet instantiations in development.

### 2.2 The ground segment that already points at the Moon

- **Deep Space Network** upgrades: DSS-23 (Goldstone) in progress, delivery April 2026;
  DSS-33 (Canberra) planned 2029; DSS-35/DSS-36 (Canberra) complete; DSS-53 (Jan 2021)
  and DSS-56 (Feb 2022) (Madrid).
- **LEGS — Lunar Exploration Ground Sites**: NASA initiating **three sites with 18-m
  antennas** as government-owned-contractor-operated assets for Direct-to-Earth (DTE)
  cislunar coverage.
- Orion **Artemis II Optical Communications System (O2O)**: transmitted **484 GB** over
  the 10-day Artemis II mission.
- **TBIRD** (TeraByte InfraRed Delivery, 6U CubeSat in LEO, May 2022 – Sep 2024):
  **200 Gbps** optical downlink; **4.8 TB error-free in a single ~5-minute pass**
  (Guinness World Record); < 10 µrad RMS body pointing; 1.5 µm band, dual-polarisation
  QPSK; ground terminal at JPL's Optical Communication Telescope Laboratory.
  NTRS 20230000434; NTRS 20230014010.
- **LLCD** (2013–14, lunar orbit → Earth): **622 Mbps**, four 40 cm ground telescopes.
  LRO's optical relay: 1.244 Gbps.

**Engineering consequence for the "beam to Earth":** optical downlink from the Moon is
*proven* but at 622 Mbps — two orders of magnitude below TBIRD's 200 Gbps — because the
longer range and the narrower divergence cost received power. Energy in a beam falls as
1/r². The Moon→Earth beam is a *modest* pipe compared with a LEO optical downlink.

### 2.3 The Moon as a sensing site — NASA is already funding it

**Lunar Sentinel — Advanced Space, NASA Ames Research Center, SBIR Phase II, awarded
15 Sep 2026.** <https://advancedspace.com/advanced-space-awarded-sbir-phase-ii-contract-to-develop-space-situational-awareness-capabilities-in-low-lunar-orbit-for-nasa/>
- Develops algorithms to **detect, track, and catalogue non-transmitting objects in Low
  Lunar Orbit** using a **hybrid network of lunar-surface and in-space optical sensors**.
- Phase I study showed a network of in-situ observers improves visibility of the LLO
  environment and maintains awareness of objects difficult to track from Earth.
- Names the central obstacle: **the "lunar exclusion zone" or "Cone of Shame"** —
  sunlight reflected from the lunar surface overwhelms sensors pointed near the lunar
  limb. The fix: observe **"up" and "sideways"** rather than directly across the bright
  lunar background, from vantage points that avoid the exclusion zone.
- Goal: a distributed lunar-orbit catalogue and STM constellation **with minimal reliance
  on Earth**.

**CisLunarSense — arXiv:2604.10807** (published 12 Apr 2026), Dong & Akan.
**This is the "use the comms beam as a sensor" idea, published.**
- Opportunistic **integrated sensing and communication (ISAC)**: exploit the Lunar
  Gateway's Ka-band relay for **monostatic debris detection** during active relay
  sessions — no dedicated radar hardware or spectrum, only a multicarrier-capable
  transceiver and a configurable fraction of session time allocated to sensing.
- Quantifies a **36 dB cislunar sensing advantage** over a ground-based Ka-band reference.
- Gateway-operational debris (v_rel < 50 m/s) detectable within **700 km** with
  **over 30 minutes of warning**; external threats (v_rel up to 500 m/s) detectable
  within **400–630 km**.
- Context: the Gateway is scheduled for NRHO assembly around Earth–Moon L2 from 2028;
  objects separated in NRHO remain in the vicinity 30–100 days, repeatedly approaching
  at 30–50 m/s.

### 2.4 The military is already moving on cislunar awareness

- **AFRL Oracle family**: Oracle-Prime (Oracle-P) — purpose-built cislunar SSA
  experiment; wide-field discovery sensor plus narrow-field custody sensor with onboard
  processing; Terran Orbital bus PDR Dec 2025, delivery targeted 2027, seeking a launch
  opportunity; **Advanced Space** is the prime for Oracle-P. Oracle-Mobility (Oracle-M),
  formerly D2S2 — mobile pathfinder, $75 M, integrated propulsion hot-fire complete
  March 2025, launch expected mid-2027.
  <https://www.afrl.af.mil/News/Article-Display/Article/3611977/afrls-oracle-family-of-systems-developing-nations-1st-cislunar-space-situationa/>
  <https://aviationweek.com/space/satellites/afrl-cislunar-space-tracking-prototype-due-launch-mid-27>
- **Space Force Cislunar Coordination Office** announced 16 Apr 2026.
- **Cislunar Prime** (spaceWERX): solicitation Jan 2027, awards spring 2027.
- Pentagon RFI (Nov 2026) for a **Cislunar Space System** of up to five spacecraft with
  government-provided payloads for military mission needs in late 2029.
- Assessment as of late 2026: the US has **no operational sensor dedicated to watching
  cislunar space**; everything flying is a demonstrator or a borrowed asset; the
  catalogue that governs spaceflight safety effectively stops at the geostationary belt.

### 2.5 The physics of what the Moon actually adds

**Cislunar sensor-network modelling (ESA):** "Beyond GEO: Strategies for Monitoring
Cislunar..." SDC9 paper 258, ESA Advanced Concepts Team —
<https://conference.sdo.esoc.esa.int/proceedings/sdc9/paper/258/SDC9-paper258.pdf>
- CR3BP model built on ESA's **GODOT** astrodynamics library; compares **Earth-based,
  space-based and lunar-surface-based** observers.
- "By positioning sensors close to the cislunar region, either in cislunar orbits or on
  the lunar surface itself, the limitation of low signal strength can be mitigated."
- Moon-based observers: "significantly smaller distances… higher apparent magnitude of
  the targets… better observability."
- Drawbacks named: **the Moon's horizon** limits single sensors; observers must be
  clustered into a network; and the "logistics of setting up and operating such a ground
  station."

**Delft thesis (TU Delft) — "Sensor Tasking for Space Situational Awareness in Cislunar
Space":** <https://repository.tudelft.nl/file/File_decdd924-cfe6-454b-a9a5-133aa74a7a05?preview=1>
- "Ground-based sensors and sensors in Earth's orbit suffer from limited coverage and
  unfavorable viewing geometry."
- A telescope on the Moon's **far side** can scan the sky **without Earth's light
  pollution** and could track objects in Earth–Moon L2 orbits.
- Eapen et al.: a lunar **north-pole** optical telescope improved tracking of certain
  orbits but has limitations — **fixed location, periods of darkness**; "surface sensors
  alone are not sufficient for full coverage and must be part of a mixed architecture."

**Lunar NEO detection — the "5–6 extra hours" number:**
- **arXiv:2611.05435** (published 3 Nov 2026) "From Earth's Harshest Landscapes to Lunar
  Horizons: Engineering NEA Telescopes for Extreme Environments" — AMAS project.
  A lunar telescope benefits from **no atmosphere, reduced scattered light, and extended
  access to near-Sun sky regions** that ground observatories cannot reach.
  **"Depending on the encounter geometry, lunar-based survey systems may provide up to
  5–6 hours of additional warning time compared to Earth-based observatories."**
  NEA mean approach velocity ≈ 20 km/s.
- **CAPS — Comet/Asteroid Protection System**, NASA concept studies, NTRS 20030014831
  (preprint) and NTRS 20050186565 (executive summary):
  - "Detection telescopes would be **orbiting and/or lunar surface-based**, providing
    surveys of nearly the entire celestial sky approximately every 30 days."
  - A lunar node = one wide-FOV survey telescope plus **three narrow-FOV tracking
    telescopes**; **two nodes, one in each lunar hemisphere**, give nearly complete sky
    coverage every month. Survey FOV 1.0° × 1.0°, tracking FOV 0.1° × 0.1°, mosaic
    detectors ~36,000 × 36,000 pixels.
  - Tracking telescopes used **interferometrically** for precision astrometry.
  - **Active laser ranging** for range and range-rate; "active laser ranging is
    preferable to radar systems due to the potentially large distances."
  - **"Having the interferometer fixed to the lunar surface keeps the baseline very
    stable, reducing measurement uncertainties."**
  - Named disadvantages: **lunar dust degrading the optics**, and observation axes
    **constrained by the Moon's rotation rate**.
  - Explicitly: CAPS was a conceptual study, no direct plans to implement.
- **Lunar-based NEA monitoring effectiveness evaluation** — Springer LNCS, 2026,
  DOI **10.1007/978-981-95-9694-2_9** (verified via Crossref), "Research on the
  Effectiveness Evaluation System of Lunar-Based Near-Earth Asteroid Monitoring Systems."
  States the thesis plainly: "the world relies on ground-based optical telescopes and
  radar systems for NEA monitoring… the lunar-based monitoring system can effectively
  compensate for the shortcomings of ground-based systems."

### 2.6 The Moon as a source of the hazard — the 2032 case

- **arXiv:2506.11217** (published 12 Jun 2025) "The Potential Danger to Satellites due
  to Ejecta from a 2032 Lunar Impact by Asteroid 2024 YR4."
  ~1 % chance that 2024 YR4 strikes the Moon **and** that > 10 % of the ejecta is
  delivered to Earth. Lunar ejecta entering near-Earth space would add **years to as
  much as a decade of equivalent background meteoroid exposure** to LEO satellites over
  a few days.
- **NTRS 20190029189** (AAS 19-616, "Spaceflight Hazards of Escape-Velocity-Domain
  Impact Ejecta in the CR3BP"): lunar surface impacts of > 1000 kg inject ejecta into
  geocentric orbit, **"exacerbating existing concerns in Space Situational Awareness"**.
  Escape-velocity-domain ejecta remain in orbit for more than 30 days.
- Implication: a lunar early-warning capability is not only an observer of near-Earth
  traffic. It is also the instrument that would characterise the Moon-impact case.

### 2.7 The cost of sitting on the Moon — engineering honesty

- **LuSEE-Night power requirements** (arXiv:2407.07173): electronics must operate under
  hard radiation, the instrument must be thermally isolated during the **100 K** lunar
  night and have a heat-rejection path to survive the **390 K** daytime; the
  spectrometer must be powered through the whole night from a **7 kWh** battery because
  of mass limits; **328 hours** of lunar night.
- **Overnight Power and Thermal Solutions for Small Landers** (CLPS 2022), NTRS
  20220018215: night 50–90 K, day 150–385 K; a ~100 kg science lander at ±45° latitude
  needs ~40 W of night power; a **thermal vault** (55 °C to −40 °C) is required to
  protect electronics; ~1 m² of package leaks ~9.6 W from 20 °C to deep space, so a
  lunar night costs ~3,700 Wh.
- **Surviving Night at the Lunar South Pole** (NTRS 20230008341): south-pole night
  temperatures below 100 K, down to 25 K in permanently shadowed regions; lowering a
  component's survival temperature from 270 K to 250 K cuts heater power by 26 %.
- **Lunar Power Hibernation** (NTRS 20210019184): 18650 Li-ion cells survive the cold
  and recover; ~354 h night at non-polar latitudes.
- Dust: *"dust deposition effectively increases the sink temperature thus limiting heat
  rejection capability"* (NTRS 20250007283).
- Net: a **fixed, power-surviving lunar surface station is feasible but is a
  100–500 kg-class CLPS-class problem with a 300+ hour cold-soak requirement**, and
  every real program puts the *moving* tracker in orbit and uses the surface for
  something fixed and stable.

---

## 3. Registry status of the author's own identifiers (checked 24 Nov 2026)

DataCite (Zenodo's registry):

| DOI | Status |
|---|---|
| 10.5281/zenodo.21308871 | **registered**, 2026, title confirmed |
| 10.5281/zenodo.24408811 (Is the Riemann Hypothesis Solved?) | **registered**, 2026, title confirmed |
| 10.5281/zenodo.24435288 (Dark Matter) | **NOT registered** — 404 at DataCite and at doi.org |
| 10.5281/zenodo.24457166 (Lunar Rover Design) | **NOT registered** — 404 at DataCite and at doi.org |

Both DOIs are present in seven places in each repository, and both books were built and
delivered — but the Zenodo records are not published, so the DOIs do not resolve. This
is an open action, not a defect in the books.

---

## 4. The three distinct populations — do not merge them

| Population | Scale | Why the Moon helps | The Moon's limit |
|---|---|---|---|
| **LLEO debris, 1–10 cm** | 1.5 M modelled; > 300 k in NASA's ODPO catalogue | far-side LEO view; independent geometry | too faint for a small telescope; the association problem is not solved by more detections |
| **Beyond-GEO / cislunar traffic** | the blind spot; the catalogue effectively stops at GEO | closest vantage point; fixed surface geometry | single site is limited by the Moon's horizon; needs clustering |
| **NEOs and the Moon-impact case** | 2024 YR4 returns in 2028, impact window late 2032 | solar elongation; **+5–6 h warning**; no Earth light pollution on the far side | dust on the optics; the Moon's rotation rate constrains the observation axes |

---

## 5. Open questions M1 must settle

1. What is the actual detection floor of a lunar-surface optical sensor for a 10 cm LEO
   fragment, in V magnitude, against lunar background? The Cone of Shame needs a number.
2. Does a fixed lunar site improve orbit determination (covariance) as much as the
   literature claims, and how does that compare with an LEO observer in the same place?
3. What is the Moon→Earth beam budget for the *warning* product specifically — what
   latency, what data volume, and does the 622 Mbps LLCD-class link suffice?
4. How much of the 23 % Unidentified-class catalogue and the > 20 % uncorrelated
   detection rate would a lunar sensor actually reduce, given the association engine is
   the bottleneck?
5. Which existing Artemis-era delivery vehicle (CLPS, LCRNS hosted payload) could carry
   such a pod, and at what cost and date?

---

# Appendix A — the planetary-defence angle (added 24 Nov 2026, after the owner's
# decision to centre the book on NEOs and planetary defence, and to argue fixed
# surface stations rather than a moving tracker)

**No cross-references to the owner's other books.** Each book stands on its own science.
This appendix therefore cites only the primary and peer-reviewed record.

## A.1 2024 YR4 — the spine of the argument

A ~60 m rocky object discovered **27 Dec 2024**, on a ~4-year orbit giving close
approaches in 2028 and 2032.

| Date | Event | Source |
|---|---|---|
| 27 Dec 2024 | discovered | NTRS 20260002503 |
| 18 Feb 2025 | **Earth impact probability for 22 Dec 2032 peaks at ~3 %** | NTRS 20260002503 |
| 18 & 26 Feb 2025 | JWST observations; orbit refined | NASA CNEOS blog |
| 23 Feb 2025 | Earth impact probability **drops below 10⁻⁴** | J. Astronautical Sci. 10.1007/s40295-026-00576-0 |
| late Feb → Apr 2025 | **lunar** impact probability *rises* 1.7 % → 3.8 % | NASA CNEOS blog; ESA |
| end of apparition | **lunar impact probability ~4.3 %** | NTRS 20250008366; NTRS 20260002503 |
| 11 May 2025 | **last observation** (JWST, MPEC 2025-L19) | J. Astronautical Sci. |
| — | **unobservable from ground or space until June 2028** | NTRS 20250008366 |
| 22 Dec 2032 | possible lunar impact, **v ≈ 14.1 km/s**, impact times cluster within 2 h of 15:18 UTC | arXiv:2601.10666 |

Monte Carlo (arXiv:2601.10666): **426 of 10,000 clones intersect the Moon** →
P_imp = 4.26 %. Nominal selenocentric closest approach **3,000 km**; lunar B-plane
uncertainty **25,000 km**.

**The number that should be the book's spine.** From the Journal of the Astronautical
Sciences (10.1007/s40295-026-00576-0): for **two** of ten sampled orbit solutions the
impact probability *rose above 10 %* as observations accumulated — *"implying that the
uncertainty region converges on the Earth as it shrinks over time."* And from the
19 Feb 2025 solution the ζ₂₀₃₂ uncertainty fell from **153,000 km to 126,000 km** while
the nominal miss distance rose from 120,000 km to 200,000 km.

**More data can make the answer worse.** That is the inversion at the heart of "early
warning": precision is not monotonic in information when the target's *physical*
properties are unmeasured.

## A.2 The characterisation gap — the real hole

**arXiv:2301.10348** — "On the Need for a Near-Earth Object Characterization
Constellation in Low-Earth Orbit" (24 Jan 2023).
- *"At the present rate, it will take 40 years to meet the detection mandate, and there
  are insufficient global facilities dedicated to NEO characterization to come close to
  the characterization threshold."*
- *"**Only about 15 % of NEOs have had a spectrum measured, and fewer than percent have
  been imaged with radar.**"*
- *"Radar sensitivity falls as r⁻⁴, so it is only viable for very nearby or very large
  NEOs."*
- *"In 2004 when 99942 Apophis was discovered and determined to have a high chance of
  impact 25 years later, it took far too long to characterize the asteroid."*
- There are **~200×** more Chelyabinsk-meteor-sized and larger NEOs than 140 m-and-larger
  ones.
- Characterisation requires observations spanning **multiple wavelengths, cadences and
  instruments**; detections are typically made while the NEO is close and recoverable
  for only a short duration, so *"missing the opportunity to track and characterize any
  newly discovered NEO could mean years of waiting for another opportunity."*

Detection mandate (George E. Brown, Jr. NEO Survey Act, NASA Authorization Act of
2005): find and catalogue **90 % of NEOs ≥ 140 m** within 15 years (by 2020) — the
deadline passed unmet. NASA NEO Observations Program: *"less than half of the estimated
25,000 NEOs that are 140 meters and larger have been found to date."* Congress testimony
(Zurbuchen): ~8,915 of ~21,665 NEAs found are > 140 m, ≈ 36 % of the estimated
population; at the current rate the 1 km goal took until 2011, the 140 m goal needs
> 30 years.

**This is the argument the book should make: discovery is a survey problem that is
decades from its mandate; characterisation is a physics problem that is decades further
behind. Characterisation is what turns a probabilistic exclusion into a certainty.**

## A.3 The Apophis precedent — and the Yarkovsky trap

**Apophis (99942)**, 2029 close approach at ~32,000 km above the surface (about six
Earth radii), naked-eye visible.

- Upon discovery in 2004 it was briefly estimated to have a **2.7 %** chance of
  impacting Earth in 2029; a later estimate gave a few percent for 2029 or 2036.
- **Arecibo delay-Doppler radar (2005–06)** reduced the volume of the statistical
  uncertainty region entering the encounter to **7.3 %** of the pre-radar solution, and
  combined with 0.3 arcsec optical astrometry reduced the 2029 along-track position
  uncertainty by **97 %, from ±860 km to ±22 km (3σ)**. It extended the data arc by
  96 days and eliminated the potential 2029 impact.
- But the same radar data *increased the trajectory uncertainty growth rate across the
  encounter by 800 %* because the predicted approach was closer.
- **March 2021: Goldstone (California) + Green Bank (West Virginia) bistatic radar**
  observations from ~17 million km reduced the projected 2029 orbit uncertainty *"from
  hundreds of kilometres to just a handful of kilometres"* and **ruled out any Earth
  impact for at least 100 years** — including the 2068 case. This is the most decisive
  act of planetary defence ever performed, and it was made by **a bistatic link between
  two fixed Earth stations**.
- The structural problem (Farnocchia, CNEOS): *"Normal impact probability assessments
  based on the SDM become problematic without knowledge of the object's physical
  properties; **impact could be excluded while the actual dynamics still permit it.**"*
  Key unmeasured parameters — mass and spin pole — have no associated probability
  distributions, so the study uses minimum/maximum range-of-effect rather than impact
  probability. The true 2029 keyhole *"is not known in the absence of knowledge of the
  complete dynamics."*
  Consequence: even a spacecraft accompanying Apophis with **2-metre** position
  measurements could not have settled the 2036 case.
- **arXiv:2201.12205** (28 Jan 2022) on 2029 observing conditions: **bistatic radar is
  "the most feasible radar technique"** at close approach, because the round-trip time
  is too short for monostatic TX/RX switching. A global collaboration (Australia,
  Africa, Europe, America) yields delay-Doppler SNR **> 10⁸** covering **~85 %** of
  the asteroid's surface. A satellite imaging radar facility would give ~2 orders of
  magnitude better range resolution, but no such facility has yet seen an asteroid pass
  within range.
- **Apophis Specific Action Team** (NASA, 2023): radar observable from ~mid-March to
  ~mid-May; for several days around close approach the SNR is sufficient for
  **~metre-scale resolution with existing facilities**.

## A.4 What a lunar fixed station adds — three privileges, three limits

### Privilege 1 — an interplanetary baseline for bistatic radar
The decisive PD measurements have all been **bistatic** (Goldstone→Green Bank; the
proposed 2029 global bistatic campaign). Bistatic geometry needs a transmitter and a
receiver **separated**. A lunar station gives that separation at ~400,000 km, and it is
*not on the same planet*, so it observes the target's other face and at a different
phase angle.
- **Limit:** radar sensitivity falls as **r⁻⁴** (arXiv:2301.10348). The Sun's flux at
  the target is the binding constraint. A 400,000 km baseline added to a target at
  ~1.3 AU is a modest gain, and for most NEOs the object is simply too far for radar.

### Privilege 2 — near-Sun access from the lunar poles
**arXiv:2611.05435** (3 Nov 2026): a lunar telescope benefits from no atmosphere,
reduced scattered light, and **extended access to near-Sun sky regions** largely
inaccessible from the ground because of solar glare and sky background. *"Depending on
the encounter geometry, lunar-based survey systems may provide up to **5–6 hours of
additional warning time** compared to Earth-based observatories."* NEA mean approach
velocity ≈ 20 km/s. A "baseline concept" is a compact wide-field survey telescope.
The geometry that makes it work: at the lunar poles the Sun stays near the horizon, so
the ground is dimly lit and the sky background is low, while the observer can still see
close to the Sun.
- **Limit:** the **lunar exclusion zone / "Cone of Shame"** (Advanced Space, NASA Ames
  SBIR Ph II, 15 Sep 2026) — sunlight reflected from the lunar surface overwhelms
  sensors pointed near the lunar limb. The stated fix is to observe **"up" and
  "sideways"** rather than across the bright background. Dust is the same problem later.

### Privilege 3 — a surface-fixed, stable baseline
**CAPS** (NTRS 20030014831 / 20050186565): *"Having the interferometer fixed to the
lunar surface keeps the baseline very stable, reducing measurement uncertainties."*
- **Limit, from the same source:** **lunar dust degrading the optics**, and observation
  axes **constrained by the Moon's rotation rate**. Plus, from the ESA GODOT
  cislunar-network study (SDC9 paper 258) and the TU Delft thesis: a single lunar site
  is limited by **the Moon's horizon**; sensors must be clustered; and the Moon's
  rotation constrains the accessible sky.

### The published answer to "which lunar observable is best"
**Solar System Research, 10.1134/S0038094626600563** (Pleiades, 2026), "Optical
Astrometry and Radar Ranging in Earth–Moon Tracking Geometry for Cislunar Orbit
Determination of Non-Cooperative Targets":
- Two-station Earth–Moon geometry; **weighted batch least squares in the SPOT
  orbit-determination toolkit**; three configurations — A: Earth optical astrometry +
  Earth radar range; B: A + lunar optical astrometry; C: A + lunar radar range.
- Targets: Earth–Moon L4, low circular lunar orbit, highly elliptical lunar orbit, and
  an **Apophis close-approach reference arc**.
- Verdict: *"The Earth-only baseline converged for all targets, but the benefit of a
  lunar station depended strongly on target distance and geometry. **Lunar optical was
  most effective for the two lunar orbiters. Lunar radar range was most effective for
  distant geometries. The preferred lunar-station observable is therefore not
  universal.** It depends on station–target distance, target dynamics, and parameter
  correlation."*

**That single sentence is the book's thesis.** A lunar station is not a better ground
station. It is **a second geometry**, and which observable you fly is a function of the
target.

### Why 2024 YR4 is the right test case for the book
- It is the live case: 4.3 % lunar impact, 22 Dec 2032, v ≈ 14.1 km/s, B-plane
  uncertainty 25,000 km, unobservable until June 2028.
- Its **lunar impact** is precisely the case where a lunar station has the shortest
  range and the best geometry of any platform on Earth-Moon.
- Its orbit is a ~4-year arc, so the same object returns in 2028 — the exact structure
  that makes a *fixed* station's long-baseline value compound.
- **arXiv:2601.10666** already builds a coordinated observation timeline naming
  **ground-based telescopes, lunar orbiters and surface stations** — the book can be
  the rigorous version of that timeline.
- And it is honest about the limit: the 2025–2028 blackout was a **distance** problem
  (the object was too far for *any* observatory), so a lunar station would not have
  helped there. The book must say so.

## A.5 The warning-time chain, stated honestly
The user's phrase "before it is too late" implies a single clock. There are five, and
the Moon helps with two of them:

| Stage | Instrument | Clock | Does the Moon help? |
|---|---|---|---|
| 1. Discovery | wide-field optical survey | minutes of alert | partly — near-Sun access (+5–6 h) |
| 2. Orbit / impact probability | astrometry, B-plane | weeks to years | yes — second geometry, and the 2029-window problem |
| 3. **Characterisation** | **spectra, radar shape, rotation, mass** | the actual bottleneck | **yes — most** (bistatic baseline, fixed interferometer) |
| 4. Mitigation decision | modelling | years | no |
| 5. Deflection | spacecraft | years | no |

Stage 3 is where the Moon earns its place: *"Only about 15 % of NEOs have had a spectrum
measured, and fewer than percent have been imaged with radar."*

## A.6 Ranging heritage (if the pod carries a ranging beam)
- LLR reaches **2–5 mm per normal point**, sub-centimetre Earth–Moon distance; the
  signal is ~10⁷ times weaker than LAGEOS-1 because of the r⁻⁴ law.
- **NGLR-1** (arXiv:2611.23393, 17 Nov 2026): the first single 10-cm corner-cube
  retroreflector; one-way range precision **6.0 / 6.6 / 6.5 mm** from Grasse, Wettzell
  and Apache Point, limited by the ground station rather than the reflector; legacy
  Apollo/Lunokhod arrays are limited by laser-pulse broadening from lunar librations.
- **arXiv:2502.02796** (5 Feb 2025): photon-rich CW LLR; sustained millimetre ranging
  with a pathway to sub-0.1 mm; **differential** LLR between widely separated reflectors
  mitigates common-mode station errors to tens of micrometres, limited primarily by
  uncorrelated atmospheric turbulence.
- ESA's **NovaMoon** mission will deploy a further retroreflector to the lunar South
  Pole region (ILRS), alongside the MoonLIGHT pointing concept and MPAc.
- **Inverting LLR** — a lunar *transmitter* with an Earth receiver — is the same
  time-of-flight physics with the roles reversed, and it is what gives a lunar pod a
  range observable to a non-cooperative target.

## A.7 Open questions this angle must settle (replacing the earlier list)
1. For a 60 m object at ~1.3 AU, what does a lunar station actually buy in astrometric
   σ, given the range advantage is only ~1.3×? (Optical flux ∝ 1/d²; radar ∝ 1/d⁴.)
2. What is the YR4 impact probability governed by — astrometry alone, or the physical
   parameters (mass, spin pole, thermal properties) that dominate the Yarkovsky term?
   The two candidate papers must be reconciled; the book must not assert either.
3. Can a lunar surface station realistically achieve **bistatic** operation with an Earth
   partner, and what is the round-trip time budget at a 400,000 km separation?
4. What is the lunar night / dust / Cone-of-Shame budget for a fixed station that must
   point within a few degrees of the Sun?
5. Which existing delivery vehicle carries such a pod — CLPS, LCRNS hosted payload, or
   neither — at what cost and date?
6. What would a two-station Earth–Moon architecture (one Earth, one lunar) have bought
   in the 2024 YR4 case specifically? Run it, don't assert it.

---

# Appendix B — novelty audit for the lunar NEO-characterisation concept (24 Nov 2026)

The owner asked for "something specific, not an all-size-fits-all… a definite solution to the
problem, and if it's a novel approach the better because the true and tried have failed."
That makes a **novelty audit mandatory before any architecture is proposed**: an
architecture that has been in the literature for twenty years cannot be presented as
novel.

Every identifier below resolved via the arXiv API or Crossref on 24 Nov 2026.

## B.1 The prior art map

| Candidate architecture | Prior art (verified) | Verdict |
|---|---|---|
| Lunar wide-field optical survey telescope for NEOs | **arXiv:2611.05435** (AMAS, 3 Nov 2026); CAPS NTRS 20030014831 / 20050186565; Springer LNCS 10.1007/978-981-95-9694-2_9 (2026) | **Covered.** AMAS even publishes the lead-time table: 30 m → 0.05 AU, **~4–5 days** extra; 140 m → 0.10 AU, **~9 days**; 1 km → 0.50 AU, **~6 weeks** |
| Lunar surface optical interferometer for NEO astrometry | CAPS 2003 (full Table 1 of max baselines vs angular resolution); **arXiv:2510.24901** (KISS study, 115 pp, 28 Oct 2025); **arXiv:2408.04699** (AeSI, NIAC Ph 1, 2024); MoonLITE (Pioneers, not selected; ROSES-2025 removed CLPS language) | **Covered, and a mature, heavily-funded field.** Not a gap |
| Lunar bistatic radar | **arXiv:1810.08712** (Brozović, Planetary Bistatic Radar, 2018); **arXiv:1908.05171** (Astro2020 white paper, 2019); Lazio et al., AMOS 2022 — which explicitly lists *"using the Moon itself"* among demonstrated reference-receiver scenarios; HAARP/UNM-LWA/OVRO-LWA HF bistatic work (two Moon-bounce experiments; first 9.6 MHz asteroid attempt) | **Covered.** Also note the ngVLA→GBT sensitivity numbers: 3× GBT sensitivity more than doubles the accessible volume (range +30 %); 5× more than triples it (+50 %) |
| Cislunar optical survey / catalog layer (space-borne) | **Lunar Sentinel** (Advanced Space / NASA Ames SBIR Ph II, 15 Sep 2026); **arXiv:2609.10663** (Nautilus, 9 Sep 2026, ~5–8 × 50 cm nodes, cislunar + high-Earth geometries); ORACLE-P (AFRL); CisLunarSense (arXiv:2604.10807) | **Heavily covered** |
| Space-based NEO characterisation telescope | **arXiv:2609.03371** + **arXiv:2609.02571** (3.5m Segmented-Mirror Robotic Space Telescope white papers, 2–3 Sep 2026); NEO Surveyor (L1, launch ≤ Jun 2028, 0.5 m, 4–5.2 & 6–10 µm, elongation 45–120°, ±40° ecliptic, ~13-day cadence); Roman (launch Oct 2026, arXiv:2508.14412) | **Heavily covered** |
| LEO characterisation constellation | arXiv:2301.10348 (v2, 24 Aug 2026) — proliferated small satellites, visible + NIR, central scheduler | **Covered** |

### CAPS 2003 Table 1 — the numbers a lunar interferometer must satisfy
3 m apertures, 100 m baseline, fringe visibility 0.5, λ = 750 nm, SNR 7. Maximum
allowable baseline is set by the target's angular size (the NEO becomes over-resolved):

| 50 m NEO distance (AU) | max baseline (m) | est. angular resolution (arcsec) |
|---|---|---|
| 0.8 | 168 | 1.3 × 10⁻⁴ |
| 0.6 | 450 | 4.9 × 10⁻⁵ |
| 0.4 | 337 | 1.6 × 10⁻⁴ |
| 0.2 | 225 | 2.0 × 10⁻⁴ |
| 0.1 (140 m object) | 113 | 2.6 × 10⁻⁴ |

**Note the implication: a ~100 m lunar baseline is exactly the right length for a
50–140 m NEO at 0.1–0.2 AU.** The Moon does not give a long baseline; it gives a
*stable* one (CAPS: *"Having the interferometer fixed to the lunar surface keeps the
baseline very stable, reducing measurement uncertainties"*), and the matching of
baseline to target is a constraint the Moon does not relax.

## B.2 What is genuinely NOT covered — the defensible gap

**A lunar *thermal-infrared* station, with its thermal-background budget worked out,
does not appear in the literature.** The pieces are all seeded; the assembly is not:

1. AMAS names "infrared monitoring stations" and "lunar polar observatories" as
   *asset classes* within a general Earth–Moon network, and states that a lunar polar
   observatory benefits from *"unique illumination conditions and potentially stable
   thermal environments, particularly near permanently shadowed regions."* It does
   **not** specify a surface MIR instrument, a background budget, a power architecture,
   or a service model.
2. The KISS study (arXiv:2510.24901) takes lunar interferometry across *"UV to MIR
   wavelengths"* but its baseline design is **optical** (450–850 nm, 30 cm apertures,
   100 m baseline, σ = 2 nm path measurement, 5 m main delay line, 1.9 m differential
   delay). No MIR surface instrument.
3. No search result presents a lunar MIR telescope's **background budget** — and that is
   where the real contradiction lies:
   - Sunlit lunar regolith reaches **390 K**. Wien: λ_peak = 2898/390 = **7.4 µm** —
     i.e. the *sunlit lunar surface radiates directly into the 5–14 µm band in which
     asteroid thermal emission is measured.* A surface MIR telescope on sunlit regolith
     sits inside its own foreground.
   - The cure is a **permanently shadowed region** (25–40 K ground; NTRS 20230008341
     gives south-pole night below 100 K and PSRs down to 25 K), which has no sunlight and
     therefore no solar power.
   - The power cure is an artificial-Sun: Honeybee Robotics' **LAMPS** — a 20 m
     deployable robotic solar array, ~10 kW — deployed at Mons Malapert to create
     artificial illumination and direct-to-Earth comms (NASA AMMB "Telescopes on the
     Moon", July 2026).
   - So the architecture is: **a cold telescope in shadow, powered by a mast-mounted
     array on the sunlit rim**, with a sunshade to keep the hot terrain out of the
     field. That is a specific, buildable, and genuinely unworked design.
4. And nobody has connected the platform to the **service** product: a schedulable,
   on-demand thermal-IR measurement of a *named* target, deliverable in a bounded time,
   tasked from the Minor Planet Center.

## B.3 The result the book should deliver

> The Moon helps exactly one place in planetary defence — **characterisation** — and
> within characterisation exactly one measurement: **the thermal measurement that fixes
> the diameter**, because thermal flux scales with D² and diameter sets impact energy.
> It does not help discovery (Rubin, NEO Surveyor, and the ground networks own that),
> it does not help astrometry (a ground astrometric facility measures against the
> stars; the Moon's moving-baseline geometry is strictly worse), and it does not help
> mitigation or deflection. The binding constraint on that one measurement is **not**
> the Moon's distance, its stability, or its geometry — it is the Moon's own thermal
> emission.

This is a *result*, not a concept. It is falsifiable, and it is not in the literature.

## B.4 The counter-argument the book must own
A lunar MIR station faces: no atmosphere to reject heat into, 300+ h cold survival, dust
on the optics, and a sunlit-terrain foreground that must be baffled out. A 0.5 m
space telescope at Sun–Earth L1 (**NEO Surveyor**, launch ≤ June 2028) or the proposed
**NEOMIR** can make the same measurement with no foreground and no night survival.
Against that, the lunar platform offers: no atmospheric transmission limit (so the full
5–20 µm band rather than narrow windows), on-call scheduling rather than a survey
cadence, and launch cost far below a space telescope. **The book must reach a verdict on
this, not evade it** — and the honest verdict may well be that the Moon is the wrong
site for the thermal measurement and the right site for the *interferometric shape*
measurement, where the surface stability is the binding constraint instead.

## B.5 Evidence anchors for the "decisive measurement" claim
- **arXiv:2609.15756** (14 Sep 2026, accepted A&A): JWST DDT programme on 2024 YR4;
  MIRI measurements 26 Mar 2025; NEATM / FRM / ITM / TPM models; *"the only size
  measurements that would be possible until 2028"*; a low sky background (below
  16 MJy/sr at 10 µm) thanks to a solar elongation of **120.8°**; NEO Surveyor's
  elongation floor (45°) means the target *"disappears about 25 and 15 days before the
  Earth encounter in 2028 and 2032"* (Müller et al. 2026); NEOMIR would cover 30–70°.
- **Radar shape/rotation capability**: apXiv:2509.15684 (Radio Science Letters, 19 Sep
  2025) — Canberra DSN transmit at 20 kW continuous, Parkes + ATCA + UTAS receive,
  four VLBI telescopes, multistatic, Doppler compensation at each station; the
  Australian infrastructure has characterised **>50 NEAs** by bistatic radar since 2015.
- **Spin / shape science case**: NASA Apophis Specific Action Team (2023) — radar
  observable ~mid-March to ~mid-May; for several days around close approach the SNR
  supports ~metre-scale resolution with existing facilities; spin measurements
  pre/post encounter give dynamical moment-of-inertia ratios.

---

# Appendix C — M1 RESEARCH COMPLETE (24 Nov 2026, deep-research run 20261124_220052)

Full research deliverable: `/workspace/mavis-deep-research/20261124_220052_lunar-asteroid-characterization/final_turn_001.md`
(10,004 words, 55 registry-verified sources, all figures generated by `compute_numbers.py`).

**Generator:** `/workspace/book-research/lunar-ssa/compute_numbers.py` — every headline number in the
deliverable is computed, never transcribed. It caught three of its own errors during the run
(Wien constant off by 10^3; wrong Fresnel-scale branch; an unjustified Yarkovsky extrapolation
across two orders of magnitude in diameter, now removed with an explicit caveat).

## C.1 Corrections to Appendix A and Appendix B

| Inherited claim | Verified finding |
|---|---|
| "a ~100 m lunar baseline is exactly the right length for a 50–140 m NEO at 0.1–0.2 AU" | **Wrong, and backwards.** CAPS Table 1's maximum-baseline column reproduces exactly as B_max = λ/(4θ_diam) to within 0.71 % on all 8 rows; the precision column as λ/(B·SNR) to within 2.21 %. At CAPS's 100 m design point a 50 m object at 0.2 AU spans N = 0.45 fringe spacings — the target is *unresolved*. CAPS is an astrometric-centroid instrument (design point V = 27), not a shape imager. |
| "(372) Palma ... baseline spacing required ~100 km" | **Wrong.** The VLBA baselines used were **1,200–2,300 km** (Earth scale). The ~100 km figure is the *Fresnel scale* √(dλ/2) = 104 km = 42 mas. Effective diameter 192.1 ± 2.3 km (MCMC silhouettes) or 192.1 ± 4.8 km (circular-disk phase fit). |
| "the Moon helps exactly one place: characterisation, and within it the thermal measurement that fixes the diameter" | **Wrong, and it cuts against the concept.** Sunlit regolith at 390 K radiates 27.5 W m⁻² sr⁻¹ µm⁻¹ at 10 µm. A Lambertian sphere's resolved surface brightness at 10 µm is B_λ(T_sub)/4, distance-independent. Contrast vs sunlit regolith: 0.61 (0.3 AU), 0.26 (0.5), 0.055 (1.0), 0.027 (1.3 AU) — the ground is always brighter than the target. The real foreground is the baffle: 1.6× the target at 390 K, 0.2× at 250 K, ~10⁻¹³ at 40 K. The MIR channel loses to Sun–Earth L1 on cost and complexity. |
| "Rozitis & Green (2012, MNRAS) — YORP is very sensitive to differences in shape" | **Correct but needs the correction.** The paper is Rozitis & Green 2012, **MNRAS 423, 367** (arXiv:1203.1464). Gross shape differences move Yarkovsky only ~10 % for same-size asteroids; it is *roughness beaming* that enhances Yarkovsky (tens of %, up to a factor of 2) and *YORP* that is shape-sensitive. Scaling laws: da/dt ∝ 1/(ρ_b D); dω/dt ∝ 1/(ρ_b D²). ±3 % on D → ±3 % Yarkovsky, ±6 % YORP. Θ = Γω/(εσT³_SSP). |
| "DAMIT holds models for over 10,000 asteroids, of which only 33 are NEAs" | **Superseded.** arXiv:2610.06082 (5 Oct 2026) tripled the catalogue to ~25,000 models; its sample included 881 NEAs, of which 47 received models. The 33-NEA figure was accurate as of Jan 2025. |
| "the Moon's rotation rate constrains the observation axes" | **Half right, and quantitatively the wrong way round.** Sidereal rotation 27.321661 d → baseline orientation sweeps 13.176°/day → 90° in **6.83 days**, delivering the second orthogonal baseline orientation CAPS itself requires, with no moving hardware. The lunar sky rotates **27× more slowly** than the Earth's (13.176°/day vs 15°/hour): access windows in days, no tracking needed. |

## C.2 The finding that decides the book

**Shape imaging needs a kilometre-scale baseline; astrometric centroiding does not.**
N = θ_diam·B/λ samples across the diameter. Cross-checked against ALMA's 3 Juno image
(0.042″ on a 180 mas object → N = 4.3). Required B at N = 4:

| D (m) | Δ (AU) | θ (mas) | λ/θ (m) | B (N=4) | B (N=7) |
|---|---|---|---|---|---|
| 60 | 0.1 | 0.83 | 187 | 748 | 1,309 |
| 60 | 0.2 | 0.41 | 374 | 1,496 | 2,618 |
| 60 | 0.5 | 0.17 | 935 | 3,740 | 6,545 |
| 140 | 0.1 | 1.93 | 80 | 321 | 561 |
| 140 | 0.2 | 0.97 | 160 | 641 | 1,122 |
| 140 | 0.5 | 0.39 | 401 | 1,603 | 2,805 |

Consequence: the lunar optical interferometry literature (arXiv:2510.24901, 100 m baseline,
30 cm apertures; AeSI arXiv:2408.04699) is sized for **milliarcsecond stellar astrometry**, not for
asteroids. The required lunar instrument is a **distributed 0.3–3 km surface array** — and this is
where the Moon genuinely wins, because a kilometre-scale baseline on the ground is simultaneously an
atmospheric, a metrological and a thermal-expansion problem, while on the Moon it is a construction
problem.

## C.3 The settled thesis

1. The binding gap in planetary defence is **physical characterisation**, not detection. CNEOS Sentry:
   the tabulated impact energy is "generally good to within a factor of three" because "uncertainty in
   this value is dominated by mass uncertainty". Derived: δln E = 3 δln D + δln ρ ⇒ energy to a factor
   of 3 needs D to 30 %; to a factor of 2 needs D to 14 %.
2. **Shape is the shared upstream term of both chains** (volume→mass→energy→hazard class, and
   YORP→spin state→Yarkovsky→along-track→keyhole→probability). Resolved imagery is the *preferred*
   sizing method (Jones et al.) and the worst-throughput one.
3. The physical term dominates the impact probability only at **Apophis-type horizons**, not at the
   2032 YR4 horizon (where the astrometric term dominates by three orders of magnitude). The lunar
   station earns its place for objects that will **return**.
4. **Bottke et al. 2013 Table 5 is the book's spine:** the assumed diameter alone moves the Apophis
   2036 keyhole impact probability by **433×**; the keyhole sits 4.77 σ out in the along-track tail;
   back-solved σ_ζ = 398.5 km; the Torino Level-1 threshold p ≥ 4.64×10⁻³/E moves by a factor 4.53
   across the published YR4 model set.
5. **The "beam to Earth" re-purposed as an alerting path.** The documented 2024 YR4 failure was that
   "no automated system currently alerts physical characterization sites"; IRTF observers "had not yet
   learned of the object's Torino 1 status". A sensor does not fix an alerting failure.
6. **Bounded novelty:** the lunar interferometer is 23 years old and heavily worked. The defensible
   contribution is the first quantitative, published argument for *where* in the planetary-defence
   architecture a lunar platform earns its place, plus the selection rule.

## C.4 Newly verified sources (all registry-resolved 24 Nov 2026)

arXiv: 1203.1464, 1301.1607, 2011.13632, 2610.06082, 1903.03159, 2611.05435, 2510.24901, 2408.04699,
2310.12918, 2609.03371, 2609.02571, 2509.15684, 2604.10807, 2609.10663, 2508.14412, 2607.03276,
2604.26734, 1810.01815, 2407.07173, 2611.23393, 2502.02796, 2609.15756, 2601.10666, 2506.11217,
1502.04816, 1804.05640, 1503.02650, 1102.0802, 2005.09947, 1501.05958, 2301.10348, 1305.3109.
DOIs: 10.1111/j.1365-2966.2012.20882.x, 10.1016/j.icarus.2013.02.020, 10.1007/s10569-020-09991-3,
10.3847/1538-4357/ae4ddb, 10.3847/2041-8213/adfa8b, 10.1016/j.icarus.2010.11.017,
10.3847/1538-3881/aad45b, 10.1088/2041-8205/808/1/L2, 10.1146/annurev-astro-081817-052013.
NTRS: 20030014831, 20050186565, 20250005751, 20250006886, 20250008366, 20260001844, 20220008062.
Web: NASA OIG IG-25-006 (24 Jun 2025); NASA Lunar Surface Technology; NASA Dust Mitigation;
ESA NEOCC Definitions; CNEOS Sentry Torino Scale + Object Details; ESA NEOMIR (CDF study + ESA page);
Advanced Space Lunar Sentinel SBIR Ph II; ESA SDC9 paper 258.

## C.5 Carried claims — NOT asserted in the manuscript

- The phrase "an MPC for physical characterization" was **not found** in NTRS 20250006886 on inspection.
  The manuscript asserts only what the document says: no automated alert system exists for
  physical-characterisation sites; PDCO and IAWN were discussing one; an automated alert was
  exercised for 2025 FA22 on 25 Apr 2025.
- The Moon's **libration amplitude (±8°)** was not re-verified this session; it is not used in any
  computed result.
- The exact **NGLR-1 range precisions (6.0/6.6/6.5 mm)** were not re-verified verbatim; the
  manuscript states the abstract-level "millimetre scale" only.
- The **radar "many-to-one mapping"** characterisation is carried with the source review
  (arXiv:2005.09947) named, not quoted.

## C.6 Book architecture (derived from the research)

Seven parts, thirty chapters, four appendices, one evidence ledger. Full chapter list in
`final_turn_001.md` §"The book architecture". Appendices: (A) the CAPS Table 1 re-derivation and the
corrected shape-imaging requirement; (B) the complete generated number set; (C) the prior-art map;
(D) the evidence ledger with per-source verification status.

---

# Appendix D — the detection counterfactual and the managerial frame (24 Nov 2026)

Added after the owner asked for (i) a chapter showing how the lunar approach would have *measurably
helped detect* other NEOs, with a comparison baseline, and (ii) a managerial/justified comparison
against competing approaches. Everything below is produced by `compute_numbers.py` sections 12–17,
not transcribed.

## D.1 The comparison baseline is the historical record

The counterfactual is anchored to something that can be checked rather than modelled: the JPL SBDB
records of what was actually observed and when.

| object | first observation | close approach | range | v_rel | note |
|---|---|---|---|---|---|
| 2008 TC3 | 2008-10-06 | — | — | — | named by AMAS as a Sun-ward blind-zone failure |
| 2019 OK | 2017-02-21 | 2019-07-25 | 71,355 km | 0.1058 km/s | announced three days before the pass |
| 2024 YR4 | 2024-12-25 | 2024-12-25 | 828,775 km | 13.7515 km/s | discovered on the night of the pass |
| 2024 YR4 | 2024-12-25 | 2032-12-22 | 278,333 km | 13.3072 km/s | next approach; a lunar impact |
| 99942 Apophis | — | 2029-04-13 | 38,011 km | 7.4225 km/s | inside the Earth's sphere of influence |

Source: NASA/JPL SBDB Query API (`sbdb.api`) and Close Approach Data API (`cad.api`),
retrieved 24 Nov 2026. Note **2024 YR4 was discovered on the night it passed at 828,775 km** and
**2019 OK was announced three days before it passed at 71,355 km**. Both were found late because
they arrived from the Sun-ward side, not because the instruments were inadequate. AMAS (arXiv:
2611.05435) makes exactly this claim and names 2008 TC3 and 2019 OK.

## D.2 The discovery-side quantity, reconstructed from AMAS Table 2

AMAS gives the first detectable distance from a lunar observatory and the extra lead time, for
v ≈ 20 km/s. Inverting the lead time recovers the ground limit the table implies:

| class | lunar first detectable | extra lead | implied ground limit |
|---|---|---|---|
| 30 m, city-scale | 0.05 AU | 4–5 d | 0.102 AU (0.096–0.108) |
| 140 m, potentially hazardous | 0.10 AU | ~9 d | 0.204 AU |
| 1 km, global-scale | 0.50 AU | ~6 weeks | 0.985 AU |

## D.3 The discovery baseline itself (NASA CNEOS, data current 22 Nov 2026)

| series | known | 2024 arrivals | 2025 arrivals |
|---|---|---|---|
| All NEAs | 43,212 | 2,996 | 3,383 |
| ≥ 140 m | 11,725 | 397 | 342 |
| ≥ 1 km | 883 | 2 | 2 |

The ≥ 140 m class is 27.1 % of the catalogue and its arrival rate is **falling** (397 → 342), while
the sub-140 m population still arrives at ~3,000/yr. The catalogue is nearly complete at the top and
still growing at the bottom. On Jones et al. (arXiv:2301.10348) — "Only about 15 % of NEOs have had
a spectrum measured, and fewer than percent have been imaged with radar" — about 1,759 of the 11,725
≥ 140 m objects have any physical account and about 9,966 have none.

**This is the managerial finding: for the hazard-relevant class the gap is not discovery, it is
accounting.** The book must say so rather than claim a detection capability the platform does not
have.

## D.4 Two-station ranging on the Earth–Moon baseline (new, and the strongest new result)

The Earth–Moon baseline b = 384,400 km is known to millimetres by laser ranging. Two astrometric
solutions tied to that frame turn an angular detection into a ranged one:

- sightline separation δ = (b/Δ)·sin ψ
- range error σ_Δ = Δ²·σ_θ/(b·sin ψ)

Range error in metres (ψ = 90°):

| Δ | δ (deg) | 0.1 mas | 1 mas | 10 mas | 100 mas |
|---|---|---|---|---|---|
| 0.00554 AU | 26.57 | 0.87 | 8.66 | 86.63 | 866.29 |
| 0.05 AU | 2.94 | 70.56 | 705.64 | 7,056 | 70,564 |
| 0.1 AU | 1.47 | 282 | 2,823 | 28,226 | 282,256 |
| 1.0 AU | 0.147 | 28,226 | 282,255 | 2,822,554 | 28,225,543 |

The error grows as Δ², so this is a close-approach instrument, not a catalogue instrument. It is
valid only while the target is outside the baseline (Δ > b); inside b the Moon's own ephemeris
gives the range directly, to the centimetre.

Achievable differential astrometry (CAPS centroid rule λ/(B·SNR), SNR 7): 0.2210 mas at a 100 m
baseline, 0.0147 mas at 1.5 km, 0.0074 mas at 3 km. So the 1 mas column above is the conservative
case, not the achievable one.

**At 2024 YR4's discovery-night distance of 828,775 km the range is good to 8.7 m at 1 mas, and to
about 13 cm at the 1.5 km baseline's 0.0147 mas.** No ground optical facility ranges a
non-cooperative NEO; radar can, but only within roughly 0.2 AU and only for radar-crossing objects
(the d⁻⁴ law). This is a capability that exists nowhere else on Earth.

## D.5 What each documented case would have been measured

| case | θ (mas) | aperture to resolve | matched baseline at N = 4 | V (zero phase) | range |
|---|---|---|---|---|---|
| 2024 YR4, discovery night, 828,775 km | 15.13 | 12.47 m | 40.9 m | 12.65 | 8.66 m (parallax) |
| 2024 YR4, 2028 apparition, 0.05 AU | 1.68 | 112.57 m | 369.1 m | 17.42 | 706 m (parallax) |
| 2024 YR4, 2032 lunar impact, 22,900 km | 547.6 | 0.345 m | 1.13 m | 4.85 | 1 cm (direct) |
| 2024 YR4, 2032 nominal, 3,000 km | 4,180.3 | 0.045 m | 0.15 m | 0.44 | 1 cm (direct) |
| Apophis 2029, 38,011 km | 1,763.6 | 0.107 m | 0.35 m | 1.11 | 1 cm (direct) |

V is the zero-phase magnitude with the heliocentric distance set to 1 AU and is optimistic at these
phase angles. H is the SBDB absolute magnitude; for 2024 YR4 the SBDB value 23.93 ± 0.28 differs
from the JWST value 24.14 ± 0.25 — a 0.21 mag discrepancy inside both uncertainties, carried
visibly rather than reconciled.

## D.6 The service cannot be a census (the book's self-limiting result)

- A fixed station needs a 90° baseline-orientation sweep per campaign: 6.83 days at 13.176°/day.
- With 30 % overhead: **37.4 campaigns per year**.
- Demand: 342 new ≥ 140 m objects per year (2025). Coverage: **10.9 % of the annual arrival**.
- Clearing the 11,725 known ≥ 140 m objects at 37/yr: **313 years**. A ten-year clearance would
  need 342/yr, i.e. nine times the array.

The lunar station therefore cannot be a census and must be a targeted service — which is exactly
what the platform selection rule already says. The arithmetic and the architecture agree.

## D.7 The accountability ladder (what each link is worth)

E = ½ρ(π/6)D³v², so δln E = 3 δln D + δln ρ.

| state | E uncertain by |
|---|---|
| Sentry tabulated state (D 30 %, ρ 30 %) | 2.86 — matches Sentry's "factor of three" |
| thermal-model spread removed (D 19 %, ρ 30 %) | 2.19 |
| + resolved shape (D 10 %, ρ 30 %) — requirement | 1.73 |
| + close-approach density (D 10 %, ρ 10 %) — requirement | 1.46 |
| + both at 5 % — requirement | 1.22 |

Decomposition check on the published 2024 YR4 model set: thermal model alone 1.684, density alone
2.692, product 4.535 against the published spread of 4.532 (2.16 to 9.79 Mt). The diameter and the
density contribute comparably. **Removing the thermal-model ambiguity buys half the gap; the other
half is the density, and the density is a mass measurement, not a shape.** This is the argument for
pairing the shape array with the close-approach mass capability, and it is the strongest internal
justification for the lunar platform's particular geometry.

## D.8 Consequences for the book structure

1. A new chapter in Part VI, beside the platform selection rule: **the counterfactual ledger** —
   what the lunar approach would have detected, measured against the historical record.
2. A new chapter in Part I or III: **the managerial frame** — the portfolio, the jobs to be done,
   the scorecard, and the honest losses (the Moon loses the thermal channel and the survey race).
3. A management summary in the front matter, in the register of a programme decision: the question,
   the answer, the rule, the cost class, the risk, and what the platform explicitly does not do.
4. The platform selection rule is promoted from a chapter to the book's deliverable, and is stated
   in the managerial form: for each target, return the platform, not the architecture.

## D.9 Sources added in this pass

- NASA CNEOS Discovery Statistics, cumulative NEA series `nea_vs_time.json` (data current
  22 Nov 2026), retrieved from `https://cneos.jpl.nasa.gov/stats/nea_vs_time.json`.
- NASA/JPL SBDB Query API, `https://ssd-api.jpl.nasa.gov/sbdb.api` (first observation dates,
  absolute magnitudes) and Close Approach Data API, `https://ssd-api.jpl.nasa.gov/cad.api`
  (close-approach ranges and relative velocities), retrieved 24 Nov 2026.
- Hadjara et al. 2026 (arXiv:2611.05435), Table 2, read from the full text cached at
  `evidence/amas.pdf` / `evidence/amas.txt`.
- Jones et al. (arXiv:2301.10348) for the 15 % spectrum / <1 % radar figures (already verified).

