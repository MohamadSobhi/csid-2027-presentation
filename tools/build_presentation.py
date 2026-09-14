import argparse, hashlib, json, os, posixpath, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def export_foreground(slide, meta, root, width, height):
 if not meta['media']:return
 from PIL import Image
 import tempfile
 shapes=list(slide.Shapes)
 last=max((i for i,s in enumerate(shapes) if s.Type==16),default=-1)
 foreground=[s for s in shapes[last+1:] if s.Visible] if last>=0 else []
 if not foreground:return
 layer=Image.new('RGBA',(width,height),(0,0,0,0))
 with tempfile.TemporaryDirectory() as temp:
  for sh in foreground:
   svg=Path(temp)/'shape.svg';png=Path(temp)/'shape.png'
   sh.Export(str(svg),6)
   markup=svg.read_text(encoding='utf-8-sig')
   origin=re.search(r'<g transform="translate\(([-\d.]+)[ ,]+([-\d.]+)\)"',markup)
   if not origin:raise RuntimeError('Cannot resolve foreground shape export bounds')
   sh.Export(str(png),2,round(width*0.75),round(height*0.75),1)
   # SVG uses 96-DPI slide coordinates; PNG is exported at width x height.
   factor=width/(slide.Parent.PageSetup.SlideWidth*4/3)
   x=round(-float(origin.group(1))*factor);y=round(-float(origin.group(2))*factor)
   with Image.open(png) as part:layer.alpha_composite(part.convert('RGBA'),(x,y))
 meta['foreground']=f"assets/images/foreground-{meta['number']:03}.png"
 layer.save(root/meta['foreground'])

def _build(source):
 source=Path(source).resolve(); before=hashlib.sha256(source.read_bytes()).hexdigest()
 for folder in ['slides','slides/thumbs','assets/video','assets/audio','assets/images','data']:(ROOT/folder).mkdir(parents=True,exist_ok=True)
 def save(name,data): (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 with zipfile.ZipFile(source) as z:
  def xml(path): return ET.fromstring(z.read(path))
  def rels(path):
   rp=posixpath.join(posixpath.dirname(path),'_rels',posixpath.basename(path)+'.rels')
   return {r.attrib['Id']:{**r.attrib,'resolved':posixpath.normpath(posixpath.join(posixpath.dirname(path),r.attrib['Target']))} for r in xml(rp)} if rp in z.namelist() else {}
  pr=xml('ppt/presentation.xml'); size=pr.find('p:sldSz',NS); w,h=int(size.get('cx')),int(size.get('cy')); rr=rels('ppt/presentation.xml')
  paths=[rr[s.get('{'+NS['r']+'}id')]['resolved'] for s in pr.find('p:sldIdLst',NS)]
  fonts=Counter(); slides=[]; notes={}; totals=Counter()
  for part in z.namelist():
   if part.startswith('ppt/') and part.endswith('.xml'):
    for el in xml(part).iter():
     if el.get('typeface'):fonts[el.get('typeface')]+=1
  def extract(part,category):
   dest='assets/'+category+'/'+posixpath.basename(part)
   (ROOT/dest).write_bytes(z.read(part));return dest
  for i,path in enumerate(paths,1):
   r=xml(path); rel=rels(path); count=Counter(el.tag.split('}')[-1] for el in r.iter());totals.update(count)
   slide={'number':i,'image':f'slides/slide-{i:03}.png','thumbnail':f'slides/thumbs/slide-{i:03}.webp','media':[],'links':[],'text':'\n'.join(e.text or '' for e in r.findall('.//a:t',NS)),'hasAnimations':bool(r.find('p:timing',NS) is not None),'hasTransition':any(e.tag.endswith('}transition') for e in r.iter()),'hidden':r.get('show')=='0'}
   for shape in r.findall('.//p:pic',NS)+r.findall('.//p:sp',NS):
    xf=shape.find('.//a:xfrm',NS)
    if xf is None:continue
    off,ext=xf.find('a:off',NS),xf.find('a:ext',NS)
    if off is None or ext is None:continue
    rect={'x':int(off.get('x'))/w,'y':int(off.get('y'))/h,'width':int(ext.get('cx'))/w,'height':int(ext.get('cy'))/h}
    for e in shape.iter():
     kind=e.tag.split('}')[-1]
     if kind in ['videoFile','audioFile']:
      rid=e.get('{'+NS['r']+'}link'); relationship=rel.get(rid,{})
      if relationship.get('TargetMode')=='External':raise RuntimeError('Linked media requires handling: '+relationship.get('Target',''))
      part=relationship.get('resolved')
      if part:
       media={'kind':'video' if kind=='videoFile' else 'audio','src':extract(part,'video' if kind=='videoFile' else 'audio'),**rect}
       blip=shape.find('.//a:blip',NS)
       if blip is not None:
        poster=rel.get(blip.get('{'+NS['r']+'}embed'),{}).get('resolved')
        if poster:media['poster']=extract(poster,'images')
       slide['media'].append(media)
     if kind=='hlinkClick':
      link=rel.get(e.get('{'+NS['r']+'}id'),{})
      if link.get('TargetMode')=='External' and link.get('Target','').startswith(('https://','http://','mailto:')):slide['links'].append({'href':link['Target'],**rect})
      elif link.get('resolved') in paths:slide['links'].append({'href':'#slide-'+str(paths.index(link['resolved'])+1),**rect})
   for relationship in rel.values():
    if relationship['Type'].endswith('/notesSlide'):
     nr=xml(relationship['resolved']);paras=[]
     for sp in nr.findall('.//p:sp',NS):
      ph=sp.find('.//p:ph',NS)
      if ph is not None and ph.get('type') in ['sldNum','hdr','ftr','dt','sldImg']:continue
      paras.extend(''.join(t.text or '' for t in p.findall('.//a:t',NS)) for p in sp.findall('.//a:p',NS))
     note='\n'.join(paras).strip()
     if note:notes[str(i)]=note
   slides.append(slide)
  metadata={'width':w,'height':h,'aspectRatio':w/h,'slides':slides}
  save('data/slides.json',metadata);save('data/notes.json',notes)
  save('data/source-analysis.json',{'slideCount':len(slides),'sizeEMU':[w,h],'fonts':sorted(fonts),'elementCounts':dict(totals),'notesSlides':list(notes),'sourceSHA256':before,'media':[{ 'slide':s['number'],**m} for s in slides for m in s['media']],'animationsSlides':[s['number'] for s in slides if s['hasAnimations']],'transitionSlides':[s['number'] for s in slides if s['hasTransition']]})
 import win32com.client
 from PIL import Image
 app=win32com.client.DispatchEx('PowerPoint.Application')
 deck=None
 try:
  deck=app.Presentations.Open(str(source),ReadOnly=True,Untitled=False,WithWindow=False)
  height=round(3840*h/w)
  for i in range(1,deck.Slides.Count+1):
   dst=ROOT/f'slides/slide-{i:03}.png';deck.Slides(i).Export(str(dst),'PNG',3840,height)
   with Image.open(dst) as im:
    im.thumbnail((480,270));im.save(ROOT/f'slides/thumbs/slide-{i:03}.webp',quality=85)
   export_foreground(deck.Slides(i), slides[i-1], ROOT, 3840, height)
   print(f'Exported {i}/{deck.Slides.Count}',flush=True)
 finally:
  if deck is not None:deck.Close()
  app.Quit()
 save('data/slides.json',metadata)
 assert hashlib.sha256(source.read_bytes()).hexdigest()==before,'Source changed unexpectedly'
 print('Build complete; source hash unchanged.',flush=True)
def build(source):
 global ROOT
 import tempfile, shutil
 project=ROOT
 with tempfile.TemporaryDirectory(prefix='.build-',dir=project) as temp:
  staging=Path(temp)/'new';staging.mkdir();ROOT=staging
  try:_build(source)
  finally:ROOT=project
  moved=[]
  try:
   for name in ['slides','assets','data']:
    destination=project/name;backup=Path(temp)/('old-'+name)
    if destination.exists():destination.rename(backup)
    moved.append((destination,backup))
    (staging/name).rename(destination)
  except Exception:
   for destination,backup in reversed(moved):
    if destination.exists():shutil.rmtree(destination)
    if backup.exists():backup.rename(destination)
   raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source');args=p.parse_args()
 config=ROOT/'source.local.json'
 source=args.source or os.environ.get('CSID_PPTX') or (json.loads(config.read_text(encoding='utf-8-sig'))['source'] if config.exists() else None)
 if not source:p.error('Set CSID_PPTX or pass --source PATH; see README.')
 build(source)

