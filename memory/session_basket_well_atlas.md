# Basket / shared well atlas migration — 26 October 2026

User approved #2 from art cleanup: migrate sole CSC_ALL_Props_E/ET consumers to
current shared prop atlas, preserve well tinting, retire obsolete maps/materials.
Completed and installed. Tools project/tools/art/migrate_legacy_prop_atlas.py and
its _blender.py companion. Outputs Desktop/Codex/Basket-Well-shared-atlas-20261026.
Archive Desktop/Archive/CSC-basket-well-atlas-20261026 contains original mod files,
three source masters, original Current library/CURRENT.json and registrations.

Current release2026-10-26_Shared_01_r045, publishedCurrent+Releases+CURRENThash.
Existing legacy paint (no new artwork) copied/resampled with all companion maps
into verified free slots40wood/tint,41basket,42limestone,43darkwellinterior.
Tint mask newCSC_Props_Shared_01_T, black outside newwood mask. New material
CSC_ALL_Props_01_T clonesShared01 and bindsT. ExistingShared01unchanged.
AO preservedlegacy patches in previouslyfree cells: basket[1408,384,1536,512],
well[896,128,1024,256],wellPIL[512,256,640,384]. Prior allocated basket authoringAO
cell preserved. All previoussurface/AO pixels outside thesecells unchanged.
Manifest/sourcepatches/2048masters updated, portablepack_basket_well.py exactrebuild
verified, libraryfileshashed. Shared01_E remainsreserved/preservedexplicituser.

RuntimeBasketAST nowShared01; sharedCSC_ALL_is_WellAST nowShared01_T.
Only materialname replacements; allstateflags/emissionflags/placementsunchanged.
NativeCSC_TAILORS_Basket506v,CSC_ALL_Well138v,CSC_ALL_Well_PIL280v: UV1/UV2only.
Position/topology/normals/tangents/emissionUV3 preserved, nativebonebindingroundtrip.
Three savedsources now Props/Tailors/CSC_TAILORS_Basket.blend,
Props/CSC_ALL_is_Well.blend andProps/CSC_ALL_is_Well_PIL.blend. Native-derived
editableExport+Review, realstaticweights/customnormalmetadata, localtextures,
exports/<geo>CN6FGXGEO. Installed3savedfilevalidatorsPASS; sourceCN6nativeparityPASS.

Archived2oldMTL +7TEX/DDS pairs (B,B_T,N,AO,M,G,T). Added1MTL+1TEX/DDS pair:
net13fewerfiles,1fewermaterial,6fewertexturefamilies,~16MiBlessCSCsourcefiles.
BothisolatedTilebasescooksPASS before5,312,000bytes/after5,310,464bytes,1536bytesless.
NoXLPentrychange.520unaffectedruntimearthashesunchanged. Retiredoldfilesabsent,
newTintMTL/TEXruntime-reachable, allCurrent/Releasehasheschecked. NewDDSAErecord
addedalongsideTEX;originalcachearchived. Nativegameviewnotreviewed; sixpaired
renderimages inspected andmatchappearance (greentesttintinclpillagedwell).

ExistingBase09oldCSC_BAKERS_Wellmissingmaterial remainsunchanged andreported.
Do not infer thatwellvariantwasreplaced; onlysharedCSC_ALL_is_Well migrated.
Cleanup audit originalscriptreport assumesold190filelist; callrun(output,False)
for currentinventories, notitsdatedhardcodedHTMLreport. HistoricalL2installer
baselineisobsolete aftercleanup/thismigration; neverreplayblindly.
CURRENT 26 October follow-up: newer authored Tailors basket installed; r046
supersedes r045 basket additions. See project/docs/art/tailors-basket-replacement-20261026.md.
Active Props/Tailors/CSC_TAILORS_Basket.blend is now the 169-authoring/351-exported
vertex basket (260 triangles), original Textile Workshop revision11 source unchanged.
Slot41 and AO [1408,384,1536,512] reclaimed; original AO [1280,384,1408,512] retained.
Older master, exports and original Props/_archive/CSC_ALL_Basket files archived in
Desktop/Archive/CSC-older-tailors-basket-20261026. No placements/state changes.
Both cooks pass; 5,120 bytes cooked saving. Installed source/export and 537 other
runtime hashes pass. No live game/AE verification. Older r045 notes below are history.

