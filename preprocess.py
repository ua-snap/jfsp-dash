"""

Preprocess Alfresco data into shapes that can
be easily used by JFSP app.

"""

import sys

sys.path.append("./preprocess")
sys.path.append(".")

import luts
import area
import veg
import cost

data_dir = "data"

area.process(data_dir)
# veg.process(data_dir)
# cost.process(data_dir)
