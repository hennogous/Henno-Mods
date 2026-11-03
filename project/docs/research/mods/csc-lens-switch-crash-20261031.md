# Lens-switch crash with a removed City Center — 31 October 2026

## Finding

The latest crash is a GameCore access violation while executing a city's
yield-focus command with a missing City Center district. Henno subsequently
confirmed manually removing that city's City Center. The recovered native path
matches that explanation. This differs from the earlier, fixed radio-button
shutdown crash in HavokScript.

No lens code, installed mod, save, game settings or running game was changed
during this investigation. No game was launched or crash reproduction attempted.
The green-highlight report remains unconfirmed in an intact-city game; do not
roll back the renderer or declare a separate overlay defect from this damaged
city alone.

## Preserved evidence

The game had already exited. Its native dump was preserved from
`Base/Binaries/Win64Steam/CivilizationVI.exe.dmp`, last written at 16:16:32 local
time, together with logs and installed/source lens files in:

`C:/Users/Shadow/Desktop/Codex/csc-lens-switch-crash-20261031-161632/`

The dump is 296,902 bytes and contains an actual ExceptionStream. Its context
must be used instead of the dump thread's later crash-handler snapshot context.
Thread 23460 reports `0xC0000005`, reading address `0xc0` at
`GameCore_XP2_FinalRelease.dll+0x52d00`. The faulting instruction is
`mov r8d, dword ptr [rdx]`, with original RDX `0xc0`.

The installed GameCore SHA256 is
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`, matching
the inspected Ghidra image. PE timestamp also matches the captured module.

## Verified native path

An offline helper mapped exact local images and captured stack bytes as
non-executable data and called Windows `RtlVirtualUnwind`. It opened no target
process and executed no target code. Twelve frames were recovered to thread
startup, then the walk stopped at a zero return address. Raw stack pointer
guesses are not used as call frames.

Relevant actual frames, expressed as GameCore RVAs:

```text
0x52d00   map-coordinate read through RDX=0xc0
0x191616  District::Instance::GetComponentID
0x133a9   City::Commands::BaseHandler::Start
0x67f270  City::Commands::SetFocus::Start
0x13ea1   City::Commands::Manager::Start
0x33f44   Messages::CityCommand::Execute
0x37e67   Messages::Manager::ReceiveMessage
0x37358   Messages::Manager::ProcessMessages
```

The inspected base handler obtains the city's default district when no district
argument is supplied, then calls the district's component-ID accessor without
checking the returned pointer. The district pointer is zero in this failure;
the accessor passes its coordinate member at null plus `0xc0`, matching the
exception exactly. `SetFocus` is the normal favored/disfavored city-yield command.

The network log's final messages are CityCommand 2 requests. The installed
Quarter logs identify the 20%/80% build, not the subsequent 20%/60% source change.
The last logged CSC close completed its own checkbox update. The faulting stack
contains no renderer or HavokScript radio-button frame.

## Green highlights and next check

Henno also observed unexpected green tiles when switching vanilla lenses to
Bakers'. The Quarter palette has blue/red/yellow/white, so green merits a
separate valid-world check. The borrowed Appeal carrier can invoke the vanilla
Appeal painter; however, the crash and invalid city make stale display state
another plausible explanation. The dump does not identify which layer painted
those tiles or prove that they are a separate CSC rendering defect.

Retest vanilla-to-Bakers switching with an intact City Center before changing
overlay behavior. Keep the accepted direct RGBA renderer, selected-city
placement coverage and current 20%/60% source styling. If green persists in that
valid state, capture the source lens, affected plots and current renderer logs
and investigate the carrier painter independently. Do not attempt to support a
deleted City Center by adding an unrelated lens workaround.
