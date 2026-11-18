# Stage 3 transaction precision investigation — 11 November 2026

Henno requested trial coefficient 0.101 for Bakery and Tailor Stage 3 sales.
Updated both SQL registries, Bakers legacy Food modifier amount and matching
comments. Customer population continues to determine both sides of each sale.

Henno then observed in Sukritact Simple UI Adjustments a 10-pop local sale
paying 0.8 Food/Production/Gold. Adding an adjacent Bakery in a 5-pop city
raised the customer's Food to 1.9 and paid the 5-pop seller 0.9 Production/Gold.

Offline hypothesis reproduces all three observations exactly. The shared Lua
encodes target / recipient population * 10000 as binary bits. SQL applies each
bit / 10000 as a separate per-population modifier. If native code truncates each
modifier coefficient to Q8 (1/256), encoded rate 1010 becomes 23/256, paying
0.8984375 at population 10. Rate 2020 becomes 49/256, paying 1.9140625 at
population 10 and 0.95703125 at population 5. Truncating the displayed tenth
gives 0.8, 1.9 and 0.9. This is a model, not verified native engine behavior.
CSC's Suk_YieldTT.lua TTtoTable preserves supplied numeric text in this row.

Live inspection attempted with project/tools/adjacencies/tuner.py. Socket
connection to 127.0.0.1:4318 failed with PermissionError WinError 10013 from
session restrictions. No live mutation or runtime inspection completed.
Next verify native precision and consider exact binary fraction units shared
by Lua and SQL, quantizing the aggregate rate once before bit decomposition.
Keep save migration/property early-return behavior in scope if encoding changes.
