"""Read back installed assets, accepting AE-regenerated DDS headers/mips only when top pixels match."""
from publish_cafe_props import *
import struct
def decode_top(path):
    raw=path.read_bytes();assert raw[:4]==b'DDS ';h,w=struct.unpack_from('<II',raw,12);size,flags,fourcc,bits,r,g,b,a=struct.unpack_from('<8I',raw,76)
    offset=128
    if fourcc==struct.unpack('<I',b'DX10')[0]:
        dxgi=struct.unpack_from('<I',raw,128)[0];offset=148
        if dxgi==61:return np.frombuffer(raw[offset:offset+w*h],np.uint8).reshape(h,w)
        assert dxgi in (28,29);return np.frombuffer(raw[offset:offset+w*h*4],np.uint8).reshape(h,w,4)[:,:,:3]
    if bits==8 or len(raw)<w*h*2:return np.frombuffer(raw[offset:offset+w*h],np.uint8).reshape(h,w)
    assert bits==32,(bits,flags,fourcc)
    pixels=np.frombuffer(raw[offset:offset+w*h*4],'<u4').reshape(h,w)
    channels=[]
    for mask in [r,g,b]:
        shift=(mask&-mask).bit_length()-1;channels.append(((pixels&mask)>>shift).astype(np.uint8))
    return np.stack(channels,axis=-1)
def main():
    results=checks();verification=[]
    for k in ['B','N','G','M','AO']:
        p=MOD/'Textures'/f'CSC_Props_Shared_01_{k}.dds';actual=decode_top(p);expected=np.array(Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB' if actual.ndim==3 else 'L'))
        err=int(np.abs(actual.astype(int)-expected.astype(int)).max());print(k,'pixel error',err,flush=True);assert err<=1
        verification.append(dict(channel=k,max_pixel_error=err,installed_sha256=sha(p)))
    for ident in IDS:
        for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:assert sha(OUT/(ident+ext))==sha(MOD/folder/(ident+ext))
    for name,folder in [('CSC_ALL_Stage_4_Cobble_Decals.mtl','Materials'),('CSC_ALL_Stage_4_Cobbles_B.tex','Textures'),('CSC_ALL_Stage_4_Cobbles_B.dds','Textures')]:assert sha(OUT/name)==sha(MOD/folder/name)
    for p in STAGE.rglob('*'):
        if p.is_file():assert sha(p)==sha(SHARED/'Current'/p.relative_to(STAGE))==sha(SHARED/'Releases'/RELEASE/p.relative_to(STAGE))
    entries=ET.parse(MOD/'XLPs/CSC_Tilebases.xlp').findall('m_Entries/Element');assert all(sum(txt(e,'m_EntryID')==ident for e in entries)==1 for ident in IDS)
    report=dict(release=RELEASE,assets=results,source_directory=str(SOURCE),existing_ae_assemblies_not_written=True,surface_slots=list(range(10,16)),occupied_surface_pixels_preserved=True,other_AO_pixels_preserved=True,opacity_emission_sheet02_source_unchanged=True,atlas_rebuild_hashes_match=True,installed=True,cook_tested=False,in_game_tested=False,placement='Review proposal only; AE owns final positions and duplicates.',dds_readback=verification,installation_note='Texture watcher regenerated runtime DDS headers/mips after canonical publication. Installed top-mip pixels separately compared against published PNGs; exact staged binary hashes are not expected.')
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2));print('CAFE INSTALL VERIFIED',flush=True)
if __name__=='__main__':main()
