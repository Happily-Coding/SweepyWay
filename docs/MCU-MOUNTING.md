# MCU mounting — what the buyer does, and what the factory does

The nice!nano is **never placed by JLCPCB**. That is deliberate, not a gap in the order: the module is
the one part a user wants to own (it carries their firmware, and it is the expensive and
supply-constrained piece). What matters is that **the buyer never needs a soldering iron**. Two
supported ways to get there.

## Option A — solderless spring headers (Typeractive), nothing fitted at the factory

JLCPCB assembles the diodes and the three connectors and leaves the MCU area empty. The buyer presses
Typeractive's solderless spring headers into the 2 × 12 socket holes and pushes the nice!nano on.

* factory work: none in the MCU area
* buyer work: press in headers, plug in the module — **no iron**
* PCB requirement: the 24 socket holes must accept the spring pins. Measured on the published board:
  **⌀1.0 mm drill with a ⌀1.7 mm plated pad** (2 rows at x ±7.62 mm, 2.54 mm pitch). Spring pins need
  a plated hole they can grip, so this is the number to check against whichever header is bought.
* consequence: the board ships with 24 empty plated holes, and the user can swap the MCU freely.

## Option B — factory-fitted headers, buyer plugs the module in

JLCPCB fits the 2 × 12 headers (through-hole, or female headers so the module can be removed) and the
buyer simply pushes the nice!nano into them.

* factory work: 24 through-hole joints — **not** the SMT line. JLCPCB's standard PCBA is SMT; THT is
  a separate service whose availability must be confirmed per order (do not assume it).
* buyer work: plug in the module — **no iron**
* if female headers are used, the module stays removable and swappable, same as Option A

## What is excluded from the BOM either way

`mcu_nice_nano` is in the BoM as `Assemble=no` (`HAND-SOLDER`). That flag is what stops JLCPCB from
looking for a part it cannot place; it does **not** mean the buyer must solder. The `header-preview_nano`
footprints in the PCB are virtual previews (0 pads) and carry no order meaning.

## The one soldering step that is *not* the MCU

The 32 hotswap sockets per half are SMD and **can** be factory-fitted — but only by consignment (mail
the sockets to JLCPCB, see `docs/ORDER-READINESS.md` B4), because every choc socket code in their
catalogue is out of stock or discontinued. If the sockets are consigned, the buyer's only assembly is
pressing switches and the MCU into place.

## Summary

| step | Option A (spring headers) | Option B (factory headers) |
|---|---|---|
| JLCPCB places the MCU | no | no |
| JLCPCB work in the MCU area | none | 24 THT joints (confirm THT service) |
| buyer needs a soldering iron | **no** | **no** |
| MCU swappable later | yes | yes (if female headers) |
| order complexity | lowest | + THT service question |
