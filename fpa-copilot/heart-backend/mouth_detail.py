"""Experimental local compositing: keep approved pixels outside the mouth area."""
import cv2
import numpy as np

# MediaPipe's outer lip contour, excluding eyes, nose and jaw.
LIPS=(61,185,40,39,37,0,267,269,270,409,291,375,321,405,314,17,84,181,91,146)


def blend_mouth(original, generated, source_lips, generated_lips):
    if original.shape!=generated.shape or original.dtype!=np.uint8 or generated.dtype!=np.uint8:
        raise ValueError('Matching uint8 video frames required.')
    height,width=original.shape[:2]
    points=np.concatenate((source_lips,generated_lips)).astype(np.float32)
    if points.shape!=(40,2) or not np.isfinite(points).all():
        raise ValueError('Two complete lip contours required.')
    if (points<0).any() or (points[:,0]>=width).any() or (points[:,1]>=height).any():
        raise ValueError('Lip contour is outside the frame.')
    span=np.ptp(points,axis=0)
    if span[0]<5 or span[0]>width*.35 or span[1]>height*.20:
        raise ValueError('Lip contour moved outside the expected mouth area.')
    mask=np.zeros((height,width),dtype=np.uint8)
    hull=cv2.convexHull(np.rint(points).astype(np.int32))
    cv2.fillConvexPoly(mask,hull,255)
    # Union of both contours covers the old and new lip/teeth positions.
    # A narrow feather blends their boundary without replacing the whole jaw.
    radius=max(2,int(round(span[0]*.12)))
    mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,radius*2+1)))
    kernel=radius*2+1
    alpha=cv2.GaussianBlur(mask,(kernel,kernel),0).astype(np.float32)/255
    outer=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,radius*2+1)))
    ring=(outer>0)&(mask==0)
    correction=np.median(original[ring].astype(np.float32)-generated[ring].astype(np.float32),axis=0) if ring.any() else np.zeros(3)
    matched=np.clip(generated.astype(np.float32)+correction,0,255)
    mixed=np.rint(original.astype(np.float32)*(1-alpha[:,:,None])+matched*alpha[:,:,None]).clip(0,255).astype(np.uint8)
    return mixed,alpha


class DetailBlender:
    def __init__(self):
        import mediapipe as mp
        self.detector=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1,refine_landmarks=False,min_detection_confidence=.5)
        self.source_cache={}

    def lip_points(self, frame):
        result=self.detector.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        if not result.multi_face_landmarks:
            raise RuntimeError('Mouth detail pass could not locate the face.')
        height,width=frame.shape[:2]
        points=result.multi_face_landmarks[0].landmark
        return np.array([(points[i].x*width,points[i].y*height) for i in LIPS],dtype=np.float32)

    def blend(self, original, generated, source_index):
        if source_index not in self.source_cache:
            self.source_cache[source_index]=self.lip_points(original)
        return blend_mouth(original,generated,self.source_cache[source_index],self.lip_points(generated))

    def close(self): self.detector.close()
