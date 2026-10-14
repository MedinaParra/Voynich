"""Layout utilities that never receive reference rows or text labels."""
from __future__ import annotations
import math
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import linear_sum_assignment

def in_polygon(point, polygon):
    x,y=point;inside=False
    for i,(x0,y0) in enumerate(polygon):
        x1,y1=polygon[(i+1)%len(polygon)]
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0:
            inside=not inside
    return inside

def inside_regions(point, region):
    return any(in_polygon(point,p) for p in region['polygons'])

def samples(line,size,count=21):
    w,h=size
    pts=line.get('baseline')
    if not pts:
        a=line['bbox_pixels'];pts=[[a[0],(a[1]+a[3])/2],[a[2],(a[1]+a[3])/2]]
    pts=np.array(pts,dtype=float)
    if len(pts)==1:pts=np.repeat(pts,2,axis=0)
    distances=np.r_[0,np.cumsum(np.sqrt(np.sum(np.diff(pts,axis=0)**2,axis=1)))]
    if not distances[-1]:return [(pts[0,0]/w,pts[0,1]/h)]*count
    positions=np.linspace(0,distances[-1],count)
    return list(zip(np.interp(positions,distances,pts[:,0])/w,
                    np.interp(positions,distances,pts[:,1])/h))

def filter_paragraphs(lines,size,regions,min_fraction=.5):
    kept=[]
    for line in lines:
        points=samples(line,size)
        scores=[sum(inside_regions(p,r) for p in points)/len(points) for r in regions]
        if not scores:continue
        i=int(np.argmax(scores))
        if scores[i]>=min_fraction:
            kept.append({**line,'paragraph':regions[i]['paragraph'],'region_fraction':scores[i]})
    return kept

def row_union(members,size,paragraph):
    w,h=size
    boxes=[r['bbox_pixels'] for r in members]
    b=[min(x[0] for x in boxes),min(x[1] for x in boxes),
       max(x[2] for x in boxes),max(x[3] for x in boxes)]
    return {'paragraph':paragraph,'bbox_pixels':b,
            'bbox_normalized':[b[0]/w,b[1]/h,b[2]/w,b[3]/h],
            'member_indices':[r['index'] for r in members]}

def assemble(lines,size,regions,tolerance_factor=.45,deskew=False,min_fraction=.5):
    kept=filter_paragraphs(lines,size,regions,min_fraction)
    rows=[]
    for paragraph in sorted({r['paragraph'] for r in kept}):
        group=[r for r in kept if r['paragraph']==paragraph]
        heights=[r['bbox_pixels'][3]-r['bbox_pixels'][1] for r in group]
        tolerance=max(3.,float(np.median(heights))*tolerance_factor)
        slopes=[]
        for r in group:
            pts=r.get('baseline') or []
            if len(pts)>1 and abs(pts[-1][0]-pts[0][0])>10:
                slopes.append((pts[-1][1]-pts[0][1])/(pts[-1][0]-pts[0][0]))
        slope=float(np.clip(np.median(slopes),-.15,.15)) if deskew and slopes else 0.
        anchors=[]
        for r in group:
            pts=r.get('baseline') or [[(r['bbox_pixels'][0]+r['bbox_pixels'][2])/2,
                                      (r['bbox_pixels'][1]+r['bbox_pixels'][3])/2]]
            anchor=float(np.median([y-slope*x for x,y in pts]))
            anchors.append((anchor,r))
        clusters=[]
        for anchor,line in sorted(anchors,key=lambda x:(x[0],x[1]['bbox_pixels'][0])):
            eligible=[c for c in clusters if all(abs(anchor-a)<=tolerance for a,_ in c)]
            if eligible:
                target=min(eligible,key=lambda c:abs(anchor-np.median([a for a,_ in c])))
                target.append((anchor,line))
            else:clusters.append([(anchor,line)])
        for c in clusters:
            row=row_union([r for _,r in c],size,paragraph)
            row['anchor']=float(np.median([a for a,_ in c]));row['slope']=slope
            row['tolerance_pixels']=tolerance;rows.append(row)
    return rows,kept

def box_iou(a,b):
    i=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    area=lambda x:max(0,x[2]-x[0])*max(0,x[3]-x[1])
    union=area(a)+area(b)-i
    return i/union if union else 0.

def matches(pred,truth,threshold=.5):
    pairs=[]
    if pred and truth:
        matrix=np.array([[box_iou(a,b) for b in truth] for a in pred])
        score=(matrix>=threshold)*(min(len(pred),len(truth))+1)+matrix
        rows,cols=linear_sum_assignment(-score)
        pairs=[{'pred':int(i),'truth':int(j),'iou':float(matrix[i,j])}
               for i,j in zip(rows,cols) if matrix[i,j]>=threshold]
    tp=len(pairs);denom=len(pred)+len(truth)
    return {'tp':tp,'fp':len(pred)-tp,'fn':len(truth)-tp,
            'precision':tp/len(pred) if pred else (1. if not truth else 0.),
            'recall':tp/len(truth) if truth else (1. if not pred else 0.),
            'f1':2*tp/denom if denom else 1.,'pairs':pairs,
            'pred_count':len(pred),'truth_count':len(truth),'threshold':threshold}

def levenshtein(a,b):
    prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        curr=[i]
        for j,y in enumerate(b,1):curr.append(min(curr[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=curr
    return prev[-1]

def pua_text(tokens,mapping):
    out=[]
    for token in tokens:
        symbols=token.split(',')
        missing=[x for x in symbols if x not in mapping]
        if missing:raise ValueError('Unmapped Boxer units: '+repr(missing))
        out.append(''.join(mapping[s] for s in symbols))
    return ' '.join(out)

def row_image_name(row_id):
    # Kraken 7.1 strips ALL suffixes when looking for the paired .gt.txt.
    # Keep logical dotted row IDs in metadata, but never in image basenames.
    if not row_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in row_id):
        raise ValueError('Unsafe row identifier')
    return row_id.replace('.','_')+'.png'

def mask_image(im,regions):
    mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
    for region in regions:
        for poly in region['polygons']:
            draw.polygon([(round(x*im.width),round(y*im.height)) for x,y in poly],fill=255)
    return Image.composite(im.convert('RGB'),Image.new('RGB',im.size,'white'),mask)

def image_features(im):
    data=np.asarray(im.convert('L').resize((64,16),Image.Resampling.LANCZOS),dtype=float)/255.
    v=(data-data.mean())/max(.05,float(data.std()))
    return v.ravel(),math.log(im.width/im.height)

def nearest_text(im,train):
    a,aspect=image_features(im)
    scores=[float(np.mean((a-b['features'][0])**2))+.05*(aspect-b['features'][1])**2 for b in train]
    i=int(np.argmin(scores))
    return train[i]['text'],train[i]['id']
