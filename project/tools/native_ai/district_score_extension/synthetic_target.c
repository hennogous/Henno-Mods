#include <glib.h>
typedef gint32*(*Caller)(gint32*,guint32,gint32*,gint32,gint32,void*,void*,void*);
typedef struct { gint32 original_calls,arg_errors,monitor_calls; } Harness;
extern Harness harness;
extern gpointer create_thread(gpointer,gsize,gpointer,gpointer,guint32,gpointer);
extern guint32 wait_one(gpointer,guint32);
extern gint32 close_handle(gpointer);
gint32 *score(gint32 *out,guint32 district,gint32 *discount,gint32 ready,gint32 horizon,guint8 *plot,void *city) {
  g_atomic_int_add(&harness.original_calls,1);
  if(!discount || *discount!=512 || (ready!=3 && ready!=4) || horizon!=50 || !city || !plot)
    g_atomic_int_add(&harness.arg_errors,1);
  if(ready==3 && *(gint32*)(plot+8)) {gint32 inner;score(&inner,district,discount,4,horizon,plot,city);}
  *out=*(gint32*)plot;
  if(*(gint32*)(plot+4)) return out+1;
  return out;
}
guint32 run_calls(gpointer target,guint32 count,gpointer row,gpointer city,gpointer plot,guint32 district) {
  guint32 i;gint32 out[2],discount=512;Caller call=(Caller)target;
  for(i=0;i<count;i++)call(out,district,&discount,3,50,plot,city,row);
  return harness.original_calls;
}
typedef struct {gpointer target,row,city,plot;guint32 count,district;} ThreadArgs;
guint32 thread_worker(gpointer raw) {
  ThreadArgs *a=raw;run_calls(a->target,a->count,a->row,a->city,a->plot,a->district);return 0;
}
gint32 parallel_calls(gpointer target,guint32 count,gpointer row,gpointer city,gpointer plot,guint32 district) {
  ThreadArgs args[4];gpointer threads[4];guint32 i;
  for(i=0;i<4;i++){
    args[i].target=target;args[i].row=row;args[i].city=city;args[i].plot=plot;args[i].district=district;args[i].count=count;
    threads[i]=create_thread(0,0,thread_worker,&args[i],0,0);
    if(!threads[i])break;
  }
  {guint32 made=i;for(i=0;i<made;i++){wait_one(threads[i],0xffffffff);close_handle(threads[i]);}return made==4?0:-1;}
}

/* Owned stand-ins for the three observed ABI boundaries; no game functions. */
void cache_probe(guint8 *object) {
  if(object)g_atomic_int_add(&harness.monitor_calls,1);
}
gint32 best_probe(guint8 *object,gint32 *coordinates) {
  gint32 district=*(gint32*)(object+0x80);
  g_atomic_int_add(&harness.monitor_calls,1);
  if(district>=0){coordinates[0]=10;coordinates[1]=10;}
  return district;
}
gint32 *pv_probe(guint8 *object,gint32 *out,gint32 district,guint8 *plot) {
  if(object && district>=0)g_atomic_int_add(&harness.monitor_calls,1);
  *out=plot?768:1024;return out;
}
