from modules.orbbec_utilities import *

resolutionWidth = 320
resolutionHeight = 240

astra = Astra(
    [
        "color",
        "depth"
    ],
    (resolutionWidth, resolutionHeight),
)

running = True 

while running:
    swivel_color_frame = astra._get_color_frame(0)
    swivel_depth_frame = astra._get_depth_frame(0)
    
    fixed_color_frame = astra._get_color_frame(1)
    fixed_depth_frame = astra._get_depth_frame(1)
    
    cv2.imshow("swivel color", swivel_color_frame)
    cv2.imshow("swivel depth", swivel_depth_frame)
    cv2.imshow("fixed color", fixed_color_frame)
    cv2.imshow("fixed depth", fixed_depth_frame)
    
    if cv2.waitKey(15)==27:
        running = False 
        
astra._destroy()
cv2.destroyAllWindows()