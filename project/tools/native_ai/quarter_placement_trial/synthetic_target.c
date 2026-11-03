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
  gint32 district=*(gint32*)(object+0x80),best=-2559744,d=-1,x=0,y=0;
  guint32 i,j,count;guint8 *rows,*row;gint32 *scores,*reservation,threshold;
  g_atomic_int_add(&harness.monitor_calls,1);
  /* Unique-winner stand-in only: fixtures never exercise equal-score RNG. */
  if(*(gint32*)(object+0x84)){
    count=*(guint32*)(object+0x4d8);rows=*(guint8**)(object+0x4c8);
    for(i=0;i<count;i++){
      row=rows+(gsize)i*0x78;
      if(!row[0x55] || (!row[0x5a] && !row[0x57]))continue;
      scores=*(gint32**)(row+0x20);reservation=*(gint32**)(row+0x48);
      threshold=reservation && reservation[0]!=-1?reservation[1]:-2559744;
      for(j=0;j<(guint32)*(gint32*)(object+0x88);j++){
        if(scores[j]>threshold && scores[j]>best){best=scores[j];d=j;x=*(gint32*)(row+8);y=*(gint32*)(row+12);}
      }
    }
    if(d>=0){coordinates[0]=x;coordinates[1]=y;}return d;
  }
  if(district>=0){coordinates[0]=10;coordinates[1]=10;}
  return district;
}
gint32 *pv_probe(guint8 *object,gint32 *out,gint32 district,guint8 *plot) {
  guint32 i,count;guint8 *rows,*row;gint32 score,best=0;
  if(object && district>=0)g_atomic_int_add(&harness.monitor_calls,1);
  if(*(gint32*)(object+0x84)){
    *out=0;if(district<0 || district>=*(gint32*)(object+0x88))return out;
    count=*(guint32*)(object+0x4d8);rows=*(guint8**)(object+0x4c8);
    for(i=0;i<count;i++){
      row=rows+(gsize)i*0x78;
      if(plot && (*(gint32*)(row+8)!=(gint32)*(gint16*)(plot+0x28) || *(gint32*)(row+12)!=(gint32)*(gint16*)(plot+0x2a)))continue;
      score=(*(gint32**)(row+0x20))[district];
      if(plot){*out=score;return out;}
      if(score>best)best=score;
    }
    *out=best;return out;
  }
  *out=plot?768:1024;return out;
}

/* Compose the owned ABI caller with an ordinary score-vector store. This is
 * a native fixture model, not an execution of GameCore's preference/aggregation. */
gint32 *score_and_store(gpointer target,gint32 *out,guint32 district,gint32 *discount,
                       gpointer plot,gpointer city,guint8 *row) {
  Caller call=(Caller)target;gint32 *returned=call(out,district,discount,3,50,plot,city,row);
  if(returned==out)(*(gint32**)(row+0x20))[district]=*returned;
  return returned;
}
