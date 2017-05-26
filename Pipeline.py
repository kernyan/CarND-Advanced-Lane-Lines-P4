#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import *
from moviepy.editor import VideoFileClip

RegexCalibration = './camera_cal/*.jpg'
RegexTest        = './test_images/*.jpg'
List_TestImages  = GlobDirectory(RegexTest)
ImgTest0         = ReadImage(List_TestImages[0])

List_CalibrationImages = GlobDirectory(RegexCalibration)
Img0       = ReadImage(List_CalibrationImages[0])
Img_Size   = (Img0.shape[1], Img0.shape[0])

ObjPoints = []
ImgPoints = []
BoardSize = (9, 6)

ObjPoints, ImgPoints = FindChessBoardCorners(BoardSize, List_CalibrationImages)
Mtx, Dist = CalibrateCamera(ObjPoints, ImgPoints, Img_Size)
    
process_image = PipeLineWrapper(ImgPipeLine,
                                Mtx, 
                                Dist, 
                                MagicCorner_ProjectVideoSDC())

Output_Path = 'project_video_Out123.mp4'
clip1       = VideoFileClip('project_video.mp4')
VideoOut    = clip1.fl_image(process_image)
VideoOut.write_videofile(Output_Path, audio=False)
