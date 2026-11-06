# Live Bakers district bid on the November hotfix

A single guarded district score write on patched stock GameCore changed
Delhi's native selection to Bakers' Quarter. Delhi reserved the intended
tile and requested Craftsmanship. The preparation failed before a
construction contract was submitted, and the tile was still empty at turn 25.

## Matched selection

The shared controller loaded the archived Online turn-1 Mill study fixture
with only the isolated CSC package enabled. The fixture has diagnostic
starting conditions, including a pre-existing Granary and a population-15
Delhi. The loaded module was stock XP2 SHA
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
The controller checked that the fixture's observed facts matched the archived
control, which had closed normally on the same stock build. It verified the
save, retired package, observer and writer source archives and frozen trace.
[Hotfix comparison and original stock control](csc-ai-xp2-november-hotfix-20261106.md).

| At the decision | Stock control | Stock plus one test bid |
| --- | ---: | ---: |
| Bakers at plot 1210, before aggregation | 77,534 Q8 | 77,534 Q8 |
| Bakers at plot 1210, native aggregate | 104,621 Q8 | 104,621 Q8 |
| Adjustment to completed Bakers score | 0 | +143,858 Q8 |
| Native winner | Neighborhood, plot 1358 | Bakers, plot 1210 |
| Winning score | 248,223 Q8 | 248,479 Q8 |

The diagnostic amount places Bakers one utility unit above the matched
control winner. Frida wrote one fresh cell after building aggregation.
The native selector and exact plot present-value read both returned
248,479 Q8. The frozen trace has one write, zero errors and no pending
callbacks. It establishes score delivery and an induced choice. The amount
is a test signal and carries no claim about the value of the Stage 2 chain.

## Preparation, expiry and construction

After turn 2 the writer and observers froze. The controller advanced only
through normal finite autoplay intervals.

- The native tree decoded Bakers at 970 whole utility, reserved (26, 16)
  and accepted its Craftsmanship goal on AI turn 1.
- The same Bakers preparation remained visible through turn 10. On turn 9
  the native decorator logged contract 4 waiting 8 of 8 turns. On turn 10
  the decorator reported failure and no contract, and the Bakers tree failed.
- On turn 11 Delhi chose a new Campus plan and accepted Writing. Campus
  subsequently appears in the construction queue. The closed CityBuild and
  queue logs show no Bakers production contract or order for Delhi.
- Nine physical observations from turns 2 through 25 found the exact plot
  still owned by Delhi's player, with no district foundation and no
  Craftsmanship unlock. Delhi pursued other production during the window.

The matched control ends at turn 2. The later observations describe how
the treated AI handled its own preparation. A sustained bid and the cause
of the incomplete research remain outside the comparison.
The next construction test should start with a legal, already unlocked
Bakers candidate and available production. Live bids for a Mill, Granary
and material work still require separate delivery evidence.

## Controller and retained evidence

The fresh-control attempt reached turn 2 with a frozen zero-write trace
and restored preferences. The owned native process stayed in the background
after acknowledging its supported Exit command. After verifying the held
process identity and absence of a window or active callbacks, it was stopped
and the temporary package was retired by hash. That attempt supplied no
comparison arm. The retry used the earlier normally closed patched control.

The treatment completed normal native exit with code 0. The controller
verified all 153 preference entries and the temporary package retirement.
The installed content and pinned save/source inputs matched at teardown.
No active test owner remained.

Evidence root `Desktop/Codex/csc-gamecore-hotfix-20261106`. The first attempt
is `stock-pulse-followthrough-01`. The accepted treatment is
`stock-pulse-followthrough-02`, which retains its control-reference hashes,
native logs, and exact executed-source archive.

| Accepted receipt | SHA-256 |
| --- | --- |
| `result.json` | `cc37022b6bce0902bb417fb31fc576f6389203ddaa1f447782745a31c609d3a6` |
| `pulse/trace-frozen.json` | `ba7541633c735bde7e8c615fd518e1b1f8770499cc8ff0911155ba78b3e11523` |
| `pulse/followthrough.json` | `553cc1d9c369e8a1a19ed563bbcafc2ef23c0180986d8ac89e2db08507dce362` |

The test uses a stock research process and an isolated save. The CE
development carrier still needs its patched-host qualification.
