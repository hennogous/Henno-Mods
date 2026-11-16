# Ordinary specialist income in the shared economy

16 November2026. G3 staffing slice, roadmap1.4/2.1/2.2. Services deferred.

## Native mechanism

Plot `GetYield` RVA5f6d0 calls Rules::Yields::GetYield37ec60. On a completed
non-City-Center district, it sums `District_CitizenYieldChanges` and the citizen
rows of buildings returned by GetBuildingsAtLocation10b6e0. That location query
uses physical building locations and does not filter pillage. City
GetYieldFromTiles133780 multiplies each worked plot yield by assigned workers
and256 for its Q8 total.

WorkerCapacity10fff0 is separate: it requires the appropriate working city and
completed, unpillaged district, then adds district capacity and unpillaged
building slots. A pillaged building can therefore lose slots while its native
per-worker rate remains in the district's sum. This is a static code finding;
the lifecycle of actual assignments remains an observed input.

Reference DLL SHA256324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c;
runtime SHA256092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f.
The previously qualified full .text parity applies. Private decompilation records:
`staffing-native-plot-yield.json` and `staffing-native-city-workers.json`, under
`C:/Users/Shadow/Desktop/Codex/csc-ai-ordinary-economy-20261116`.

## Model implementation

Facts caches the loaded native citizen-yield definitions. At a Quarter it selects
only ordinary Stage2/3/4 producers, preserving intrinsic specialist Gold when the
optional transaction-Gold layer is off. Service buildings and their rates are
excluded. It reads actual worker count and a fresh receiving-city observation;
unavailable assignment ownership earns no assumed income.

The model credits ordinary existing per-worker rates for those observed workers.
A missing ordinary building can improve the same assignments after construction.
A present building's citizen rows are already baseline, including when pillaged;
repair must not add those rows again. A new empty Quarter has zero observed
specialists, and more slots never create forecast workers automatically.

This modifies AI accounting only. Gameplay SQL, payouts, assignments and slots
are unchanged. Five actual-SQL→Facts→Model regressions cover0/1/2 workers,
Service exclusion, intrinsic Tailor Gold with transaction Gold off, a future Cafe,
missing assignment ownership and the present/pillaged distinction.

`staffing250-01` qualifies the current reader/model on the mature turn250 world:
22 Quarter chains,28 observed specialist workers and30 ordinary staffing streams.
All10,954 native effect rows,137 fixed rows and the67-city population refresh
still match the original package. The zero-price pass publishes no bids or orders,
advances no AI turns, and closes/restores with exit0. Astra independently reviews
the five staffing regressions and11 joint-ledger cases. Full suites pass40
transaction tests and113 economy tests.

The facts/model command takes3.700 seconds wall time for five players, including
console discovery/transport and logging. Native yield pricing and customer-site
search are absent from that diagnostic, so G5 will measure the complete priced
path after integration. The complete G3 customer-world/route/adjacency integration
and G4 native overlap remain open.
