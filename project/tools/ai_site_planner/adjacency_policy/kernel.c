#include <glib.h>
#include <gum/guminterceptor.h>
#include <string.h>
/* Multi-city research policy. Native-only callbacks; no calls into the game,
 * Lua or JavaScript. Publishes only while disabled and drained. */
#define LIMIT 4096
#define ENTRIES 128
#define INVALID (-2559744)
typedef struct {gint32 player,city,district,plot,delta;} Entry;
typedef struct {gint32 player,city,district,plot,x,y,base,result,reason,eligible,kind;} Record;
typedef struct {
 GMutex mutex;gint32 mode,active,count,version,n,width,height,district_count,fatal;
 guint32 calls,admitted,changed,errors;gpointer caller;
 gint32 allowed[64];Entry entries[ENTRIES];Record records[LIMIT];
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

static void fault(void){state.errors++;state.fatal=1;state.mode=0;}
guint32 state_size(void){return sizeof(State);}
void initialize(void){memset(&state,0,sizeof(State));g_mutex_init(&state.mutex);}
/* header: width,height,districtCount,monotonicVersion,entryCount,64 AI flags.
 * One entry per city; a replacement never increments restored cache memory. */
gint32 publish(const gint32 *h,const Entry *entries,gpointer caller){
 gint32 i,j,result=-1;g_mutex_lock(&state.mutex);
 if(state.mode||state.active||state.fatal)goto done;
 if(!valid_span(h,69*4,FALSE)||!caller)goto done;
 if(h[0]<1||h[0]>256||h[1]<1||h[1]>256||h[2]<1||h[2]>4096||h[3]<=state.version||h[4]<0||h[4]>ENTRIES)goto done;
 for(i=0;i<64;i++)if(h[5+i]!=0&&h[5+i]!=1)goto done;
 if(h[4]&&!valid_span(entries,h[4]*sizeof(Entry),FALSE))goto done;
 for(i=0;i<h[4];i++){
  Entry e=entries[i];
  if(e.player<0||e.player>63||!h[5+e.player]||e.city<0||e.district<1||e.district>=h[2]||e.plot<0||e.plot>=h[0]*h[1]||e.delta!=1048576)goto done;
  for(j=0;j<i;j++)if(entries[j].player==e.player&&entries[j].city==e.city)goto done;
 }
 state.width=h[0];state.height=h[1];state.district_count=h[2];state.version=h[3];state.n=h[4];state.caller=caller;
 memcpy(state.allowed,h+5,64*4);if(state.n)memcpy(state.entries,entries,state.n*sizeof(Entry));
 state.count=0;state.calls=state.admitted=state.changed=state.errors=0;result=0;
 done:g_mutex_unlock(&state.mutex);return result;
}
gint32 set_mode(gint32 mode){gint32 r=-1;g_mutex_lock(&state.mutex);
 if(mode==0){state.mode=0;r=state.active;}
 else if(mode==2&&!state.active&&!state.fatal&&state.version>0){state.mode=2;r=0;}
 g_mutex_unlock(&state.mutex);return r;
}
static Entry *find_city(gint32 player,gint32 city){gint32 i;
 if(player<0||player>63||!state.allowed[player])return NULL;
 for(i=0;i<state.n;i++)if(state.entries[i].player==player&&state.entries[i].city==city)return &state.entries[i];return NULL;
}
static Entry *object_entry(guint8 *object){guint8 *city;
 if(!valid_span(object,0x4dc,FALSE)){fault();return NULL;}
 city=*(guint8**)(object+0x90);if(!valid_span(city,0xdc,FALSE)){fault();return NULL;}
 return find_city(*(gint32*)(city+0xd8),*(gint32*)(city+0xa8));
}
static void record(Entry e,gint32 kind,gint32 district,gint32 plot,gint32 base,gint32 result,gint32 reason,gint32 eligible){Record *r;
 if(state.count>=LIMIT){fault();return;}r=&state.records[state.count++];
 r->player=e.player;r->city=e.city;r->district=district;r->plot=plot;
 r->x=plot<0?-1:plot%state.width;r->y=plot<0?-1:plot/state.width;
 r->base=base;r->result=result;r->reason=reason;r->eligible=eligible;r->kind=kind;
}
typedef struct {gint32 accepted,version,kind;Entry entry;gint32 *out;guint8 *object;} Invocation;
typedef char Fits[(sizeof(Invocation)<=1024)?1:-1];
void on_enter(GumInvocationContext *ic){Invocation *v=GUM_IC_GET_INVOCATION_DATA(ic,Invocation);guint8 *city,*plot,*row;Entry *e;gint32 d,x,y,i;
 if(!v)return;v->accepted=0;g_mutex_lock(&state.mutex);state.calls++;
 if(state.mode!=2||gum_invocation_context_get_return_address(ic)!=state.caller)goto done;
 d=(gint32)(gintptr)gum_invocation_context_get_nth_argument(ic,1);
 for(i=0;i<state.n;i++)if(state.entries[i].district==d)break;if(i==state.n)goto done;
 city=gum_invocation_context_get_nth_argument(ic,6);plot=gum_invocation_context_get_nth_argument(ic,5);
 if(!valid_span(city,0xdc,FALSE)||!valid_span(plot,0x2c,FALSE)){fault();goto done;}
 e=find_city(*(gint32*)(city+0xd8),*(gint32*)(city+0xa8));if(!e||e->district!=d)goto done;
 x=*(gint16*)(plot+0x28);y=*(gint16*)(plot+0x2a);
 if(x<0||x>=state.width||y<0||y>=state.height||y*state.width+x!=e->plot)goto done;
 row=(guint8*)ic->cpu_context->r12;
 if(!valid_span(row,0x78,FALSE)||*(gint32*)(row+8)!=x||*(gint32*)(row+12)!=y||*(gint16*)(row+0x70)!=e->player||*(gint32*)(row+0x74)!=e->city){fault();goto done;}
 if(!row[0x55]||(!row[0x5a]&&!row[0x57]))goto done;
 v->out=gum_invocation_context_get_nth_argument(ic,0);if(!valid_span(v->out,4,TRUE)){fault();goto done;}
 v->entry=*e;v->version=state.version;v->accepted=1;state.active++;state.admitted++;
 done:g_mutex_unlock(&state.mutex);
}
void on_leave(GumInvocationContext *ic){Invocation *v=GUM_IC_GET_INVOCATION_DATA(ic,Invocation);gint32 base,result,reason=0;gint64 sum;
 if(!v||!v->accepted)return;v->accepted=0;g_mutex_lock(&state.mutex);state.active--;
 if(gum_invocation_context_get_return_value(ic)!=v->out||!valid_span(v->out,4,TRUE)){fault();goto done;}
 base=*v->out;result=base;
 if(state.mode!=2||v->version!=state.version)reason=1;
 else if(base==0||base==INVALID)reason=2;
 else {sum=(gint64)base+v->entry.delta;if(sum>2147483647LL||sum<(-2147483647LL-1)||sum==INVALID)reason=3;else result=(gint32)sum;}
 if(state.count>=LIMIT||state.changed>=512){fault();goto done;}
 if(!reason){*v->out=result;state.changed++;}
 record(v->entry,0,v->entry.district,v->entry.plot,base,result,reason,1);
 done:g_mutex_unlock(&state.mutex);
}
static void monitor_enter(GumInvocationContext *ic,gint32 kind){Invocation *v=GUM_IC_GET_INVOCATION_DATA(ic,Invocation);Entry *e;guint8 *p;gint32 d,index;
 if(!v)return;v->accepted=0;g_mutex_lock(&state.mutex);state.calls++;
 if(state.mode!=2||!state.n)goto done;
 v->object=gum_invocation_context_get_nth_argument(ic,0);e=object_entry(v->object);if(!e)goto done;
 v->out=NULL;
 if(kind==2){v->out=gum_invocation_context_get_nth_argument(ic,1);if(!valid_span(v->out,8,TRUE)){fault();goto done;}}
 if(kind==3){d=(gint32)(gintptr)gum_invocation_context_get_nth_argument(ic,2);if(d!=e->district)goto done;
  p=gum_invocation_context_get_nth_argument(ic,3);if(!p)goto done;if(!valid_span(p,0x2c,FALSE)){fault();goto done;}
  index=*(gint16*)(p+0x2a)*state.width+*(gint16*)(p+0x28);if(index!=e->plot)goto done;
  v->out=gum_invocation_context_get_nth_argument(ic,1);if(!valid_span(v->out,4,TRUE)){fault();goto done;}}
 v->entry=*e;v->version=state.version;v->kind=kind;v->accepted=1;state.active++;state.admitted++;
 done:g_mutex_unlock(&state.mutex);
}
static void monitor_leave(GumInvocationContext *ic){Invocation *v=GUM_IC_GET_INVOCATION_DATA(ic,Invocation);guint8 *rows,*row;gint32 *scores,d,plot,x,y,value;guint32 n,i;
 if(!v||!v->accepted)return;v->accepted=0;g_mutex_lock(&state.mutex);state.active--;
 if(state.mode!=2||v->version!=state.version)goto done;
 d=v->entry.district;plot=v->entry.plot;
 if(v->kind==3){if(gum_invocation_context_get_return_value(ic)!=v->out||!valid_span(v->out,4,FALSE)){fault();goto done;}
  value=*v->out;record(v->entry,3,d,plot,value,value,0,1);goto done;}
 if(v->kind==2){d=(gint32)(gintptr)gum_invocation_context_get_return_value(ic);
  if(d==-1){record(v->entry,2,-1,-1,0,0,0,0);goto done;}
  if(d<0||d>=state.district_count||!valid_span(v->out,8,FALSE)){fault();goto done;}
  x=v->out[0];y=v->out[1];if(x<0||x>=state.width||y<0||y>=state.height){fault();goto done;}plot=y*state.width+x;
 }
 if(!valid_span(v->object,0x4dc,FALSE)){fault();goto done;}
 n=*(guint32*)(v->object+0x4d8);rows=*(guint8**)(v->object+0x4c8);
 if(n>37||(n&&!valid_span(rows,(gsize)n*0x78,FALSE))){fault();goto done;}
 for(i=0;i<n;i++){row=rows+i*0x78;x=*(gint32*)(row+8);y=*(gint32*)(row+12);if(y*state.width+x!=plot)continue;
  scores=*(gint32**)(row+0x20);if(!valid_span(scores,state.district_count*4,FALSE)){fault();goto done;}
  value=scores[d];record(v->entry,v->kind,d,plot,value,value,0,row[0x55]&&(row[0x5a]||row[0x57]));break;
 }
 done:g_mutex_unlock(&state.mutex);
}
void cache_enter(GumInvocationContext *ic){monitor_enter(ic,1);}void cache_leave(GumInvocationContext *ic){monitor_leave(ic);}
void best_enter(GumInvocationContext *ic){monitor_enter(ic,2);}void best_leave(GumInvocationContext *ic){monitor_leave(ic);}
void pv_enter(GumInvocationContext *ic){monitor_enter(ic,3);}void pv_leave(GumInvocationContext *ic){monitor_leave(ic);}
guint32 snapshot(gint32 *out,guint32 capacity){guint32 n;g_mutex_lock(&state.mutex);n=10+state.count*11;
 if(capacity<n)n=0;else{out[0]=state.mode;out[1]=state.active;out[2]=state.count;out[3]=state.calls;out[4]=state.admitted;out[5]=state.changed;out[6]=state.errors;out[7]=state.fatal;out[8]=state.version;out[9]=state.n;memcpy(out+10,state.records,state.count*sizeof(Record));}
 g_mutex_unlock(&state.mutex);return n;
}
