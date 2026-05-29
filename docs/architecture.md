# Architecture Diagrams

## 1. Process Topology

```
+-----------------------------------------------------------+
| Main Process (debate.sdk.main)                            |
|                                                           |
|  +-----------------------------------------------------+  |
|  |                   MasterAgent                       |  |
|  |                 (Father / Judge)                    |  |
|  +--+-----------------------------------------------+--+  |
|     | IPC Queue 1 (Pro)           IPC Queue 2 (Con) |     |
+-----|-----------------------------------------------|-----+
      |                                               |      
+-----v-------------------+       +-------------------v-----+
| Process: Pro Subagent   |       | Process: Con Subagent   |
|                         |       |                         |
|  [ProSkill Engine]      |       |  [ConSkill Engine]      |
+----------+--------------+       +--------------+----------+
           |                                     |           
           +-------------> API <-----------------+           
```

## 2. IPC Message Flow

```
Pro Subagent                MasterAgent                 Con Subagent
      |                           |                           |
      |--- [1] ARGUMENT --------->|                           |
      |                           |--- [2] ARGUMENT --------->|
      |                           |                           |
      |                           |<-- [3] COUNTER_ARGUMENT --|
      |<-- [4] COUNTER_ARGUMENT --|                           |
      |                           |                           |
      |--- [5] ARGUMENT --------->|                           |
```
*Note: Direct Pro <-> Con communication is forbidden.*

## 3. Skill Activation Flow

```
RouterSkill
  |-- reads: Topic & Opening Statement
  |
  |-- Selects: ProSkill for Pro Subagent
  |    |-- Loads: pro_skill.skill.md + pro_skill.py
  |
  |-- Selects: ConSkill for Con Subagent
       |-- Loads: con_skill.skill.md + con_skill.py
```

## 4. Gatekeeper Flow

```
Agent `call_api()`
       |
       v
+------------------+     [Queue Full?] ---> Raise GatekeeperQueueFullError
| ApiGatekeeper    |
| (Sliding Window) |
+--------+---------+
         |
    [Rate Limit OK]
         |
         v
  Anthropic API Network Call
```

## 5. Watchdog Lifecycle

```
Session Start
      |
      +--> Spawns Subagent Process
      +--> Starts Watchdog Thread
             |
             +--> Loop:
                   |-- Wait for Ping
                   |-- If timeout > 30s:
                   |      |-- Kill Process
                   |      |-- Log Event
                   |      |-- Restart & Inject Context
                   |      +-- If Restarts > 2: Declare Forfeit
```
