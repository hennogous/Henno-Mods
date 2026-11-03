#include <glib.h>
#include <gum/guminterceptor.h>
#include <string.h>

/* Experimental, signed-Q8 adapter. No Lua, JS callback, file or game API calls.
 * Writable storage is supplied by the host; CModule globals are read-only. */
#define INVALID_SCORE (-2559744)
#define RECORD_LIMIT 128
enum { OK=0, DISABLED=1, HUMAN=2, SCOPE=3, STALE=4, NOT_ADMITTED=5,
       POINTER_MISMATCH=6, ZERO_SCORE=7, INVALID=8, OVERFLOW=9, COLLISION=10,
       ZERO_DELTA=11, CAPACITY=12 };
typedef struct {
  gint32 session,epoch,version,player,city,district,plot,delta,human,current_human,width,height,max_changes,district_count;
  gpointer caller;
} Policy;
typedef struct { gint32 player,city,district,plot,x,y,base,result,reason,eligible,kind; } Record;
typedef struct {
  GMutex mutex;
  Policy policy;
  gint32 mode,active,count;
  guint32 calls,admitted,changed,errors,skipped,fatal;
  Record records[RECORD_LIMIT];
} State;
extern State state;
extern gsize query_memory(gconstpointer,gpointer,gsize);
typedef struct {gpointer base,allocation;guint32 allocation_protect,padding;gsize bytes;guint32 committed,protect,type,tail;} Region;
gboolean valid_span(gconstpointer ptr,gsize bytes,gboolean writable) {
  Region r;guintptr start=(guintptr)ptr,end=start+bytes,region_end;
  if(!ptr || !bytes || end<start || query_memory(ptr,&r,sizeof(r))!=sizeof(r) ||
     r.committed!=0x1000 || (r.protect&0x100))return FALSE;
  region_end=(guintptr)r.base+r.bytes;
  if((guintptr)r.base>start || region_end<end || region_end<(guintptr)r.base)return FALSE;
  if(writable)return (r.protect&0xff)==4 || (r.protect&0xff)==8 || (r.protect&0xff)==0x40 || (r.protect&0xff)==0x80;
  return (r.protect&0xff)==2 || (r.protect&0xff)==4 || (r.protect&0xff)==8 ||
         (r.protect&0xff)==0x20 || (r.protect&0xff)==0x40 || (r.protect&0xff)==0x80;
}
typedef struct { gint32 accepted; gint32 district,player,city,plot,x,y,mode,delta; gint32 *out; } Invocation;
typedef struct { gint32 accepted,kind,district,plot; guint8 *object; gint32 *out; } MonitorInvocation;
typedef char InvocationFits[(sizeof(Invocation)<=1024 && sizeof(MonitorInvocation)<=1024)?1:-1];

static void fault(void) { state.errors++;state.fatal=1;state.mode=0; }

/* Called under the state lock; record saturation stops this finite experiment. */
static void record_value(gint32 kind,gint32 district,gint32 plot,gint32 x,gint32 y,
                         gint32 base,gint32 result,gint32 reason,gint32 eligible) {
  Record *r;
  if(state.count>=RECORD_LIMIT){state.mode=0;state.skipped++;return;}
  r=&state.records[state.count++];r->player=state.policy.player;r->city=state.policy.city;
  r->district=district;r->plot=plot;r->x=x;r->y=y;r->base=base;r->result=result;
  r->reason=reason;r->eligible=eligible;r->kind=kind;
}

guint32 state_size(void) { return sizeof(State); }
void initialize(void) { memset(&state,0,sizeof(State));g_mutex_init(&state.mutex); }

/* Policy replacement is refused while enabled or while an original call is live. */
gint32 configure(const gint32 *v, gpointer caller) {
  gint32 result=0;
  g_mutex_lock(&state.mutex);
  if(state.mode || state.active) result=-1;
  else if(!valid_span(v,14*sizeof(gint32),FALSE)) result=-2;
  else if(state.fatal || v[0]<=0 || v[1]<=0 || v[2]<=0 || v[3]<0 || v[4]<0 || v[5]<0 ||
          v[10]<=0 || v[10]>256 || v[11]<=0 || v[11]>256 || v[12]<1 || v[12]>128 ||
          v[13]<1 || v[13]>4096 || v[5]>=v[13] ||
          (gint64)v[7]>4096 || (gint64)v[7]<-4096 || v[6]<-1 || v[6]>=v[10]*v[11] || !caller) result=-2;
  else { memcpy(&state.policy,v,14*sizeof(gint32)); state.policy.caller=caller; }
  g_mutex_unlock(&state.mutex); return result;
}
gint32 set_mode(gint32 mode) {
  gint32 result;
  g_mutex_lock(&state.mutex);
  if(mode<0 || mode>2 || (mode && (state.active || state.fatal)) || (mode==2 && state.policy.plot<0)) result=-1;
  else { state.mode=mode; result=state.active; }
  g_mutex_unlock(&state.mutex); return result;
}

/* Standalone pure kernel: independent fixtures use this documented word packet.
 * base,delta,enabled,originalHuman,currentHuman,nativeAdmitted,pointerEqual,
 * session,observedSession,epoch,observedEpoch,version,observedVersion,scopeEqual. */
gint32 evaluate(const gint32 *v, gint32 *out) {
  gint64 sum; *out=v[0];
  if(!v[2]) return DISABLED;
  if(v[3] || v[4]) return HUMAN;
  if(!v[13]) return SCOPE;
  if(v[7]!=v[8] || v[9]!=v[10] || v[11]!=v[12]) return STALE;
  if(!v[5]) return NOT_ADMITTED;
  if(!v[6]) return POINTER_MISMATCH;
  if(v[0]==INVALID_SCORE) return INVALID;
  if(v[0]==0) return ZERO_SCORE;
  if(v[1]==0) return ZERO_DELTA;
  if((gint64)v[1]>4096 || (gint64)v[1]<-4096)return 13;
  sum=(gint64)v[0]+(gint64)v[1];
  if(sum>2147483647LL || sum<(-2147483647LL-1)) return OVERFLOW;
  if(sum==INVALID_SCORE) return COLLISION;
  *out=(gint32)sum; return OK;
}

void on_enter(GumInvocationContext *ic) {
  Invocation *v=GUM_IC_GET_INVOCATION_DATA(ic,Invocation);
  guint8 *city,*plot,*row; gint32 x,y,owner,id,district,index,eligible;
  if(!v) return;
  v->accepted=0;
  g_mutex_lock(&state.mutex); state.calls++;
  if(!state.mode || state.policy.human || state.policy.current_human ||
     gum_invocation_context_get_return_address(ic)!=state.policy.caller) goto done;
  district=(gint32)(gintptr)gum_invocation_context_get_nth_argument(ic,1);
  if(district!=state.policy.district) goto done;
  city=gum_invocation_context_get_nth_argument(ic,6);
  plot=gum_invocation_context_get_nth_argument(ic,5);
  if(!city || !plot) goto done;
  if(!valid_span(city,0xdc,FALSE) || !valid_span(plot,0x2c,FALSE)){state.errors++;state.fatal=1;state.mode=0;goto done;}
  owner=*(gint32*)(city+0xd8); id=*(gint32*)(city+0xa8);
  if(owner!=state.policy.player || id!=state.policy.city) goto done;
  x=*(gint16*)(plot+0x28); y=*(gint16*)(plot+0x2a);
  if(x<0 || x>=state.policy.width || y<0 || y>=state.policy.height) goto done;
  index=y*state.policy.width+x;
  if(state.policy.plot>=0 && index!=state.policy.plot) goto done;
  /* Static caller contract: R12 is the current0x78-byte plot row at3e30b9. */
  row=(guint8*)ic->cpu_context->r12;
  if(!valid_span(row,0x78,FALSE) || *(gint32*)(row+8)!=x || *(gint32*)(row+12)!=y ||
     *(gint16*)(row+0x70)!=owner || *(gint32*)(row+0x74)!=id) { state.errors++;state.fatal=1;state.mode=0; goto done; }
  eligible=row[0x55] && (row[0x5a] || row[0x57]);
  if(!eligible) goto done;
  v->out=gum_invocation_context_get_nth_argument(ic,0);
  if(!valid_span(v->out,4,TRUE)) {state.errors++;state.fatal=1;state.mode=0; goto done;}
  v->accepted=1; v->player=owner; v->city=id; v->district=district; v->plot=index;
  v->x=x; v->y=y; v->mode=state.mode; v->delta=state.policy.delta;
  state.active++; state.admitted++;
done: g_mutex_unlock(&state.mutex);
}
void on_leave(GumInvocationContext *ic) {
  Invocation *v=GUM_IC_GET_INVOCATION_DATA(ic,Invocation);
  gint32 base,result,reason,packet[14],write_result; Record *r;
  if(!v || !v->accepted) return;
  /* An invocation owns its gate, so recursion and repeated leave cannot share it. */
  v->accepted=0;
  g_mutex_lock(&state.mutex); state.active--;
  if(gum_invocation_context_get_return_value(ic)!=v->out || !valid_span(v->out,4,TRUE)) {state.errors++;state.fatal=1;state.mode=0; goto done;}
  base=*v->out; result=base;
  packet[0]=base;packet[1]=v->delta;packet[2]=1;packet[3]=0;packet[4]=0;packet[5]=1;packet[6]=1;
  packet[7]=packet[8]=state.policy.session;packet[9]=packet[10]=state.policy.epoch;
  packet[11]=packet[12]=state.policy.version;packet[13]=1;
  reason=evaluate(packet,&result);
  if(state.count>=RECORD_LIMIT) {state.mode=0;state.skipped++;goto done;}
  r=&state.records[state.count++];r->player=v->player;r->city=v->city;r->district=v->district;
  write_result=state.mode==2 && v->mode==2 && reason==OK && state.changed<state.policy.max_changes;
  r->plot=v->plot;r->x=v->x;r->y=v->y;r->base=base;r->result=(write_result?result:base);
  r->reason=state.mode?reason:DISABLED;r->eligible=1;r->kind=0;
  if(write_result) {*v->out=result;state.changed++;if(state.changed>=state.policy.max_changes)state.mode=1;}
done:g_mutex_unlock(&state.mutex);
}

/* Monitor only the declared city's native cache/choice/PV boundaries. All
 * gameplay memory reads are guarded by VirtualQuery immediately before use.
 * These checks do not pin engine object lifetimes or create a generation API. */
static gboolean city_matches(guint8 *object) {
  guint8 *city;
  if(!valid_span(object,0x4dc,FALSE)){fault();return FALSE;}
  city=*(guint8**)(object+0x90);
  if(!valid_span(city,0xdc,FALSE)){fault();return FALSE;}
  return *(gint32*)(city+0xd8)==state.policy.player && *(gint32*)(city+0xa8)==state.policy.city;
}

static gboolean coordinates(gint32 x,gint32 y,gint32 *index) {
  if(x<0 || x>=state.policy.width || y<0 || y>=state.policy.height)return FALSE;
  *index=y*state.policy.width+x;return TRUE;
}

/* The bounded row array is owned by the original CityBuild object. */
static gboolean cache_rows(guint8 *object,guint8 **rows,guint32 *count) {
  if(!valid_span(object,0x4dc,FALSE)){fault();return FALSE;}
  *count=*(guint32*)(object+0x4d8);*rows=*(guint8**)(object+0x4c8);
  if(*count>37){fault();return FALSE;}
  if(*count && !valid_span(*rows,(gsize)*count*0x78,FALSE)){fault();return FALSE;}
  return TRUE;
}

static gboolean row_score(guint8 *row,gint32 district,gint32 *score,gint32 *eligible) {
  gint32 *scores;
  if(district<0 || district>=state.policy.district_count || !valid_span(row,0x78,FALSE)){fault();return FALSE;}
  *eligible=row[0x55] && (row[0x5a] || row[0x57]);
  if(!*eligible)return FALSE;
  scores=*(gint32**)(row+0x20);
  if(!valid_span(scores,(gsize)state.policy.district_count*4,FALSE)){fault();return FALSE;}
  *score=scores[district];return TRUE;
}

static void monitor_enter(GumInvocationContext *ic,gint32 kind) {
  MonitorInvocation *v=GUM_IC_GET_INVOCATION_DATA(ic,MonitorInvocation);
  guint8 *object,*plot_object;gint32 district,plot,x,y;
  if(!v)return;
  v->accepted=0;
  g_mutex_lock(&state.mutex);state.calls++;
  if(!state.mode || state.policy.human || state.policy.current_human)goto done;
  object=gum_invocation_context_get_nth_argument(ic,0);
  if(!city_matches(object))goto done;
  v->out=NULL;v->district=state.policy.district;v->plot=state.policy.plot;
  if(kind==2){
    v->out=gum_invocation_context_get_nth_argument(ic,1);
    if(!valid_span(v->out,8,TRUE)){fault();goto done;}
  }else if(kind==3){
    district=(gint32)(gintptr)gum_invocation_context_get_nth_argument(ic,2);
    if(district!=state.policy.district)goto done;
    plot_object=gum_invocation_context_get_nth_argument(ic,3);
    plot=-1;
    if(plot_object){
      if(!valid_span(plot_object,0x2c,FALSE)){fault();goto done;}
      x=*(gint16*)(plot_object+0x28);y=*(gint16*)(plot_object+0x2a);
      if(!coordinates(x,y,&plot)){fault();goto done;}
      if(plot!=state.policy.plot)goto done;
    }
    v->out=gum_invocation_context_get_nth_argument(ic,1);
    if(!valid_span(v->out,4,TRUE)){fault();goto done;}
    v->district=district;v->plot=plot;
  }
  v->accepted=1;v->kind=kind;v->object=object;state.active++;state.admitted++;
done:g_mutex_unlock(&state.mutex);
}

static void monitor_leave(GumInvocationContext *ic) {
  MonitorInvocation *v=GUM_IC_GET_INVOCATION_DATA(ic,MonitorInvocation);
  guint8 *rows,*row;guint32 count,i;gint32 district,x,y,index,score,eligible;
  if(!v || !v->accepted)return;
  v->accepted=0;
  g_mutex_lock(&state.mutex);state.active--;
  if(!state.mode || state.fatal || !city_matches(v->object))goto done;
  if(v->kind==3){
    if(gum_invocation_context_get_return_value(ic)!=v->out || !valid_span(v->out,4,FALSE)){fault();goto done;}
    score=*v->out;x=v->plot<0?-1:v->plot%state.policy.width;y=v->plot<0?-1:v->plot/state.policy.width;
    record_value(3,v->district,v->plot,x,y,score,score,v->plot<0?NOT_ADMITTED:OK,score!=INVALID_SCORE && score!=0);goto done;
  }
  if(v->kind==2){
    district=(gint32)(gintptr)gum_invocation_context_get_return_value(ic);
    if(district==-1){record_value(2,-1,-1,-1,-1,0,0,NOT_ADMITTED,0);goto done;}
    if(district<0 || district>=state.policy.district_count || !valid_span(v->out,8,FALSE)){fault();goto done;}
    x=v->out[0];y=v->out[1];
    if(!coordinates(x,y,&index)){fault();goto done;}
  }else{district=state.policy.district;x=state.policy.plot%state.policy.width;y=state.policy.plot/state.policy.width;index=state.policy.plot;}
  if(!cache_rows(v->object,&rows,&count))goto done;
  for(i=0;i<count;i++){
    row=rows+(gsize)i*0x78;
    if(!valid_span(row,0x78,FALSE)){fault();goto done;}
    if(*(gint32*)(row+8)!=x || *(gint32*)(row+12)!=y)continue;
    if(!row_score(row,district,&score,&eligible))goto done;
    record_value(v->kind,district,index,x,y,score,score,OK,eligible);goto done;
  }
done:g_mutex_unlock(&state.mutex);
}

void cache_enter(GumInvocationContext *ic){monitor_enter(ic,1);}
void cache_leave(GumInvocationContext *ic){monitor_leave(ic);}
void best_enter(GumInvocationContext *ic){monitor_enter(ic,2);}
void best_leave(GumInvocationContext *ic){monitor_leave(ic);}
void pv_enter(GumInvocationContext *ic){monitor_enter(ic,3);}
void pv_leave(GumInvocationContext *ic){monitor_leave(ic);}
/* Copy a consistent snapshot; JavaScript reads only this caller-owned copy. */
guint32 snapshot(gint32 *out,guint32 capacity) {
  guint32 n;
  g_mutex_lock(&state.mutex);
  n=10+state.count*11;
  if(capacity>=n) {
    out[0]=state.mode;out[1]=state.active;out[2]=state.count;out[3]=state.calls;
    out[4]=state.admitted;out[5]=state.changed;out[6]=state.errors;out[7]=state.skipped;
    out[8]=sizeof(Invocation);out[9]=state.fatal;
    memcpy(out+10,state.records,state.count*sizeof(Record));
  }
  g_mutex_unlock(&state.mutex);return n;
}
