# How native Economic funds a requested plot

Problem **1.5** needs more than a winning Quarter site: the AI must fund and
execute its purchase. This static investigation explains the savings accounts
seen in Nicopolis's eleven unsuccessful attempts ([AI-C141](../../civ6-ai/findings.md#ai-c141)).
It does not establish a new paid purchase or change CSC's bids.

## Main result

Economic allocates the difference between actual Treasury Gold and its own
accounted balance, rather than simply dividing displayed Gold per turn:

```text
unaccountedGoldQ8 = treasuryGoldQ8 - economicCurrentBalanceQ8
allocate that difference across four weighted savings accounts
clamp/transfer accounts and send allocation residual to slush
economicCurrentBalanceQ8 = treasuryGoldQ8
process spending contracts, Great People, routine plots and tribe payments
```

The four accounts are slush, units, plots and Great People. Values are Q8
Gold: 256 represents one Gold. Shares are also quantized to Q8 before the
multiply. The shipped default weights 3/4/1/1 are starting preferences, not
guaranteed shares of the displayed income. Initialization reads leader
preferences and agenda changes can alter them; measure the live weights.

The **plot account is capped at 150 Gold** (`0x9600` Q8). Overflow moves to
slush. This is an account cap, not a maximum purchasable tile price. Targeted
purchases can also draw from slush after satisfying their separate plot-fund
hurdle. If no Great Person class is available, that account moves to slush too.

Negative balance changes can reduce accounts. Resulting negative account
balances are clamped to zero; a remaining slush deficit clears the accounts if the bank
is nonpositive, otherwise it draws down the other accounts in vector order.
Known spending reduces the accounted balance as well as its account/slush,
so it is not charged again as an unexplained loss at the next allocation.
Plot-purchase paths perform corresponding accounting inline; observing only
the named `Spend` function would miss those debits.

## Binary and static evidence

Ghidra reference SHA-256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Its complete file-backed `.text` was previously byte-matched to installed
patched Steam XP2 SHA-256
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Image base is `0x180000000`; addresses below are RVAs for that identity.

| Routine / location | What it establishes |
| --- | --- |
| Economic constructor `455820` | Serialized field labels, including current balance, saving weights and savings |
| `AnalyzeIncome` `456a50` | Income/maintenance analysis; not the savings allocation write |
| `DoTurnActivate` `457120` | Treasury difference, four-account allocation, transfers and spending order |
| `45733c`–`457368` | Plot-account cap and overflow transfer |
| `Initialize` `4577b0` | Leader preference loading and initial account/balance setup |
| `InitializePostLoad` `457b30` | Repairs retained contract handles; does not reset these accounts |
| `Spend` `458c60` | Category/slush debit and accounted-balance decrement |

Named layout observations, not a portable API:

| Field | Offset |
| --- | --- |
| Economic's player pointer | `+0x98` |
| Economic accounted Gold balance, Q8 | `+0x120` |
| Sum of savings weights | `+0x1c8` |
| Savings weight array pointer | `+0x1e0` |
| Savings account array pointer | `+0x250` |
| Player Treasury pointer | `+0x780` |
| Treasury actual Gold balance, Q8 | `+0xa8` |
| Treasury cached net income | `+0xd8` |

Account indices are slush 0, units 1, plots 2 and Great People 3. Native
receivers, vector lengths, pointer validity and instruction identities must be
checked before any new runtime observer relies on these offsets.

Local captured pseudocode is in
`Desktop/Codex/csc-ai-problems-1-2-20261110/economic-budget-static-20261111/`.
The complete three primary decompilations are retained as
`economic-analyze-income.json`, `economic-turn-activate.json` and
`economic-spend.json`. Constructor, initialization and post-load were separately
rechecked in Ghidra and retained alongside them. Astra independently reviewed
the allocator and accounting.

## Limits and next measurement

Activation has priority, active-flag and player-class gates. The inspected
spending body skips humans. This is not proof of one allocation per global
turn. Reload does not itself imply that the whole Treasury is newly allocated.
The 150-Gold cap is statically established; it has not yet been observed live.

Nicopolis's purchase observer measured quote and savings at the attempt, but
did not capture actual Treasury or allocation history. This result supplies a
mechanism to test; it does not retrospectively measure those missing values.
Higher request values can also change which competing spending contract acts
first. Do not infer that site scores can never affect funds available later.

For the next qualified purchase fixture, capture actual bank, accounted balance,
all four accounts and live weights before and after allocation, then the
targeted quote, command validation, debit and ownership transition. Verify the
account reconciliation and keep displayed income/maintenance separate. The
boundary before managed-contract processing at `4574a6` is a static observer
candidate, not an installed or verified runtime hook.

## Runtime attempt balances: the same Nicopolis start through 206

`nicopolis-bank-attempt-01` used the same exact turn-200 Continents save and
CE carrier as AI-C141, with current main CSC scanner/publisher. It advanced
six turns through the shared controller and closed normally: exit zero,
preferences restored, no remaining owned processes, exact packages retired.
WildW's `develop` was checked before this test and remained at
`2986a746b396eb93aad14f9afffb043a09c2c489`; no upstream PR was created.

The existing read-only purchase observer now captures the saved Economic
receiver at its audited `TryPurchasePlot` savings boundary (`45918f`). It
checks that the receiver's savings base equals the saved slush pointer and
that base+8 equals the saved plot pointer. Four live weights must sum to the
recorded total. Fingerprints cover the callback and receiver-saving prologue.
Unreadable memory, mismatched layout or invalid weights latch a diagnostic
fault without adding a zero-filled receipt. Synthetic negative fixtures
verify fault streaming, suppression of later callbacks and detachment.

| Attempt turn | Quote, Gold | Actual bank, Gold | Accounted balance, Gold | Slush | Units | Plots | Great People |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 204 | 145 | 60.00390625 | 60.00390625 | 0 | 0 | 0 | 60.00390625 |
| 205 | 145 | 44.28515625 | 44.28515625 | 0 | 0 | 0 | 44.28515625 |

Weights were **3/4/1/1**, total 9, at both checks. Unaccounted balance was
zero at those instants. This does not mean zero income or establish the
preceding allocation history. Positive Great People savings do not prove
an available Great Person purchase or that its availability check ran here.
At both captured attempts **actual Treasury was below the tile price**, in
addition to the failed plot/slush gates. Raising the site bid alone cannot
make an unaffordable purchase legal at that point.

All 22 purchase and one district-selector receipts exactly matched the
streamed journals. Removing only the six added accounting fields leaves the
same purchase records as the first two attempts of AI-C141. The turn-203
selector result is identical too. There were no native observation faults,
no paid-command receipts, and plot 401 was still unowned and empty at 206.
The observer did not measure a complete allocation cycle or a successful
purchase; the 150-Gold cap remains a static finding.
Astra independently checked the exact receipts, streams, staged source,
cleanup and negative fixtures. The observed rejection remains the earlier
plot-fund gate; command affordability was not reached by these observations.

Current scanner SHA-256:
`5e20093b864b083ec2fcade73c98d3912cd918e7e2e4a8bcff15a4fe37d5573e`.
Observer SHA-256:
`98470b8fd76ece4e7c6d2d464100982fc316aa10f79c22c97b1de163592678bf`.
Purchase trace SHA-256:
`cb805455eec31c38d886281ca67736afa7ec0818ec6898e551d6ccd26f0075fe`.
Selector trace SHA-256:
`a83039f7afad090f1867aad3fbd0da1f349a29964de8321c9c4bb2d509a40475`.

See [AI-C144](../../civ6-ai/findings.md#ai-c144). Next qualify an actually
affordable, credible Quarter footprint and its native comparison/request;
observe payment, ownership and construction without changing the Treasury.
These receipts explain this failed fixture, not a general need to subsidize AI.
