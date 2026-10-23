import sys; sys.path.insert(0,'.')
import numpy as np, cv2
from PIL import Image
from geom import *
import os
IMG=os.environ.get('IMG_DIR','./')  # dossier contenant 1.jpg (photo), 2.png (recto), 3.png (verso)
bg=np.asarray(Image.open(IMG+'1.jpg').convert('RGB')).astype(np.float32)/255
H,W=bg.shape[:2]

def load(f,gap=None):
    a=np.asarray(Image.open(IMG+f).convert('RGBA')).astype(np.float32)/255
    rgb=a[...,:3].copy()
    rgb[:,0]=rgb[:,1]; rgb[:,-1]=rgb[:,-2]; rgb[-1]=rgb[-2]; rgb[0]=rgb[1]
    if gap is not None: rgb[:,gap]=rgb[:,gap+1]
    return rgb
ext=load('2.png'); inn=load('3.png',gap=292)
ext_split=[0,284,568,860]; inn_split=[0,292,576,860]

LIGHT={'L':[(.955,.955,.945,.93),(.885,.875,.865,.855),(.905,.855,.88,.885)],
       'R':[(.90,.935,.905,.945),(.90,.90,.89,.885),(.89,.88,.87,.86)]}
LIFT=0.07; SAT=0.94
S=4  # supersampling

def prep(rgb):
    g=rgb.mean(2,keepdims=True)
    rgb=g+(rgb-g)*SAT
    rgb=LIFT+(1-LIFT)*rgb
    return np.clip(rgb,0,1)

def render(design,split,T,B,lights):
    xs=[p[0] for p in T+B]; ys=[p[1] for p in T+B]
    x0,y0=int(np.floor(min(xs)))-3,int(np.floor(min(ys)))-3
    x1,y1=int(np.ceil(max(xs)))+3,int(np.ceil(max(ys)))+3
    cw,ch=(x1-x0)*S,(y1-y0)*S
    acc=np.zeros((ch,cw,3),np.float32); al=np.zeros((ch,cw),np.float32)
    hgt=design.shape[0]
    for i in range(3):
        sx0,sx1=split[i],split[i+1]
        pan=prep(design[:,sx0:sx1])
        h,w=pan.shape[:2]
        tl,tr,bl,br=lights[i]
        u=np.linspace(0,1,w)[None,:,None]; v=np.linspace(0,1,h)[:,None,None]
        Lf=(tl*(1-u)*(1-v)+tr*u*(1-v)+bl*(1-u)*v+br*u*v)
        pan=(pan*Lf).astype(np.float32)
        src=np.float32([[0,0],[w,0],[w,h],[0,h]])
        dst=np.float32([T[i],T[i+1],B[i+1],B[i]]); dst=((dst-[x0,y0])*S).astype(np.float32)
        M=cv2.getPerspectiveTransform(src,dst)
        # pad source by edge replication so interior edges sample cleanly
        pad=4
        pp=cv2.copyMakeBorder(pan,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
        Tm=np.array([[1,0,-pad],[0,1,-pad],[0,0,1]],np.float64)
        Mp=M@np.linalg.inv(np.array([[1,0,pad],[0,1,pad],[0,0,1.]]))
        col=cv2.warpPerspective(pp,Mp,(cw,ch),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
        m=np.zeros((ch,cw),np.uint8)
        cv2.fillPoly(m,[np.int32(np.round(dst*8))],255,lineType=cv2.LINE_AA,shift=3)
        m=m.astype(np.float32)/255
        acc+=col*m[...,None]; al+=m
    a=np.clip(al,1e-6,None)
    col=acc/a[...,None]; al=np.clip(al,0,1)
    col=cv2.resize(col,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)
    al=cv2.resize(al,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)
    return col,al,(x0,y0)

def grow(T,B,d=0.8):
    T=[(x,y-d) for x,y in T]; B=[(x,y+d) for x,y in B]
    T[0]=(T[0][0]-d,T[0][1]); B[0]=(B[0][0]-d,B[0][1]); T[-1]=(T[-1][0]+d,T[-1][1]); B[-1]=(B[-1][0]+d,B[-1][1])
    return T,B
L_top,L_bot=grow(L_top,L_bot); R_top,R_bot=grow(R_top,R_bot)
# rebuild the 2px halo just outside each brochure (old edge colours) from the table around it
bg8=(bg*255).astype(np.uint8)
hm=np.zeros((H,W),np.uint8)
for T,B in [(L_top,L_bot),(R_top,R_bot)]:
    cv2.fillPoly(hm,[np.int32(np.round(np.array(T+B[::-1])*8))],255,shift=3)
hm=cv2.dilate(hm,np.ones((5,5),np.uint8))
fill=cv2.inpaint(bg8,hm,4,cv2.INPAINT_TELEA).astype(np.float32)/255
bg_clean=bg*(1-(hm[...,None]>0))+fill*(hm[...,None]>0)
out=bg_clean.copy()
layers=[]
for name,des,sp,T,B in [('L',ext,ext_split,L_top,L_bot),('R',inn,inn_split,R_top,R_bot)]:
    col,al,(x0,y0)=render(des,sp,T,B,LIGHT[name])
    # photographic softness + grain
    col=cv2.GaussianBlur(col,(0,0),0.45)
    rng=np.random.default_rng(7)
    col=col+rng.normal(0,0.006,col.shape).astype(np.float32)
    h,w=al.shape
    reg=out[y0:y0+h,x0:x0+w]
    out[y0:y0+h,x0:x0+w]=col*al[...,None]+reg*(1-al[...,None])

# fold crease highlights / shadows
def crease(p,q,val,alpha,width=1.0):
    global out
    m=np.zeros((H*4,W*4),np.uint8)
    cv2.line(m,(int(p[0]*4*8),int(p[1]*4*8)),(int(q[0]*4*8),int(q[1]*4*8)),255,int(max(1,width*4)),cv2.LINE_AA,shift=3)
    m=cv2.resize(m.astype(np.float32)/255,(W,H),interpolation=cv2.INTER_AREA)*alpha
    out=out*(1-m[...,None])+np.float32(val)*m[...,None]
crease(L_top[1],L_bot[1],(0.15,0.15,0.17),0.18,1.2)
crease(L_top[2],L_bot[2],(0.97,0.97,0.97),0.45,1.4)
crease(R_top[1],R_bot[1],(0.95,0.95,0.95),0.25,1.2)
crease(R_top[2],R_bot[2],(0.12,0.12,0.14),0.22,1.2)

# thin contact shadow where the paper meets the table
for T,B in [(L_top,L_bot),(R_top,R_bot)]:
    for i in range(3):
        p=(B[i][0],B[i][1]+0.9); q=(B[i+1][0],B[i+1][1]+0.9)
        crease(p,q,(0.16,0.13,0.10),0.35,1.3)
# restore pencils (occluders in front of the inside brochure)
ox=bg; r,g,b=ox[...,0],ox[...,1],ox[...,2]
mx=ox.max(2)
pen=((b/np.clip(r,1e-3,None)>0.37)&(mx<0.80))|(mx<0.36)
reg=np.zeros((H,W),bool); reg[752:806,792:905]=True
pen&=reg
inside=np.zeros((H,W),np.uint8)
cv2.fillPoly(inside,[np.int32(np.round(np.array(R_top+R_bot[::-1])))],1)
inside=cv2.erode(inside,np.ones((7,7),np.uint8))>0
core=(pen&inside).astype(np.uint8)
core=cv2.morphologyEx(core,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
grown=cv2.dilate(core,np.ones((7,7),np.uint8))>0
pen=(core>0)|(grown&pen)
pen=pen.astype(np.float32)
pen=cv2.morphologyEx(pen,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
pen=cv2.GaussianBlur(pen,(0,0),0.55)
np.save('penmask.npy',pen)
out=bg*pen[...,None]+out*(1-pen[...,None])

Image.fromarray((np.clip(out,0,1)*255+0.5).astype(np.uint8)).save('mockup.png')
Image.fromarray((pen*255).astype(np.uint8)).save('penmask.png')
print('ok')
