# Resize / compress source visuals into build/assets, and pre-render the finishing textures
import os, glob, numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
Image.MAX_IMAGE_PIXELS=None
S='/tmp/claude-0/-home-user-HANDY/36455e3e-c271-5390-ad89-57cd94b34b42/scratchpad'
X=S+'/dl/x'; M=S+'/dl/docxmedia/word/media'; A=S+'/build/assets'; os.makedirs(A,exist_ok=True)
LB=glob.glob(X+'/LOGO_BRANDING/*')[0]
def save(src,name,lim=2000,keep_alpha=False,q=86,crop=None):
    im=Image.open(src)
    if crop: im=im.crop(crop)
    im.thumbnail((lim,lim),Image.LANCZOS)
    if keep_alpha:
        im.convert('RGBA').save(f'{A}/{name}.png',optimize=True)
    else:
        if im.mode in('RGBA','LA','P'):
            im=im.convert('RGBA'); bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); im=bg
        im.convert('RGB').save(f'{A}/{name}.jpg',quality=q,optimize=True,progressive=True)
I=S+'/../images'
save(I+'/1.png','logo_noir',1274,True); save(I+'/2.png','logo_blanc',1274,True)
save(LB+'/logotype_marinor.png','logo_couleur',1277,True); save(LB+'/logo_icon.png','logo_icon',600,True)
for n,f in [('rough1','1ere piste esquisse logo.png'),('rough2','2eme piste esquisse logo.png'),('rough3','3eme piste esquisse logo.png'),
            ('zone','logo_marinor_avec_zone_de protection.png'),('declinaisons','declinaisons.png'),('interdits','interdits.png')]:
    save(f'{LB}/{f}',n,1600)
g=lambda d:glob.glob(f'{X}/{d}/**/*.png',recursive=True)
pick=lambda d,s:[f for f in g(d) if s in os.path.basename(f)][0]
save(pick('AFFICHE1','Affiche1'),'affiche1',2200); save(pick('AFFICHE1','Mise'),'affiche1_situ',1500)
save(pick('AFFICHE2','Affiche2'),'affiche2',2200); save(pick('AFFICHE2','Mise'),'affiche2_situ',1500)
save(pick('AFFICHE3','Affiche3'),'affiche3',2200); save(pick('AFFICHE3','Mise'),'affiche3_situ',1500)
save(pick('FLYER','Flyer'),'flyer',1700); save(pick('FLYER','Mise'),'flyer_situ',1445)
save(pick('KAKEMONO','Kakemono'),'kakemono',1800); save(pick('KAKEMONO','Mise'),'kakemono_situ',1532)
save(pick('DEPLIANT','EXTERIEUR'),'depliant_recto',1600); save(pick('DEPLIANT','verso'),'depliant_verso',1600); save(pick('DEPLIANT','mockup'),'depliant_situ',1600)
for n,s in [('polos','POLOS'),('camion','CAMION'),('sac','SAC'),('carnet','CARNET'),('carte','CARTE'),('tabliers','CUISINE'),('packshot','Cosmetic')]:
    d={'POLOS':'MOCKUPS_PT1','CAMION':'MOCKUPS_PT2','SAC':'MOCKUPS_PT2','Cosmetic':'MOCKUPS_PT2'}.get(s,'MOCKUPS_PT3')
    save(pick(d,s),n,1600)
# memoir figures
for n,f in [('arbo_client','image26.png'),('arbo_admin','image27.png'),('mcd','image51.png'),('phpmyadmin','image101.png'),
            ('spot2d_ae','image73.png'),('spot3d_b1','image74.png'),('spot3d_b2','image75.png'),('typos','image14.png')]:
    save(f'{M}/{f}',n,2000)
sd=sorted(glob.glob(X+'/IMAGES_DU_SITE/*/*.png'))
for i,f in enumerate(sd): save(f,f'site_{i:02d}',1800,q=90)
# hero food photo: sharp + blurred warm versions
food=Image.open(glob.glob(X+'/elements_graphiques/**/IMAGE.png',recursive=True)[0]).convert('RGB')
food.thumbnail((2400,2400),Image.LANCZOS); food.save(f'{A}/food.jpg',quality=86)
w,h=food.size; c=food.crop((0,int(h*0.18),w,int(h*0.18)+int(w*9/16))).resize((1920,1080),Image.LANCZOS)
b=c.filter(ImageFilter.GaussianBlur(14)); b=ImageEnhance.Color(b).enhance(1.15); b=ImageEnhance.Brightness(b).enhance(0.62)
b.save(f'{A}/food_blur.jpg',quality=85)
# finishing textures
rng=np.random.default_rng(7)
n=rng.normal(0,1,(1080,1920)); n=(np.clip(n*40+128,0,255)).astype('uint8')
alpha=np.full((1080,1920),14,'uint8')   # ~8% alpha monochrome grain
Image.fromarray(np.dstack([n,n,n,alpha]),'RGBA').save(f'{A}/grain.png',optimize=True)
yy,xx=np.mgrid[0:1080,0:1920]; r=np.sqrt(((xx-960)/960)**2+((yy-540)/540)**2)
va=(np.clip((r-0.55)/0.75,0,1)**1.6*170).astype('uint8'); z=np.zeros_like(va)
Image.fromarray(np.dstack([z+18,z+3,z+6,va]),'RGBA').save(f'{A}/vignette.png',optimize=True)
# golden bokeh / spice dust for the appetite slide
bk=Image.new('RGBA',(1920,1080),(0,0,0,0)); d=ImageDraw.Draw(bk)
for i in range(70):
    x,y=rng.uniform(0,1920),rng.uniform(0,1080)**1.0; rad=rng.uniform(3,26); a=int(rng.uniform(25,90))
    col=[(249,168,37),(251,208,33),(255,236,209)][i%3]
    d.ellipse([x-rad,y-rad,x+rad,y+rad],fill=col+(a,))
bk=bk.filter(ImageFilter.GaussianBlur(6)); bk.save(f'{A}/bokeh.png',optimize=True)
# brand motif pattern layers (very low opacity), for the parallax camera plate
mot=Image.open(LB+'/motif.png').convert('RGBA'); mw=Image.open(LB+'/motif_version_white.png').convert('RGBA')
def tile(src,col,alpha,name):
    t=src.copy(); t.thumbnail((700,700)); arr=np.array(t); m=arr[...,3].astype(float)
    if src is mot: m=m*(arr[...,:3].mean(-1)<128)   # black glyphs only
    out=np.zeros_like(arr); out[...,0],out[...,1],out[...,2]=col; out[...,3]=(m/255*alpha).astype('uint8')
    t=Image.fromarray(out,'RGBA'); W,H=3200,1800; big=Image.new('RGBA',(W,H))
    for yy in range(0,H,t.size[1]):
        for xx in range(0,W,t.size[0]): big.alpha_composite(t,(xx,yy))
    big.save(f'{A}/{name}.png',optimize=True)
tile(mot,(123,20,33),10,'motif_bord'); tile(mot,(255,236,209),10,'motif_creme')
print(sorted(os.listdir(A)))
