# Module 1: OCR and labeling

## About the Module

### Objective: 
Develop and run a labeling pipeline with Optical Character Recognition (OCR) using Tesseract and PAWLs within a Docker container to extract text from PDF files and label it. The results should be similar to what you will use throughout the whole course.

### Task:
1. **Optical Character Recognition step:**  
   Write code to build a Docker container with the Tesseract tool inside and perform OCR on a set of PDF documents.
2. **Labeling with PAWLs:**  
   Fetch the PAWLs container from the repository, build it, and label the set of documents.
3. **Conversion to DocBank format:**  
   Convert the results of the labeling into a format compatible with the DocBank dataset.

#### Prerequisites
- Docker
- Docker Compose

---

## Tasks Description

> **Note on File Locations!:**
> After running the step (`--mode pawls`) and annotating in PAWLs, the key files for each paper (identified by its `<paper_id>`) are stored within the PAWLs directory structure as follows:
> *   **Original PDF:** `pawls/skiff_files/apps/pawls/papers/<paper_id>/<paper_id>.pdf`
> *   **Extracted Structure:** `pawls/skiff_files/apps/pawls/papers/<paper_id>/pdf_structure.json`
> *   **Annotations:** `pawls/skiff_files/apps/pawls/papers/<paper_id>/[user_name]_annotations.json` (e.g., `development_user@example.com_annotations.json`)

The situation where you receive already preprocessed texts for your NLP task is quite rare. Documents are usually acquired in the form of unstructured documents (images, PDFs, excel sheets). One of the first steps in language processing is to extract text from these documents. For this task, we will use open-source Google Tesseract, although it is beneficial to get acquainted with some [proprietary alternatives](https://research.aimultiple.com/ocr-accuracy/).  
You can find instructions on how to set up Tesseract in the [installation documentation](https://tesseract-ocr.github.io/tessdoc/Installation.html). In this task, you do not need to install it locally. We will build a Docker container with Tesseract inside.


### Build OCR container and process documents

The code for container build is mostly ready. Container need to have `tesseract-ocr` installed. 
Add the installation command to the Dockerfile \
Hints:
* Dockerfile is located here: [**Module_1_Intro/Dockerfile**](Dockerfile)

The container may be ran in two modes, 'text' and 'pawls' extraction. After launching the app with pawls argument it will convert the output to the format which is accepted by PAWLs. For 'text' mode you need to write code to extract plain text using pytesseract.  
Hints:
* Python OCR app is located here: [**Module_1_Intro/src/app.py**](src/app.py)
* add missing code to `process_file_plain_text` function

After completing these actions you should be able to run the following

1. **Building the Docker Image:**

   Navigate to the directory where the `Dockerfile` is located and run the following command:

   ```bash
   docker-compose build
   ```

   This command builds the Docker container with the name `ocr-app`. 

2. **Running the Docker Container:**

   Place your PDF files in the `uploads` directory.  

   After building the image you can run the container.
   Run the following command to check the function you've implemented.  
   It will put the results of processing with Tesseract into .txt files.
   ```bash
   docker-compose run ocr-app python app.py --mode text
   ```
   To validate your code, you can run tests here: **[Module_1_Intro/test/test_text.py](Module_1_Intro/test/test_text.py)**
   
   ```bash
   pytest test/test_text.py
   ```

   To preprocess data for further usage run container with the following command:

   ```bash
   docker-compose run ocr-app python app.py --mode pawls
   ```

   This command starts the script inside the Docker container to preprocess PDFs into the PAWLS format.  
   It might take quite some time for large documents, allow up to 5-10 minutes per document


### Configure PAWLS
The application utilizes two primary directories defined in the Dockerfile:
- `uploads`: This directory is for uploading PDF files.
- `results`: This directory is for saving the output.

### PAWLS and document labeling
[PAWLS](https://github.com/allenai/pawls) is widely used for PDF labeling.  
The OCR results from Tesseract extraction are already processed and located in the `/results/skiff_files/` folder.

**Set up and run PAWLS**

1. **Clone the repository:**

   Run `git clone` in the Module folder

   ```bash
   git clone https://github.com/allenai/pawls.git
   ```

2. **Copy preprocessed PDFs and config:**
   
   Move prepared documents from the Module folder to the pawls directory.
   ```bash
   cp -r ./results/skiff_files/* ./pawls/skiff_files/
   ```
   Configuration in PAWLS is controlled by a JSON file located in the api/config directory.

3. **Running Pawls:**

    (If you launch PAWLS on Windows, you need to patch the EOL format with this [additional step](https://github.com/allenai/pawls#windows-eol-format-crlf-vs-linux-lf:~:text=Windows%20EOL%20format,in%20same%20directory).)  

   ```bash
   cd pawls
   docker-compose up --build
   ```
4. **Open PAWLS in your browser**

   Check your terminal output for a message like `Your application is starting and will be available at http://localhost:8080 when it's ready.` Once the app has started, open this address in your browser.
  
   You should be able to see something like this:
   ![Screenshot](readme_resources/Screenshot%202024-02-04%20at%2016.39.45.png)

**Configure Labels**
Your task is to define the set of required labels in the configuration file:

* **Title**
* **Author** 
* **Abstract** 
* **Section**
* **Paragraph**

Hints:
* configuration file for pawls is located here: [**Module_1_Intro/results/api/config/configuration.json**](Module_1_Intro/results/api/config/configuration.json)
* check an [example here](https://github.com/allenai/pawls/blob/main/api/config/configuration.json)

After creating a file you can move it to pawls folder using bash command
```bash
cp -r ./results/api/config/* pawls/api/config/
```
To update config exit pawls and launch it again using docker-compose


### Annotation of 5 documents:

* Check out this [video on the basics of PAWLS UI](https://youtu.be/TB4kzh2H9og?si=IYTqGD8qpesKeyaI).
* Annotate 5 documents from the provided subset with the labels mentioned above.
* You will find the results of the annotation under `Module_1_Intro/pawls/skiff_files/apps/pawls/papers`.
* For each document, the result will contain 2 files: 
    * `pdf_structure.json` -- text extracted and split by Tesseract.
    * `[user_name]_annotations.json` -- your annotations.


### Convert annotations

As you can see, the output format is different from what is used in DocBank. Write a Python script that converts the output of your labeling into the target format and save it to `Module_1_Intro/results/labeled`, each annotation to a separate .json file (*skip font and RGB for this task*):

```
[
    {
        "text": "Token",
        "x0": 117,
        "y0": 83,
        "x1": 176,
        "y1": 95,
        "r": 0,
        "g": 0,
        "b": 0,
        "font_name": "MCYIPK+NimbusRomNo9L-Regu",
        "label": "some label",
        "box": [
            117,
            83,
            176,
            95
        ]
    },
    ...
]
```

To validate that postprocessing is done , you can run tests here: **[Module_1_Intro/test/test_labeling.py](Module_1_Intro/test/test_labeling.py)**

---
## Definition of Done

This section describes the criteria for a completed task:
- The app container is building and running.
- Both `text` and `pawls` modes are functional.
- PAWLS labeling configuration is created.
- 5 examples are annotated.
- The conversion script is implemented.

---

## Recommended Materials

### Environment
Usage of [Docker Desktop](https://www.docker.com/products/docker-desktop/) is generally prohibited at EPAM for licensing reasons.

In case you run things locally, please check out the following alternatives

**MacOS:**
* [Colima](https://smallsharpsoftwaretools.com/tutorials/use-colima-to-run-docker-containers-on-macos/)

**Windows (WSL):**

On Windows, using WSL (Windows Subsystem for Linux) is the recommended approach for general work, as it will save you a lot of time in resolving Windows-related issues.

WSL
* [Guide on setting up WSL](https://learn.microsoft.com/en-us/windows/wsl/install) -- make sure to install and set WSL 2
* [Use WSL terminal in VS Code](https://code.visualstudio.com/docs/remote/wsl) -- recommended way
* [Use WSL terminal in PyCharm](https://www.jetbrains.com/help/pycharm/using-wsl-as-a-remote-interpreter.html) -- should work for PyCharm Professional

Docker & Compose

* [Guide on installing docker](https://dev.to/bowmanjd/install-docker-on-windows-wsl-without-docker-desktop-34m9)
* [Another guide, includes docker-compose](https://gist.github.com/martinsam16/4492957e3bbea34046f2c8b49c3e5ac0)
* [Rancher desktop](https://rancherdesktop.io)



**Linux:**

* [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)
* [Docker Compose](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)

### Docker and docker compose

* [Docker 101](https://docker-curriculum.com)
* [Docker Compose 101](https://github.com/dockersamples/101-tutorial/blob/master/docs_en/tutorial/using-docker-compose/index.md)

### OCR tools

While there are plenty of tools available for OCR, these are the top choices depending on whether you have a budget for cloud services or prefer to go with open-source options.

* [Tesseract](https://github.com/tesseract-ocr/tesseract) -- open source, used in this task
* [AWS Textract](https://aws.amazon.com/textract/) -- cloud, proprietary, usually better quality than tesseract
* [Azure AI Document Intelligence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence#features) -- cloud, proprietary, not just OCR, but more document structure understanding
* [Overview of different OCR engines](https://research.aimultiple.com/ocr-accuracy/) 

### Labeling tools & crowdsourcing

You don't need to delve too deeply here, but it's important to be aware of these tools and services.  
The exact choice between them depends on the specific ML task at hand, your budget, access to resources, and the cloud/infrastructure you use. The general intuition is:
* Open-source solutions are (mostly) free to use, highly customizable, but require your own infrastructure and support. 
* Cloud-based solutions might be more expensive, but they require less support and are a good choice for standard tasks, especially if you're already using SageMaker or Azure ML.


Labeling tools
* [Pawls](https://github.com/allenai/pawls) -- the one you've tried in this module, open source
* [Amazon Groundtruth](https://aws.amazon.com/sagemaker/groundtruth/) -- cloud based, proprietary
* [Azure ML Studio labeling](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-label-data?view=azureml-api-2)  -- cloud based, proprietary
* [Label Studio](https://labelstud.io) -- open source commercially usable with lack of some features 
* [Label Studio Enterprise](https://humansignal.com/platform/) -- cloud based version, proprietary
* [Appen](https://appen.com/solutions/smart-labeling/) -- cloud based, proprietary, crowd sourcing platform and annotation tooling
* [Prodigy](https://prodi.gy) -- proprietary, good integration with SpaCy

Crowdsourcing platforms
* [Amazon Mechanical Turk](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/GetStartedMturk.html)
* [Toloka](https://toloka.ai)
* [Scale AI](https://scale.com)


### Annotation process and evaluation

In case you're running an annotation project, you might need to:

1. Prepare a raw or pre-annotated set of documents for annotation in a specific format, suited for the tool in use.
2. Write detailed instructions for the annotation team.
3. Provide examples of complete annotations, with edge-cases explained and defects identified (documents/examples that cannot or should not be annotated). As a result, this will be a rather lengthy document for annotators to read and understand.
4. If possible, conduct a kickoff call with the annotation team.
5. If possible, have regular check-ins and communication with them to address new questions.
6. If possible, run a training phase for them, to measure annotation speed, check the tooling, and ensure understanding of the task.
7. Control annotation quality -- this might be done via inter-annotator agreement metrics.

Here are links on the topic:

* [Measuring quality of annotation with classical metrics](https://medium.com/toloka/guide-evaluating-the-quality-of-crowd-annotated-data-8484c361cad7)
* [Annotation agreement for different types of data](https://docs.humansignal.com/guide/stats)
* [Cohen's Kappa](https://surge-ai.medium.com/inter-annotator-agreement-an-introduction-to-cohens-kappa-statistic-dcc15ffa5ac4)

Examples of datasets

* [Instruct gpt annotation process](https://openai.com/research/instruction-following), see the paper for more
* [SQuaD 1.0](https://arxiv.org/abs/1606.05250), [SQuAD 2.0](https://arxiv.org/pdf/1806.03822.pdf) -- see the papers describing datasets collection 
* [DocBank](https://arxiv.org/pdf/2006.01038.pdf) -- checkout section 3 on how DocBank was processed and annotated
