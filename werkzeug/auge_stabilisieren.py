import cv2, numpy as np, subprocess, sys
sys.path.insert(0,'.'); from path import path
from scipy.ndimage import gaussian_filter1d
SRC=sys.argv[1]; OUT=sys.argv[2]   # SRC: auf SDR umgewandeltes Video (siehe README)
P=path(SRC,False)                       # Kamerabewegung in "1280er" Pixeln der Quellbreite
P=np.stack([gaussian_filter1d(P[:,k],1.0,mode='nearest') for k in range(2)],1)
P-=np.median(P,0)
cap=cv2.VideoCapture(SRC); W0=int(cap.get(3)); H0=int(cap.get(4)); k=W0/1280
OW,OH=1280,720; Z=1.12                   # leichtes Heranzoomen als Reserve
CW=W0/Z; CH=CW*9/16; s=OW/CW; cx,cy=W0/2,H0*0.52
enc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{OW}x{OH}','-r','30','-i','-',
  '-vf','hqdn3d=2:1.5:4:4,eq=saturation=0.86:brightness=0.015,unsharp=5:5:0.5:5:5:0','-c:v','libx264','-preset','slow','-crf','18','-g','15','-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    dx,dy=P[min(i,len(P)-1)]*k
    M=np.float32([[s,0,OW/2-s*(cx+dx)],[0,s,OH/2-s*(cy+dy)]])
    enc.stdin.write(cv2.warpAffine(f,M,(OW,OH),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT).tobytes()); i+=1
enc.stdin.close(); enc.wait(); print('frames',i, 'max shift', np.abs(P).max(0).round(0))
