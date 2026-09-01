# Aurelia → RCI Embodiment Contract

## Purpose

Aurelia is the cognitive and character-intelligence layer. The Robotic Character Interface (RCI) owns physical behavior planning, robotics, deterministic motion safety, hardware gateways, firmware validation, and actuators.

The cross-repository boundary is `rci.character_response.v1`.

```text
Verified Aurelia CognitiveCycleResponse
  -> AureliaEmbodimentAdapter
  -> CharacterResponse
       -> SpeechIntent
       -> ExpressionIntent
       -> optional MotionIntent
  -> RCI Behavior Planner
  -> RCI Motion Request
  -> RCI Trajectory Planner
  -> RCI Motion Safety Supervisor
  -> validated robot command
  -> MCU / firmware safety
  -> actuators
```

## Non-negotiable invariant

Aurelia never emits actuator commands. `CharacterResponse` contains no joint targets, servo angles, PWM values, pulse widths, motor commands, trajectories, or hardware timing parameters.

`MotionIntent` is semantic only. It contains a high-level cue (`listen`, `acknowledge`, `present`, `caution`, `celebrate`, `think`, or `none`) and a character style. Its disposition is only `optional` or `none`; Aurelia cannot require physical motion.

RCI may ignore, downgrade, replace, or reject a motion cue based on system state, character policy, robot geometry, trajectory feasibility, health, E-stop state, or any deterministic safety rule.

## Eligibility gate

`AureliaEmbodimentAdapter` fails closed unless all of the following are true:

1. final response passed the verification firewall and is safe to publish;
2. the immutable DecisionReceipt says verification passed;
3. the cognitive cycle was committed through RuntimePersistence;
4. typed persona and legacy compatibility presentation fields agree;
5. final speech text is non-empty.

Durability is reported separately. Simulation/tests may use committed in-memory persistence, while the canonical `aurelia-server` uses file-backed SQLite and therefore reports durable persistence.

## Traceability

Each payload carries:

- deterministic schema version;
- interaction correlation ID derived from the decision ID;
- decision ID;
- source character;
- verification state;
- persistence commit/durability state.

RCI must create its own downstream behavior/trajectory/command identifiers and preserve the incoming correlation/decision IDs in audit lineage.

## Schema

The machine-readable schema is committed at:

`schemas/rci-character-response-v1.schema.json`

Both repositories should validate the same fixture/schema contract before physical integration is enabled.
