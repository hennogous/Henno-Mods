/* Independent Windows/GS delivery prototype. Only MinHook is third-party code.
 * Civ selects this proxy through GameCores; no injector, daemon or tuner is
 * needed by the package. The ordinary score hook never calls Lua or game APIs.
 * This is a delivery experiment, not calibrated CSC AI policy. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include "MinHook.h"
#include "target_identity.h"

#ifdef CSC_CE_INTEGRATION
#define API_NAME(suffix) "CE_AIDistrictScores" suffix
#else
#define API_NAME(suffix) "CSCBridge" suffix
#endif

#define CAPACITY 4096
#define INVALID_SCORE (-2559744)
typedef struct { int player, city, district, plot, delta; } Entry;
typedef struct { Entry key; int base, result; } Sample;
typedef struct { int version, width, height, districts, count, allowed[64]; Entry entries[CAPACITY]; } Policy;
static SRWLOCK lock = SRWLOCK_INIT;
static Policy staging, policy;
static LONG enabled, generation, calls, matched, changed, faults;
static int staging_valid, sample_count, hooks_ready;
static Sample samples[64];
static HMODULE original;
static uintptr_t original_base;
static void *(__cdecl *original_create)(void);
static void (__cdecl *original_destroy)(void *);
typedef int *(__cdecl *NetFn)(int *, unsigned, int *, int, int, void *, void *);
static NetFn original_net;
static void (__cdecl *original_register)(void *);
extern void bridge_net_entry(void);

/* Resolve only public HKS exports. No copied HKS structs or CE implementation. */
typedef int (__cdecl *LuaFn)(void *);
static void (__cdecl *push_closure)(void *, LuaFn, int, const char *, int);
static void (__cdecl *set_field)(void *, int, const char *);
static int (__cdecl *check_integer)(void *, int);
static void (__cdecl *push_integer)(void *, int);
static const char *(__cdecl *push_string)(void *, const char *, ...);

static int readable(const void *p, size_t bytes, int write) {
    MEMORY_BASIC_INFORMATION m; uintptr_t start=(uintptr_t)p, end=start+bytes;
    if (!p || !bytes || end<start || VirtualQuery(p,&m,sizeof m)!=sizeof m ||
        m.State!=MEM_COMMIT || (m.Protect&PAGE_GUARD) || end>(uintptr_t)m.BaseAddress+m.RegionSize) return 0;
    DWORD mode=m.Protect&255;
    return mode==PAGE_READWRITE || mode==PAGE_WRITECOPY || mode==PAGE_EXECUTE_READWRITE ||
        mode==PAGE_EXECUTE_WRITECOPY || (!write && (mode==PAGE_READONLY || mode==PAGE_EXECUTE_READ));
}

static int adjusted(int base, int delta, int *result) {
    int64_t sum=(int64_t)base+delta; *result=base;
    if (!base || base<=INVALID_SCORE || (delta<0 && base<=-1048576)) return 0;
    if (delta<0 && sum<-1048576) sum=-1048576;
    /* Retain room for the native positive district preference factor. */
    if (sum>INT_MAX/2 || sum<INT_MIN || sum==INVALID_SCORE) return 0;
    *result=(int)sum; return 1;
}

int *bridge_net(int *out, unsigned district, int *time, int ready, int horizon,
                void *plot, void *city, unsigned char *row, void *caller) {
    Entry entry; int found=0, epoch=0;
    InterlockedIncrement(&calls);
    if (InterlockedCompareExchange(&enabled,0,0) && caller==(void *)(original_base+0x3e30be)) {
        AcquireSRWLockShared(&lock);
        if (enabled && readable(city,0xdc,0) && readable(plot,0x2c,0) && readable(row,0x78,0)) {
            int player=*(int *)((char *)city+0xd8), cid=*(int *)((char *)city+0xa8);
            int x=*(short *)((char *)plot+0x28), y=*(short *)((char *)plot+0x2a);
            if (player>=0 && player<64 && policy.allowed[player] && x>=0 && x<policy.width && y>=0 && y<policy.height &&
                *(int *)(row+8)==x && *(int *)(row+12)==y && *(short *)(row+0x70)==player &&
                *(int *)(row+0x74)==cid && row[0x55] && (row[0x5a]||row[0x57])) {
                for (int i=0;i<policy.count;i++) {
                    Entry e=policy.entries[i];
                    if (e.player==player && e.city==cid && e.district==(int)district && e.plot==y*policy.width+x) {
                        entry=e; epoch=generation; found=1; break;
                    }
                }
            }
        }
        ReleaseSRWLockShared(&lock);
    }
    int *returned=original_net(out,district,time,ready,horizon,plot,city);
    if (!found) return returned;
    AcquireSRWLockExclusive(&lock);
    if (enabled && generation==epoch) {
        matched++;
        if (returned!=out || !readable(out,4,1)) { faults++; enabled=0; }
        else {
            int base=*out,result;
            if (adjusted(base,entry.delta,&result)) {
                if (changed>=4096) { faults++; enabled=0; }
                else { *out=result; changed++; if(sample_count<64) samples[sample_count++]=(Sample){entry,base,result}; }
            }
        }
    }
    ReleaseSRWLockExclusive(&lock);
    return returned;
}

static int integer_result(void *L,int value) { push_integer(L,value); return 1; }
static int l_begin(void *L) {
    int v=check_integer(L,1),w=check_integer(L,2),h=check_integer(L,3),d=check_integer(L,4),ok;
    AcquireSRWLockExclusive(&lock); enabled=0; generation++;
    ok=v>policy.version && w>0 && w<=256 && h>0 && h<=256 && d>0 && d<=4096;
    memset(&staging,0,sizeof staging); staging_valid=ok;
    if(ok) { staging.version=v; staging.width=w; staging.height=h; staging.districts=d; }
    ReleaseSRWLockExclusive(&lock); return integer_result(L,ok);
}
static int l_allow(void *L) {
    int p=check_integer(L,1),ok; AcquireSRWLockExclusive(&lock);
    ok=staging_valid && p>=0 && p<64;
    if(ok) staging.allowed[p]=1;
    else staging_valid=0;
    ReleaseSRWLockExclusive(&lock); return integer_result(L,ok);
}
static int l_entry(void *L) {
    Entry e={check_integer(L,1),check_integer(L,2),check_integer(L,3),check_integer(L,4),check_integer(L,5)};
    AcquireSRWLockExclusive(&lock);
    int ok=staging_valid && staging.count<CAPACITY && e.player>=0 && e.player<64 && staging.allowed[e.player] &&
        e.city>=0 && e.district>0 && e.district<staging.districts && e.plot>=0 && e.plot<staging.width*staging.height &&
        e.delta>=-262144 && e.delta<=1048576 && e.delta!=0;
    for(int i=0;ok && i<staging.count;i++) {
        Entry a=staging.entries[i];
        if(a.player==e.player && a.city==e.city && a.district==e.district && a.plot==e.plot) ok=0;
    }
    if(ok) staging.entries[staging.count++]=e; else staging_valid=0;
    ReleaseSRWLockExclusive(&lock); return integer_result(L,ok);
}
static int l_commit(void *L) {
    AcquireSRWLockExclusive(&lock); int ok=staging_valid && hooks_ready && !faults;
    if(ok) { policy=staging; changed=matched=sample_count=0; generation++; enabled=1; }
    staging_valid=0; ReleaseSRWLockExclusive(&lock); return integer_result(L,ok);
}
static int l_disable(void *L) {
    AcquireSRWLockExclusive(&lock); enabled=0; staging_valid=0; generation++;
    ReleaseSRWLockExclusive(&lock); return integer_result(L,1);
}
static int l_status(void *L) {
    char output[16000];
    AcquireSRWLockShared(&lock);
    int n=snprintf(output,sizeof output,"{\"abi\":1,\"ready\":%d,\"enabled\":%ld,\"generation\":%ld,\"version\":%d,\"entries\":%d,\"calls\":%ld,\"matched\":%ld,\"changed\":%ld,\"faults\":%ld,\"samples\":[",hooks_ready,enabled,generation,policy.version,policy.count,calls,matched,changed,faults);
    for(int i=0;i<sample_count;i++) {
        Sample s=samples[i];
        n+=snprintf(output+n,sizeof output-n,"%s[%d,%d,%d,%d,%d,%d]",i?",":"",s.key.player,s.key.city,s.key.district,s.key.plot,s.base,s.result);
    }
    snprintf(output+n,sizeof output-n,"]}");
    ReleaseSRWLockShared(&lock); push_string(L,"%s",output); return 1;
}
static void register_bindings(void *L) {
    struct {const char *name;LuaFn fn;} bindings[]={
        {API_NAME("Begin"),l_begin},{API_NAME("Allow"),l_allow},{API_NAME("Entry"),l_entry},
        {API_NAME("Commit"),l_commit},{API_NAME("Disable"),l_disable},{API_NAME("Status"),l_status}};
    for(unsigned i=0;i<sizeof bindings/sizeof bindings[0];i++) {
        push_closure(L,bindings[i].fn,0,bindings[i].name,0); set_field(L,-10002,bindings[i].name);
    }
}
static void hook_register(void *L) { original_register(L); register_bindings(L); }

static int verify_file(const wchar_t *path) {
    BCRYPT_ALG_HANDLE alg=NULL; BCRYPT_HASH_HANDLE hash=NULL; DWORD object_size=0,received=0;
    unsigned char digest[32],buffer[65536]; char hex[65]; int ok=0;
    HANDLE file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE) return 0;
    if(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,NULL,0)<0) goto done;
    if(BCryptGetProperty(alg,BCRYPT_OBJECT_LENGTH,(PUCHAR)&object_size,sizeof object_size,&received,0)<0) goto done;
    unsigned char *object=HeapAlloc(GetProcessHeap(),0,object_size);
    if(!object) goto done;
    if(BCryptCreateHash(alg,&hash,object,object_size,NULL,0,0)>=0) {
        ok=1;
        for(;;) {
            DWORD count;
            if(!ReadFile(file,buffer,sizeof buffer,&count,NULL)) {ok=0;break;}
            if(!count) break;
            if(BCryptHashData(hash,buffer,count,0)<0) {ok=0;break;}
        }
        if(ok) ok=BCryptFinishHash(hash,digest,32,0)>=0;
        BCryptDestroyHash(hash);
    }
    HeapFree(GetProcessHeap(),0,object);
    if(ok) { for(int i=0;i<32;i++) sprintf(hex+2*i,"%02x",digest[i]); ok=!strcmp(hex,CSC_GAMECORE_SHA256); }
done:
    if(alg) BCryptCloseAlgorithmProvider(alg,0); CloseHandle(file); return ok;
}

static int load_original(void) {
    if(original) return 1;
    wchar_t path[32768]; DWORD n=GetModuleFileNameW(NULL,path,32768);
    if(!n || n>=32768) return 0;
    /* Executable is in Base/Binaries/Win64Steam (or Win64EOS). Derive the game
     * root from that actual path; neither cwd nor a configured external path. */
    for(int i=0;i<4;i++) { wchar_t *slash=wcsrchr(path,L'\\'); if(!slash) return 0; *slash=0; }
    if(wcslen(path)+80>=32768) return 0;
    wcscat(path,L"\\DLC\\Expansion2\\Binaries\\Win64\\GameCore_XP2_FinalRelease.dll");
    if(!verify_file(path)) return 0;
    original=LoadLibraryExW(path,NULL,LOAD_WITH_ALTERED_SEARCH_PATH);
    if(!original) return 0;
    original_base=(uintptr_t)original;
    original_create=(void *)GetProcAddress(original,"DllCreateGameContext");
    original_destroy=(void *)GetProcAddress(original,"DllDestroyGameContext");
    return original_create && original_destroy;
}
static int install_hooks(void) {
    if(hooks_ready) return 1;
    unsigned char *base=(unsigned char *)original;
    IMAGE_DOS_HEADER *dos=(void *)base; IMAGE_NT_HEADERS64 *pe=(void *)(base+dos->e_lfanew);
    if(pe->FileHeader.TimeDateStamp!=CSC_GAMECORE_TIMESTAMP || pe->OptionalHeader.SizeOfImage!=CSC_GAMECORE_IMAGE_SIZE ||
        memcmp(base+0x5bdac0,fingerprint_register,32) || memcmp(base+0x52a440,fingerprint_net,32)) return 0;
    HMODULE hks=GetModuleHandleW(L"HavokScript_FinalRelease.dll"); if(!hks) return 0;
    push_closure=(void *)GetProcAddress(hks,"?hks_pushnamedcclosure@@YAXPEAUlua_State@@P6AH0@ZHPEBDH@Z");
    set_field=(void *)GetProcAddress(hks,"?hksi_lua_setfield@@YAXPEAUlua_State@@HPEBD@Z");
    check_integer=(void *)GetProcAddress(hks,"?luaL_checkinteger@@YAHPEAUlua_State@@H@Z");
    push_integer=(void *)GetProcAddress(hks,"?hksi_lua_pushinteger@@YAXPEAUlua_State@@H@Z");
    push_string=(void *)GetProcAddress(hks,"?hksi_lua_pushfstring@@YAPEBDPEAUlua_State@@PEBDZZ");
    if(!push_closure || !set_field || !check_integer || !push_integer || !push_string) return 0;
    /* Keep our callbacks and the original module resident until process exit.
     * GameCore contexts may be destroyed/recreated while the DLL remains pinned. */
    HMODULE pinned;
    if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,(LPCWSTR)&install_hooks,&pinned)) return 0;
#ifndef CSC_CE_INTEGRATION
    if(MH_Initialize()!=MH_OK) return 0;
    if(MH_CreateHook(base+0x5bdac0,(void *)&hook_register,(void **)&original_register)!=MH_OK) return 0;
#endif
    if(MH_CreateHook(base+0x52a440,(void *)&bridge_net_entry,(void **)&original_net)!=MH_OK) return 0;
    /* No ordinary city analysis exists before the original context is created. */
#ifndef CSC_CE_INTEGRATION
    if(MH_QueueEnableHook(base+0x5bdac0)!=MH_OK) return 0;
#endif
    if(MH_QueueEnableHook(base+0x52a440)!=MH_OK || MH_ApplyQueued()!=MH_OK) return 0;
    hooks_ready=1; return 1;
}
static void reset_policy(void) {
    AcquireSRWLockExclusive(&lock); enabled=0; staging_valid=0; generation++;
    memset(&policy,0,sizeof policy); changed=matched=sample_count=faults=0;
    ReleaseSRWLockExclusive(&lock);
}
#ifdef CSC_CE_INTEGRATION
/* Compiled into CE, these are ordinary C linkage points, not a second DLL or a
 * runtime addon loader. CE owns initialization, Lua registration and context
 * retirement. This branch is a proposed CE feature, absent from released1.3. */
int CE_AIDistrictScoresInitialize(HMODULE core) {
    wchar_t path[32768];
    if(!core || !GetModuleFileNameW(core,path,32768) || !verify_file(path)) return 0;
    original=core; original_base=(uintptr_t)core;
    return install_hooks();
}
void CE_AIDistrictScoresRegisterLua(void *L) {
    if(push_closure && set_field && push_integer && check_integer && push_string) register_bindings(L);
}
void CE_AIDistrictScoresReset(void) { reset_policy(); }
#else
__declspec(dllexport) void *DllCreateGameContext(void) {
    if(!load_original()) return NULL;
    reset_policy();
    /* A fingerprint/API/hook failure leaves the prototype's policy disabled.
     * The Lua package will require ready=1 before publishing. */
    install_hooks();
    return original_create();
}
__declspec(dllexport) void DllDestroyGameContext(void *context) {
    AcquireSRWLockExclusive(&lock); enabled=0; staging_valid=0; generation++;
    ReleaseSRWLockExclusive(&lock);
    if(original_destroy) original_destroy(context);
}
/* Isolated arithmetic checks, callable without loading any game code. */
__declspec(dllexport) int CSCBridgeSelfTest(void) {
    int v,n=0;
    n+=adjusted(1000,256,&v)&&v==1256;
    n+=adjusted(1000,-256,&v)&&v==744;
    n+=!adjusted(0,256,&v)&&v==0;
    n+=!adjusted(INVALID_SCORE,256,&v)&&v==INVALID_SCORE;
    n+=!adjusted(INT_MAX,256,&v)&&v==INT_MAX;
    n+=adjusted(-1048500,-256,&v)&&v==-1048576;
    n+=!adjusted(-1048577,-256,&v)&&v==-1048577;
    return n;
}
BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,LPVOID reserved) {
    (void)reserved; if(reason==DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(instance);
    return TRUE;
}
#endif
