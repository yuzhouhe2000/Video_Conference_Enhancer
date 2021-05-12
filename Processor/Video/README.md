READ ME 

Written by Michael Pozzi 

The video pipeline can be found in this directory. 
The program to run along with the server and client is dlib_distance_detector.py.

The pipeline goes as follows:
    1. Get frame 
    2. Convert to gray 
    3. Get faces from detector 
    4. Find coordinates of face from rect 
    5. Get face width average 
    6. Adjust frame check value 
    7. Put rectange over face 
    8. Change servos 
    9. Find facial features from predictor 
    10. Put dots on features 
    11. Get left and right eye centers from features 
    12. Get Distance
    13. Get eye width average 
    14. Average eye dsitance 
    15. Check if face size has changed significantly 
    16. If changed significantly, adjust gain 
    17. Implement digital zoom 
    18. Display image 