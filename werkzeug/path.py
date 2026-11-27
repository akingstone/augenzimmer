import cv2, numpy as np, sys
def path(fn, show=True):
    cap=cv2.VideoCapture(fn); prev=None; P=[np.zeros(2)]; W=640
    while True:
        ok,f=cap.read()
        if not ok: break
        g=cv2.cvtColor(cv2.resize(f,(W,int(f.shape[0]*W/f.shape[1]))),cv2.COLOR_BGR2GRAY)
        H=g.shape[0]
        if prev is not None:
            mask=np.full(g.shape,255,np.uint8); cv2.ellipse(mask,(int(W*.52),int(H*.55)),(int(W*.30),int(H*.27)),0,0,360,0,-1)
            pts=cv2.goodFeaturesToTrack(prev,300,0.005,8,mask=mask)
            if pts is None: P.append(P[-1]); prev=g; continue
            nxt,st,_=cv2.calcOpticalFlowPyrLK(prev,g,pts,None,winSize=(31,31),maxLevel=3)
            d=(nxt-pts)[st[:,0]==1][:,0]
            P.append(P[-1]+np.median(d,0)*(1280/W) if len(d)>5 else P[-1])
        prev=g
    P=np.array(P); d=np.diff(P,axis=0)
    if show: print(fn,'Zittern px/Bild (Median):',np.median(np.abs(d),0).round(2),' Spannweite:',(P.max(0)-P.min(0)).round(0))
    return P
if __name__=='__main__':
    for f in sys.argv[1:]: path(f)
