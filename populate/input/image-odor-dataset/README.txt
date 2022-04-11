# Odeuropa Dataset of Olfactory Objects

This dataset is released as part of the Odeuropa project [1]. The annotations are identical to the training set of the ICPR2022-ODOR Challenge [2].
It contains bounding box annotations for smell-active objects in historical artworks gathered from various digital connections.
The smell-active objects annotated in the dataset either carry smells themselves or hint at the presence of smells.
The dataset provides 15484 bounding boxes on 2116 artworks in 87 object categories. 
An additional csv file contains further image-level metadata such as artist, collection, or year of creation.

## How to use
- Due to licensing issues, we cannot provide the images directly, but instead provide a collection of links and a download script. 
- To get the images, just run the `download_imgs.py` script which loads the images using the links from the `metadata.csv` file. The downloaded images can then be found in the `images` subfolder. The overall size of the downloaded images is c. 200MB. 
- The bounding box annotations can be found in the `annotations.json`. The annotations follow the COCO JSON format [3].
- The mapping between the `images` array of the `annotations.json` and the `metadata.csv` file can be accomplished via the `file_name` attribute of the elements of the `images` array and the unique `File Name` column of the `metadata.csv` file, respectively. 
- Additional image-level metadata is available in the `metadata.csv` file.


The creation of the dataset was partially funded by the EU's Horizon 2020 research and innovation programme under grant agreement No 101004469.


## References
[1] https://odeuropa.eu
[2] https://odor-challenge.odeuropa.eu
