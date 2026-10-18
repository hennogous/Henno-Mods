from bakery_props_atlas import *
def native(p):
 out=[]
 for c in p.read_text().split('mesh:"')[1:]:
  name,b=c.split('"',1);vb,tb=b.split('vertices\n',1)[1].split('triangles\n',1);v=np.array([[float(x) for x in l.split()] for l in vb.strip().splitlines()]);t=np.array([[int(x) for x in l.split()[:3]] for l in tb.split('\nend')[0].strip().splitlines()]);out.append((name,v,t))
 return out
a=native(OUT/'before/CSC_BAKERS_Oven_v2.cn6');b=native(OUT/'CSC_BAKERS_Oven_v2-roundtrip.cn6');rows=[]
for (name,v,t),(name2,w,tt) in zip(a,b):
 assert name==name2 and v.shape==w.shape and np.array_equal(t,tt)
 x=v[t];y=w[tt];keep=list(range(16))+list(range(18,v.shape[1]));err=float(np.max(abs(x[:,:,keep]-y[:,:,keep])));assert err<1e-5,err
 changed=np.any(abs(x[:,:,16:18]-y[:,:,16:18])>1e-6,axis=(1,2));opening=np.any(x[:,:,16]>.1,axis=1);assert np.array_equal(changed,opening)
 expected=np.stack(((192+56*(x[:,:,12]*1024-388)/120)/256,(184+48*(x[:,:,13]*1024-900)/120)/256),axis=2)
 assert np.max(abs(y[opening,:,16:18]-expected[opening]))<1e-6
 assert np.array_equal(x[~opening,:,16:18],y[~opening,:,16:18])
 rows.append(dict(mesh=name,vertices=len(v),triangles=len(t),changed_UV3_triangles=int(changed.sum()),all_other_native_attributes_max_error=err,nonopening_UV3_exact=True,opening_affine_map_verified=True))
(OUT/'native-UV3-preservation.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
