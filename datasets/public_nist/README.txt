NIST Data Publication:
Detection Limits for SEM Image Segmentation
Version 1.0.0
DOI: https://doi.org/10.18434/mds2-3838

Authors:
  Peter  Bajcsy
    National Institute of Standards and Technology
  Pushkar  Sathe
    National Institute of Standards and Technology
  Andras  Vladar
    National Institute of Standards and Technology

Contact:
  Peter Bajcsy
    peter.bajcsy@nist.gov

Description:

The dataset consists of six collections of SEM images, three trained U-net AI
models, and CSV files with image quality metrics and trained AI model accuracy
metrics. Each SEM image collection contains images augmented with Poisson noise
and contrast. 

Acknowledgment:

This work was performed with funding from the CHIPS Metrology
Program, part of CHIPS for America, National Institute of Standards and
Technology, U.S. Department of Commerce.

Disclaimer:

Statements and responses to questions about advanced microelectronics research and development programs in this presentation:
- Are informational, pre-decisional, and preliminary in nature.
- Do not constitute a commitment and are not binding on NIST or the Department of Commerce.
- Are subject in their entirety to any final action by NIST or the Department of Commerce..
Nothing in this presentation is intended to contradict or supersede the requirements published in any future policy documents or Notices of Funding Opportunity.

-------------------
General Information
-------------------

This data was [created/collected in 2024 and 2025]: [using simulation and custom-designed software].

Geographical coverage: [N/A]

Key funding sources: [the CHIPS Metrology Program]

--------------
Data Use Notes
--------------

This data is publicly available according to the NIST statements of
copyright, fair use and licensing; see
https://www.nist.gov/director/copyright-fair-use-and-licensing-statements-srd-data-and-software

You may cite the use of this data as follows:
Bajcsy, Peter, Sathe, Pushkar, Vladar, Andras (2025), Detection Limits for SEM
Image Segmentation, Version 1.0.0, National Institute of Standards and
Technology, https://doi.org/10.18434/mds2-3838 (Accessed: [give download date])

----------
References
----------


Peter Bajcsy, Brycie Wiseman, Michael Majurski, and Andras E. Vladar, "Detection Limits of AI-based SEM Dimensional Metrology", Proceedings of SPIE conference on Advanced Lithography + Patterning, 23 - 27 February 2025, San Jose, California, US, URL

Peter Bajcsy, Pushkar Sathe, and Andras E. Vladar, "Relating human and AI-based detection limits in SEM dimensional metrology", Under review.

-------------
Data Overview
-------------


    We used ARTIMAGEN SEM Simulation Software to generate images with varying contrast and noise level.
        Cizmar P., Vladár A., Postek M. “Optimization of accurate SEM imaging by use of artificial images”, Proc. SPIE 7378, Scanning Microscopy, 737815, 2009, URL
        Project URL and GitHub Repo URL
        License: As this software was developed as part of work done by the United States Government, it is not subject to copyright, and is in the public domain. Note that according to GNU.org public domain is compatible with GPL.

    We used UNet Convolutional Neural Network (CNN) AI model implementation By Michael Majurski (NIST) for training and inference of image segmentation
        Ronneberger, Olaf, Philipp Fischer, and Thomas Brox. "U-net: Convolutional networks for biomedical image segmentation." International Conference on Medical image computing and computer-assisted intervention. Springer, Cham, 2015.
        Name: WIPP UNet CNN Training Plugin and WIPP UNet CNN Inference Plugin
        Title: WIPP UNet CNN Training Plugin, Version: 1.0.0, Repository, Container image: wipp/wipp-unet-cnn-train-plugin:1.0.0
        Title: WIPP UNet CNN Inference Plugin, Version:1.0.0, Repository Container images: wipp/wipp-unet-cnn-inference-plugin:1.0.0

    The execution and full computational provenance were obtained by using the WIPP scientific workflow software:
        GitHub: WIPP code
        Bajcsy, P. , Chalfoun, J. and Simon, M. (2018), Web Microanalysis of Big Image Data, Springer International Publishing.


Files included in this publication:

  AImodel_sets.zip

    Three trained AI models (U-net architecture)
    Three trained AI models on the first five of six simulated SEM image
      collections
    Format: zip contains three folders with TensorFlow AI models
    [Detailed hyperparameters and pointers to computational provenance are provided below]

  intensity_sets.zip

    Six sets of simulated SEM images
    SEM images with varying noise and contrast values
    Format: zip file with six subfolders containing SEM image collections
    [## add'l info about this file (see recommendations above) ##]

  mask_sets.zip

    Six masks for the six simulated SEM image collections
    image masks defining foreground and background labels
    Format: zip file contains mask images and the initial intensity image with
      max contrast and min noise
    [## add'l info about this file (see recommendations above) ##]

  metrics_sets.zip

    Tabular files with image and AI model metrics
    Image quality metrics extracted from six simulated SEM images, as well as
      three AI model accuracy metrics obtained by evaluating the trained AI
      models on the sixth of the simulated SEM image collections.
    Format: zip file contains a folder with image quality metrics and a folder
      with AI model accuracy
    [## add'l info about this file (see recommendations above) ##]

  graphs
  
	relationships between AI model accuracy and image quality metrics is available at:
	https://pages.nist.gov/detection_limits/web/index.html
  
  Python code
	
	source code for detection limits is available at:
	https://github.com/usnistgov/detection_limits

---------------
Version History
---------------

1.0.0 (this version)
  initial release

--------------------------
Methodological Information
--------------------------

	See the publications for methodological information.

----------------------------------------------------
Computational Provenance of AI-based modeling
----------------------------------------------------

Computational workflows are in a workspace of Peter Bajcsy
login to wipp-dev.nist.gov (behind NIST firewall)
++++++++++++++++++++++++++++++++++++++

I. AI Modeling #1

I.1 Train

Training workflow (UNet-SEM-sim-SNR-v3) is available at 
https://wipp-dev.nist.gov/workflows/detail/67b7f6dd127d825c2e61297d

Training Parameters:
Job detail
Name:	UNet-SEM-sim-SNR-v3-train
Creation date:	Feb 20, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-SNR-v3
Plugin:	WIPP UNet CNN Training Plugin:1.0.0
Inputs 
imageDir	
SEM-sim-SNR-set1-5
maskDir	
SEM-sim-SNR-set1-5-mask-bin
useTiling	
NO
tileSize	
256
trainFraction	
0.7
batchSize	
4
numberClasses	
2
learningRate	
3e-4
testEveryNSteps	
10
balanceClasses	
YES
earlyStoppingEpochCount	
2
useIntensityScaling	
YES
useAugmentation	
NO
augmentationReflection	
YES
augmentationRotation	
YES
augmentationJitter	
0
augmentationScale	
0
augmentationNoise	
0
augmentationBlurMaxSigma	
0
augmentationIntensity	
0
Outputs 
tensorflowModel	
UNet-SEM-sim-SNR-v3-train-outputDir
tensorboardLogs	
UNet-SEM-sim-SNR-v3-train-tensorboardDir

The trained AI model (called UNet-SEM-sim-SNR-v3-train-outputDir) is available from 
https://wipp-dev.nist.gov/ai-models/67b7f94d127d825c2e61297f


I.2 Evaluate the accuracy  

The accuracy evaluation of the AI model is accomplished using a WIPP workflow consisting of two steps:
step 1: inference on set 6 
step 2: comparison of predicted segmentation mask with the ground truth masks


Job detail
Name:	UNet-SEM-sim-SNR-eval31-infer
Creation date:	Feb 21, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-SNR-eval31
Plugin:	WIPP UNet CNN Inference Plugin:1.0.0
Inputs 
imageDir	
SEM-sim-SNR-set6
model	
67b7f94d127d825c2e61297f
useIntensityScaling	
YES
Outputs 
collection	
UNet-SEM-sim-SNR-eval31-infer-outputDir


Job detail
Name:	UNet-SEM-sim-SNR-eval31-compare
Creation date:	Feb 21, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-SNR-eval31
Plugin:	wipp/wipp-dice-segmentationaccuracy:0.0.1
Computed in version:	3.2.0-SNAPSHOT
Inputs 
ground_truth	
SEM-sim-SNR-set6-mask-bin
prediction	
N/A
Outputs 
csvCollection	
UNet-SEM-sim-SNR-eval31-compare-output

The output is two CSV files available at
https://wipp-dev.nist.gov/csv-collections/67b8b8c2127d825c2e612dfb
The collection of two files is named: UNet-SEM-sim-SNR-eval31-compare-output

+++++++++++++++++++++++++++++++++++
II. AI Modeling #2

II.1 Train
Training on 5 sets --> trained AI model in WIPP
workflow name: UNet-SEM-sim-SNR-v5
https://wipp-dev.nist.gov/workflows/detail/67bd56f4127d825c2e613925

Training Parameters:
Job detail
Name:	UNet-SEM-sim-SNR-v5-train
Creation date:	Feb 25, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-SNR-v5
Plugin:	WIPP UNet CNN Training Plugin:1.0.0
Inputs 
imageDir	
SEM-sim-SNR-set1-5
maskDir	
SEM-sim-SNR-set1-5-mask-bin
useTiling	
NO
tileSize	
256
trainFraction	
0.8
batchSize	
8
numberClasses	
2
learningRate	
3e-4
testEveryNSteps	
5
balanceClasses	
YES
earlyStoppingEpochCount	
10
useIntensityScaling	
YES
useAugmentation	
YES
augmentationReflection	
YES
augmentationRotation	
YES
augmentationJitter	
0
augmentationScale	
0
augmentationNoise	
0
augmentationBlurMaxSigma	
0
augmentationIntensity	
0
Outputs 
tensorflowModel	
UNet-SEM-sim-SNR-v5-train-outputDir
tensorboardLogs	
UNet-SEM-sim-SNR-v5-train-tensorboardDir


The trained AI Model is available at https://wipp-dev.nist.gov/ai-models/67bd584c127d825c2e613927
 

II.2 Evaluate the accuracy  

workflow name: UNet-SEM-sim-eval51
https://wipp-dev.nist.gov/workflows/detail/67c627854bec7525e69f0cec

The accuracy evaluation of the AI model on set 6 is accomplished using a WIPP workflow consisting of two steps:
step 1: inference on set 6 
step 2: comparison of predicted segmentation mask with the ground truth masks

Step 1: Parameters

Job detail
Name:	UNet-SEM-sim-eval51-infer
Creation date:	Mar 3, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-eval51
Plugin:	WIPP UNet CNN Inference Plugin:1.0.0
Inputs 
imageDir	
SEM-sim-SNR-set6
model	
67bd584c127d825c2e613927
useIntensityScaling	
YES
Outputs 
collection	
UNet-SEM-sim-eval51-infer-outputDir

Step 2: Parameters
Job detail
Name:	UNet-SEM-sim-eval51-compare
Creation date:	Mar 3, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-eval51
Plugin:	wipp/wipp-dice-segmentationaccuracy:0.0.1
Inputs 
ground_truth	
SEM-sim-SNR-set6-mask-bin
prediction	
N/A
Outputs 
csvCollection	
UNet-SEM-sim-eval51-compare-output

The output is two CSV files available at
https://wipp-dev.nist.gov/csv-collections/67c627d74bec7525e69f1162
The collection of two files is named: UNet-SEM-sim-SNR-eval51-compare-output
++++++++++++++++++++++
AI model #3

III.1 Train

Training workflow (UNet-SEM-sim-SNR-v7) is available at 
https://wipp-dev.nist.gov/workflows/detail/67fd1b2d4def6c2e49231ad3

Training Parameters:

Job detail
Name:	UNet-SEM-sim-SNR-v7-train
Creation date:	Apr 14, 2025
Status:	ERROR
Owner:	pnb
Workflow Name:	UNet-SEM-sim-SNR-v7
Plugin:	WIPP UNet CNN Training Plugin:1.0.0
Inputs 
imageDir	
SEM-sim-SNR-set1-5
maskDir	
SEM-sim-SNR-set1-5-mask-bin
useTiling	
NO
tileSize	
256
trainFraction	
0.75
batchSize	
8
numberClasses	
2
learningRate	
1e-4
testEveryNSteps	
5
balanceClasses	
YES
earlyStoppingEpochCount	
10
useIntensityScaling	
YES
useAugmentation	
YES
augmentationReflection	
YES
augmentationRotation	
YES
augmentationJitter	
0
augmentationScale	
0
augmentationNoise	
0
augmentationBlurMaxSigma	
0
augmentationIntensity	
0
Outputs 
tensorflowModel	
UNet-SEM-sim-SNR-v7-train-outputDir


The trained AI Model is available at https://wipp-dev.nist.gov/ai-models/67bd584c127d825c2e613927
 

III.2 Evaluate the accuracy  

workflow name: UNet-SEM-sim-eval71
https://wipp-dev.nist.gov/workflows/detail/67fd31e64def6c2e49231ad6

The accuracy evaluation of the AI model on set 6 is accomplished using a WIPP workflow consisting of two steps:
step 1: inference on set 6 
step 2: comparison of predicted segmentation mask with the ground truth masks

Step 1: Parameters

Job detail
Name:	UNet-SEM-sim-eval71-infer
Creation date:	Apr 14, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-eval71
Plugin:	WIPP UNet CNN Inference Plugin:1.0.0
Inputs 
imageDir	
SEM-sim-SNR-set6
model	
67fd20214def6c2e49231ad5
useIntensityScaling	
YES
Outputs 
collection	
UNet-SEM-sim-eval71-infer-outputDir

Job detail
Name:	UNet-SEM-sim-eval71-compare
Creation date:	Apr 14, 2025
Status:	SUCCEEDED
Owner:	pnb
Workflow Name:	UNet-SEM-sim-eval71
Plugin:	wipp/wipp-dice-segmentationaccuracy:0.0.1
Inputs 
ground_truth	
SEM-sim-SNR-set6-mask-bin
prediction	
N/A
Outputs 
csvCollection	
UNet-SEM-sim-eval71-compare-output

The output is two CSV files available at
https://wipp-dev.nist.gov/csv-collections/67fd329c4def6c2e49231d11
The collection of two files is named: UNet-SEM-sim-SNR-eval71-compare-output

+++++++++++++++++++++++++++

