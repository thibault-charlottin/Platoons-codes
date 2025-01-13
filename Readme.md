This reposit contains the codes for platoon detection presented in the paper <br>
"Birth life and death of a platoon" <br>
Authors : Thibault Charlottin, Silvia Varotto and Christine Buisson<br>

Requierements:<br>
- pandas
- numpy
- dtaidistance
- dtaidistance

How to run the code:<be
- first, import your trajectory dataset.
- Preprocess your dataset to define a leader for each vehicle at each timestamp. A leader is defined by the first vehicle upstream on the ego vehicle, in the ego lane. A proposal for this method, based on 
- Run detect_CF.py script. You will be required to declare the column name for the ID of the vehicles, the name of the column defining the time and the name of the column defining the X road coordinate. This script will give you the DTW values of all leader-follower pairs.
- Once all DTW values have been computed. Run detect_string.py script. You will be required to declare the column name for the ID of the vehicles, the name of the column defining the time and the name of the column defining the X road coordinate. THis script will give you the platoons and the DTW values for the vehicles in the platoon. This DTW gives the similarity between the platoon's leader and ego vehicle.
