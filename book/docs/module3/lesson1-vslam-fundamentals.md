---
title: "Lesson 1: VSLAM Fundamentals"
sidebar_position: 2
description: "Visual Simultaneous Localization and Mapping - feature detection, pose estimation, and map building."
---

# Lesson 1: VSLAM Fundamentals

## Prediction Phase

- How can a robot determine its position using only camera images?
- Why is it called "simultaneous" localization and mapping?
- What happens when the robot revisits a previously seen location?

---

## What is VSLAM?

**Visual Simultaneous Localization and Mapping (VSLAM)** enables a robot to:
1. **Localize**: Determine its position and orientation in the environment
2. **Map**: Build a representation of the surrounding environment
3. **Simultaneously**: Do both at the same time, using one to improve the other

### VSLAM vs Lidar SLAM

| Feature | VSLAM | Lidar SLAM |
|---------|-------|------------|
| Sensor | Camera (RGB/stereo/RGBD) | Lidar scanner |
| Cost | Low ($20-200 camera) | High ($200-10,000+) |
| Information | Rich visual features, color | Precise range measurements |
| Compute | Higher (feature extraction) | Lower (point matching) |
| Outdoor | Good with texture | Excellent |
| Indoor | Excellent | Good |

## Feature Detection and Matching

VSLAM begins by detecting distinctive visual features in camera images.

### ORB Features

ORB (Oriented FAST and Rotated BRIEF) is the most common feature detector for real-time VSLAM:

```python
import cv2

# Initialize ORB detector
orb = cv2.ORB_create(nfeatures=1000)

# Detect keypoints and compute descriptors
image = cv2.imread('frame_001.png', cv2.IMREAD_GRAYSCALE)
keypoints, descriptors = orb.detectAndCompute(image, None)

# Draw detected features
output = cv2.drawKeypoints(image, keypoints, None, color=(0, 255, 0))
cv2.imshow('ORB Features', output)
```

### Feature Matching Between Frames

```python
# Match features between two frames
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

frame1_kp, frame1_desc = orb.detectAndCompute(frame1, None)
frame2_kp, frame2_desc = orb.detectAndCompute(frame2, None)

matches = bf.match(frame1_desc, frame2_desc)
matches = sorted(matches, key=lambda x: x.distance)

# Use top matches for pose estimation
good_matches = matches[:50]
```

## Pose Estimation

From matched features, VSLAM estimates the camera's motion:

1. **Essential Matrix**: Encodes rotation and translation between frames
2. **PnP Solver**: Determines pose from 3D-2D point correspondences
3. **Bundle Adjustment**: Refines all poses and 3D points simultaneously

```python
import numpy as np

# Extract matched point coordinates
pts1 = np.float32([frame1_kp[m.queryIdx].pt for m in good_matches])
pts2 = np.float32([frame2_kp[m.trainIdx].pt for m in good_matches])

# Compute essential matrix
E, mask = cv2.findEssentialMat(pts1, pts2, camera_matrix, method=cv2.RANSAC)

# Recover rotation and translation
_, R, t, _ = cv2.recoverPose(E, pts1, pts2, camera_matrix)
```

## Map Building

As the robot moves, VSLAM builds a 3D map of feature points:
- **Sparse Map**: 3D positions of tracked features (fast, used for localization)
- **Dense Map**: Full 3D reconstruction from depth data (detailed, used for navigation)

## Loop Closure

When the robot revisits a location, **loop closure** corrects accumulated drift:

1. Detect that current view matches a previous keyframe
2. Calculate the pose correction needed
3. Propagate correction through the entire trajectory
4. Optimize the full map

:::info Why Loop Closure Matters
Without loop closure, small errors accumulate over time, causing the map to drift. A corridor might appear to end in two different places. Loop closure "snaps" the map back into consistency.
:::

## VSLAM Pipeline Summary

```
Camera Frame → Feature Detection → Feature Matching → Pose Estimation
     ↓                                                      ↓
  Keyframe?  ←──────── Loop Closure Detection ←───── Map Update
     ↓                         ↓
  Add to Map          Pose Graph Optimization
```

---

## Execution Phase

1. Install OpenCV: `pip install opencv-python`
2. Capture images from a webcam or use a dataset
3. Run ORB feature detection on multiple frames
4. Match features between consecutive frames
5. Visualize the feature matches

---

## Reflection

- How many features were needed for reliable pose estimation?
- What happens in featureless environments (blank walls)?
- Why is ORB preferred over SIFT/SURF for real-time robotics?
- How would loop closure help in a large building?
