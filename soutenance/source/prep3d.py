# Convert the 15 OBJ products to light GLB files (decimated, JPEG textures)
import os, re, shutil, subprocess, glob, json
from PIL import Image
S='/tmp/claude-0/-home-user-HANDY/36455e3e-c271-5390-ad89-57cd94b34b42/scratchpad'
SRC=S+'/dl/x/P3D'; W=S+'/build/p3d'; T=S+'/tools/node_modules/.bin'
MAP={'Marinade-Poulet':'marinade_poulet','Marinade-Poisson':'marinade_poisson','Marinade-Mixte':'marinade_mixte',
 'Epice-Speciale-Poulet':'epice_poulet','Epice-Speciale-Poisson':'epice_poisson','Paprika':'paprika','Piment-en-Poudre':'piment',
 'Graines-Akpi':'akpi','Poudre-de-Djoumble':'djoumble','Poudre-de-Crevette':'crevette','Poudre-de-Poisson':'poudre_poisson',
 'Puree-d-Ail':'ail','Bouillon-de-Poulet':'bouillon','Pate-d-Arachide':'arachide','Huile-Rouge':'huile'}
os.makedirs(W,exist_ok=True)
for d in sorted(os.listdir(SRC)):
    key=next(v for k,v in MAP.items() if k in d)
    out=f'{W}/{key}'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
    mtl=open(glob.glob(f'{SRC}/{d}/*.mtl')[0]).read()
    for tex in set(re.findall(r'map_Kd (\S+)',mtl)):
        im=Image.open(f'{SRC}/{d}/{tex}')
        lim=1400 if ('arriere' not in tex) else 800
        im.thumbnail((lim,lim),Image.LANCZOS)
        if im.mode=='RGBA':
            nt=os.path.splitext(tex)[0]+'.png'; im.save(f'{out}/{nt}',optimize=True)
        else:
            nt=os.path.splitext(tex)[0]+'.jpg'; im.convert('RGB').save(f'{out}/{nt}',quality=87)
        mtl=mtl.replace(tex,nt)
    open(f'{out}/m.mtl','w').write(mtl)
    obj=open(glob.glob(f'{SRC}/{d}/*.obj')[0]).read()
    obj=re.sub(r'^mtllib .*$','mtllib m.mtl',obj,flags=re.M)
    open(f'{out}/m.obj','w').write(obj)
    subprocess.run([f'{T}/obj2gltf','-i',f'{out}/m.obj','-o',f'{out}/full.glb'],check=True,capture_output=True)
    r=subprocess.run([f'{T}/gltfpack','-i',f'{out}/full.glb','-o',f'{W}/{key}.glb','-si','0.2','-noq','-kn','-km'],capture_output=True,text=True)
    print(key, r.returncode, r.stderr.strip()[-200:], os.path.getsize(f'{W}/{key}.glb')//1024,'KB')
